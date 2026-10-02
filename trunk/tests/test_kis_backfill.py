"""KIS overseas backfill: join rules (fee allocation, synthetic, unsettled, qty mismatch, ISIN rename),
2-page continuation, incremental window, idempotency — against a MockTransport."""

import json
import os
import sqlite3
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import httpx

SCRATCH = Path(__file__).parent
WORK = SCRATCH / "kis_bf_test"
WORK.mkdir(exist_ok=True)
for f in WORK.glob("*"):
    if f.is_file():
        f.unlink()
os.environ["KIS_APP_KEY"] = "PSkey000000000000000000000000000000"
os.environ["KIS_APP_SECRET"] = "secret"
os.environ["KIS_ACCOUNT"] = "12345678-01"
(WORK / "config.toml").write_text(f"""[kis]
base_url = "https://kis.mock"
token_cache = "{WORK / 'token.json'}"
db = "{WORK / 'kis.sqlite'}"
""")

from brokers.common import ledger
from brokers.kis import backfill as bf, config, fills as fm, rights as rm
from brokers.kis.store import KisStore

config.load(WORK / "config.toml")

# --- pure join rules ---------------------------------------------------------

def order(odno, ord_dt, pdno, side, qty, price, *, kst_dt=None, tmd="233000"):
    return {"odno": odno, "ord_dt": ord_dt, "dmst_ord_dt": kst_dt or ord_dt, "thco_ord_tmd": tmd, "pdno": pdno,
            "excg": "NASD", "side": side, "ccld_qty": qty, "ccld_unpr": price, "ccld_amt": "0", "crcy": "USD"}

def tran(trad_dt, pdno, side, qty, price, amt, dfee, ffee, isin=None, amt_unit=None):
    return {"trad_dt": trad_dt, "pdno": pdno, "side": side, "seq": 0, "ccld_qty": qty, "amt_unit_qty": amt_unit or f"{qty}.00000000",
            "unpr": price, "frcr_amt": amt, "dmst_fee": dfee, "frcr_fee": ffee, "crcy": "USD", "std_pdno": isin}

# two buys of UNH the same day: 10@261.70 (2617.0) + 20@261.40 (5228.0); one trans row with fee 7.05 / 0
orders = [
    order("o1", "20250731", "UNH", "BUY", "10", "261.70000000", tmd="195814"),
    order("o2", "20250731", "UNH", "BUY", "20", "261.40000000", tmd="195839"),
    # after-midnight KST sell: ord_dt is the US date, dmst_ord_dt the KST date
    order("o3", "20260911", "PGY", "SELL", "10", "20.52000000", kst_dt="20260912", tmd="005058"),
    # order with no transaction row yet
    order("o4", "20260919", "NVDA", "BUY", "1", "100", tmd="230000"),
    # qty mismatch: orders say 5, trans says 4
    order("o5", "20260101", "AMD", "BUY", "5", "100", tmd="230000"),
    # ticker rename: bought as FI, later traded as FISV under the same ISIN
    order("o6", "20251030", "FI", "BUY", "10", "71", tmd="230000"),
    order("o7", "20251208", "FISV", "BUY", "20", "66.26", tmd="230000"),
    order("o8", "20260210", "FISV", "SELL", "30", "57.14", tmd="230000"),
]
trans = [
    tran("20250731", "UNH", "BUY", "30", "261.5", "7845.0", "7.05000", "0.000000", "US91324P1021"),
    tran("20260911", "PGY", "SELL", "10", "20.52", "205.2", "0.18000", "0.010000", "IL0011858912"),
    tran("20260101", "AMD", "BUY", "4", "100", "400", "0.40000", "0", "US0079031078"),
    tran("20251030", "FI", "BUY", "10", "71", "710", "0.64", "0", "US3377381088"),
    tran("20251208", "FISV", "BUY", "20", "66.26", "1325.2", "1.19", "0", "US3377381088"),
    tran("20260210", "FISV", "SELL", "30", "57.14", "1714.2", "1.54", "0.02", "US3377381088"),
    # fractional trade with no order at all
    tran("20260305", "VOO", "BUY", "0", "500", "250.0", "0.23", "0", "US9229083632", amt_unit="0.50000000"),
]
rows = fm.join_overseas(orders, trans)
by_id = {r.fill_id: r for r in rows}
# proportional allocation with the remainder on the last order: 7.05 * 2617/7845 = 2.3518 -> o1, rest 4.6982 -> o2
assert by_id["o1"].commission == Decimal("2.3518") and by_id["o2"].commission == Decimal("4.6982"), (by_id["o1"], by_id["o2"])
assert by_id["o1"].commission + by_id["o2"].commission == Decimal("7.05")
assert by_id["o1"].filled_at == "2025-07-31T19:58:14+09:00" and by_id["o1"].trading_date == date(2025, 7, 31)
assert by_id["o3"].filled_at == "2026-09-12T00:50:58+09:00" and by_id["o3"].trading_date == date(2026, 9, 11)
assert by_id["o3"].commission == Decimal("0.18") and by_id["o3"].tax == Decimal("0.01")
assert by_id["o4"].flags == ("unsettled",) and by_id["o4"].commission == 0
assert by_id["o5"].flags == ("qty_mismatch",) and by_id["o5"].quantity == 5 and by_id["o5"].commission == Decimal("0.4")
assert by_id["o6"].symbol == "FISV" and by_id["o6"].flags == ("renamed",) and by_id["o6"].isin == "US3377381088"
assert by_id["o7"].symbol == "FISV" and by_id["o7"].flags == ()
syn = by_id["trans:20260305:VOO:BUY"]
assert syn.flags == ("synthetic",) and syn.quantity == Decimal("0.5") and syn.price == Decimal("500") and syn.commission == Decimal("0.23")
assert syn.filled_at == "2026-03-06T06:00:00+09:00", syn.filled_at  # 16:00 EST on 2026-03-05 = 21:00Z = 06:00 KST next day
assert [r.fill_id for r in rows] == [r.fill_id for r in sorted(rows, key=lambda r: (r.filled_at, r.fill_id))] and rows[0].fill_id == "o1"

# same odno on two KST days that share one US session (evening + after midnight): both fills survive, ids suffixed
same = fm.join_overseas(
    [order("0030000001", "20260310", "NVDA", "BUY", "1", "100", kst_dt="20260310", tmd="233000"),
     order("0030000001", "20260310", "NVDA", "BUY", "2", "101", kst_dt="20260311", tmd="003000")],
    [tran("20260310", "NVDA", "BUY", "3", "100.67", "302", "0.27", "0", "US67066G1040")],
)
assert sorted(r.fill_id for r in same) == ["0030000001@2026-03-10", "0030000001@2026-03-11"], [r.fill_id for r in same]
assert sum(r.commission for r in same) == Decimal("0.27")

# --- pure domestic join rules ------------------------------------------------

def dorder(odno, ord_dt, pdno, side, qty, price, tmd="093000"):
    return {"odno": odno, "ord_dt": ord_dt, "ord_tmd": tmd, "pdno": pdno, "side": side, "ccld_qty": qty, "avg_prvs": price,
            "ccld_amt": "0", "excg_id": "KRX"}

def dpl(trad_dt, pdno, buy_qty, buy_amt, sll_qty, sll_amt, fee, tax):
    return {"trad_dt": trad_dt, "pdno": pdno, "seq": 0, "buy_qty": buy_qty, "buy_amt": buy_amt, "sll_qty": sll_qty,
            "sll_amt": sll_amt, "fee": fee, "tl_tax": tax}

# one day, one symbol: buy 10@1000 (10000), buy 30@1100 (33000), sell 20@1200 (24000); fee 67 over all three by amount,
# tax 48 on the single sell
drows = fm.join_domestic(
    [dorder("d1", "20260102", "005930", "BUY", "10", "1000", "090000"), dorder("d2", "20260102", "005930", "BUY", "30", "1100", "100000"),
     dorder("d3", "20260102", "005930", "SELL", "20", "1200", "140000"),
     dorder("d4", "20260105", "440110", "BUY", "5", "50000"),                      # no P&L row yet
     dorder("d5", "20260107", "000660", "SELL", "3", "200000"), dorder("d6", "20260107", "000660", "SELL", "1", "201000")],
    [dpl("20260102", "005930", "40", "43000", "20", "24000", "67", "48"),
     dpl("20260107", "00000A000660", "0", "0", "4", "801000", "40", "120"),        # 12-char code, two sells: tax by amount
     dpl("20260108", "252670", "100", "50000", "0", "0", "3", "0")],                # no order: synthetic buy
)
d = {r.fill_id: r for r in drows}
assert d["d1"].commission == 10 and d["d2"].commission == 33 and d["d3"].commission == 24, [d[k].commission for k in ("d1", "d2", "d3")]
assert d["d1"].tax == 0 and d["d2"].tax == 0 and d["d3"].tax == 48
assert d["d1"].filled_at == "2026-01-02T09:00:00+09:00" and d["d1"].trading_date == date(2026, 1, 2) and d["d1"].currency == "KRW"
assert d["d4"].flags == ("unsettled",) and d["d4"].commission == 0
assert d["d5"].symbol == "000660" and d["d5"].tax + d["d6"].tax == 120 and d["d5"].tax == 90 and d["d5"].commission + d["d6"].commission == 40
syn = d["pl:20260108:252670:BUY"]
assert syn.quantity == 100 and syn.price == 500 and syn.commission == 3 and syn.flags == ("synthetic",) and syn.filled_at == "2026-01-08T15:30:00+09:00"
assert all("." not in format(r.commission, "f") and "." not in format(r.tax, "f") for r in drows), "KRW fees are whole won"
# odno repeated on another day gets a date suffix
dup = fm.join_domestic([dorder("x", "20260102", "005930", "BUY", "1", "1000"), dorder("x", "20260103", "005930", "BUY", "1", "1000")], [])
assert sorted(r.fill_id for r in dup) == ["x@2026-01-02", "x@2026-01-03"]
assert fm.join_domestic([dorder("x", "20260102", "005930", "BUY", "1", "1000")], [])[0].fill_id == "x"

# --- pure rights rules -------------------------------------------------------

def right(bass_dt, pdno, type_cd, *, amt="0", tax="0", pay=None, qty="100", alct="0", tot="0", cblc_type="01"):
    return {"bass_dt": bass_dt, "pdno": pdno, "rght_type_cd": type_cd, "cblc_type_cd": cblc_type, "name": pdno,
            "cblc_qty": qty, "last_alct_qty": alct, "tot_alct_qty": tot, "alct_amt": amt, "tax_amt": tax,
            "cash_dfrm_dt": pay}

rrows = [
    right("20250815", "024720", "03", amt="10000", tax="0", pay="20250829", qty="200"),      # paid, KIS reports no tax
    right("20260831", "005380", "03", amt="15000", tax="2310", pay="20260930", qty="6"),     # pending (future payment)
    right("20260327", "024720", "03", amt="44000", tax="0", pay="20260423", qty="200"),
    right("20260101", "000660", "03", amt="1000", tax="154", pay="20260201", qty="4"),       # tax reported: kept as-is
    right("20260105", "005930", "03", amt="0", pay="20260201", qty="10", alct="1"),          # stock dividend: not cash
    right("20260110", "035420", "14", qty="10", alct="10", tot="20"),                         # 액면분할
    right("20260115", "122630", "02", qty="10", alct="1", tot="11"),                          # 무상증자
    right("20260120", "252670", "99"),                                                        # 기타: ignored everywhere
]
paid, pending = rm.dividends(rrows, today=date(2026, 9, 21))
assert [d.symbol for d in paid] == ["024720", "000660", "024720"], [d.symbol for d in paid]
assert [d.paid_on for d in paid] == [date(2025, 8, 29), date(2026, 2, 1), date(2026, 4, 23)]
assert paid[0].amount == 10000 and paid[0].tax == 1540 and paid[0].estimated_tax and paid[0].per_share == 50
assert paid[0].net == 8460 and paid[0].quantity == 200 and paid[0].currency == "KRW"
assert paid[1].tax == 154 and not paid[1].estimated_tax  # the API's own figure is kept
assert paid[2].per_share == 220 and paid[2].tax == 6776
assert paid[0].id == "kis:2025-08-29:024720" and paid[0].record_date == date(2025, 8, 15)
assert [r["pdno"] for r in pending] == ["005380"], pending
gross_paid, _ = rm.dividends(rrows, today=date(2026, 9, 21), gross=True)
assert [d.tax for d in gross_paid] == [0, 154, 0] and not any(d.estimated_tax for d in gross_paid)
# a dividend whose payment date has arrived is picked up
paid_later, pending_later = rm.dividends(rrows, today=date(2026, 9, 30))
assert len(paid_later) == 4 and pending_later == []
changes = rm.share_changes(rrows)
assert [(c.symbol, c.type_name) for c in changes] == [("035420", "액면분할"), ("122630", "무상증자")]
assert changes[0].holding == 10 and changes[0].total_allocated == 20

# --- store + backfill against a mock API -------------------------------------

def kis_order(odno, ord_dt, pdno, side_cd, qty, price, kst_dt=None, tmd="233000"):
    return {"ord_dt": ord_dt, "ord_gno_brno": "01790", "odno": odno, "orgn_odno": "", "sll_buy_dvsn_cd": side_cd,
            "sll_buy_dvsn_cd_name": "", "rvse_cncl_dvsn": "00", "rvse_cncl_dvsn_name": "", "pdno": pdno, "prdt_name": pdno,
            "ft_ord_qty": qty, "ft_ord_unpr3": price, "ft_ccld_qty": qty, "ft_ccld_unpr3": price, "ft_ccld_amt3": "0",
            "nccs_qty": "0", "prcs_stat_name": "완료", "rjct_rson": "", "rjct_rson_name": "", "ord_tmd": tmd,
            "tr_mket_name": "나스닥", "tr_crcy_cd": "USD", "tr_natn": "840", "ovrs_excg_cd": "NASD", "tr_natn_name": "미국",
            "dmst_ord_dt": kst_dt or ord_dt, "thco_ord_tmd": tmd, "loan_type_cd": "10", "loan_dt": "", "mdia_dvsn_name": "모바일"}

def kis_tran(trad_dt, pdno, side_cd, qty, price, amt, dfee, ffee, isin):
    return {"trad_dt": trad_dt, "sttl_dt": trad_dt, "sll_buy_dvsn_cd": side_cd, "sll_buy_dvsn_name": "", "pdno": pdno,
            "ovrs_item_name": pdno, "ccld_qty": qty, "amt_unit_ccld_qty": f"{qty}.00000000", "ft_ccld_unpr2": price,
            "ovrs_stck_ccld_unpr": "0", "tr_frcr_amt2": amt, "tr_amt": "0", "frcr_excc_amt_1": amt, "wcrc_excc_amt": "0",
            "dmst_frcr_fee1": dfee, "frcr_fee1": ffee, "dmst_wcrc_fee": "0", "ovrs_wcrc_fee": "0", "crcy_cd": "USD",
            "std_pdno": isin, "erlm_exrt": "1400", "loan_dvsn_cd": "01", "loan_dvsn_name": "현금"}

api = {
    "orders": [kis_order("A1", "20250709", "VOO", "02", "10", "572.15000000"),
               kis_order("A9", "20260310", "NVDA", "02", "1", "100", kst_dt="20260310", tmd="233000"),
               kis_order("A9", "20260310", "NVDA", "02", "2", "101", kst_dt="20260311", tmd="003000"),
               kis_order("A2", "20250731", "UNH", "02", "10", "261.70000000", tmd="195814"),
               kis_order("A3", "20250731", "UNH", "02", "20", "261.40000000", tmd="195839"),
               kis_order("A4", "20260911", "PGY", "01", "10", "20.52000000", kst_dt="20260912", tmd="005058")],
    "trans": [kis_tran("20250709", "VOO", "02", "10", "572.15", "5721.5", "5.14000", "0", "US9229083632"),
              kis_tran("20260310", "NVDA", "02", "3", "100.67", "302", "0.27", "0", "US67066G1040"),
              kis_tran("20250731", "UNH", "02", "30", "261.5", "7845.0", "7.05000", "0", "US91324P1021")],
    # the PGY transaction only appears on the second run (registered after settlement)
}
api["dorders"] = [
    {"ord_dt": "20250709", "odno": "0008251000", "orgn_odno": "", "sll_buy_dvsn_cd": "02", "pdno": "024720", "prdt_name": "콜마홀딩스",
     "ord_qty": "200", "ord_unpr": "16030", "ord_tmd": "092846", "tot_ccld_qty": "200", "avg_prvs": "16030", "tot_ccld_amt": "3206000",
     "excg_id_dvsn_cd": "SOR"},
    {"ord_dt": "20260623", "odno": "0004958400", "orgn_odno": "", "sll_buy_dvsn_cd": "02", "pdno": "440110", "prdt_name": "파두",
     "ord_qty": "20", "ord_unpr": "111100", "ord_tmd": "090637", "tot_ccld_qty": "20", "avg_prvs": "111100", "tot_ccld_amt": "2222000",
     "excg_id_dvsn_cd": "KRX"},
    {"ord_dt": "20260623", "odno": "0004958401", "orgn_odno": "0004958400", "sll_buy_dvsn_cd": "02", "pdno": "440110", "prdt_name": "파두",
     "ord_qty": "5", "ord_unpr": "0", "ord_tmd": "090700", "tot_ccld_qty": "0", "avg_prvs": "0", "tot_ccld_amt": "0",
     "excg_id_dvsn_cd": "KRX"},   # cancel row: no fill, must be dropped
]
api["dpl"] = [
    {"trad_dt": "20250709", "pdno": "024720", "prdt_name": "콜마홀딩스", "trad_dvsn_name": "현금", "buy_qty": "200", "buy_amt": "3206000",
     "sll_qty": "0", "sll_amt": "0", "fee": "116", "tl_tax": "0"},
    {"trad_dt": "20260623", "pdno": "440110", "prdt_name": "파두", "trad_dvsn_name": "현금", "buy_qty": "20", "buy_amt": "2222000",
     "sll_qty": "0", "sll_amt": "0", "fee": "81", "tl_tax": "0"},
]
api["rights"] = [
    {"bass_dt": "20250815", "shtn_pdno": "024720", "pdno": "00000A024720", "prdt_name": "콜마홀딩스", "rght_type_cd": "03",
     "rght_cblc_type_cd": "01", "cblc_qty": "200", "last_alct_qty": "0", "tot_alct_qty": "0", "last_alct_amt": "10000",
     "tax_amt": "0", "cash_dfrm_dt": "20250829"},
    {"bass_dt": "20260831", "shtn_pdno": "005380", "pdno": "00000A005380", "prdt_name": "현대차", "rght_type_cd": "03",
     "rght_cblc_type_cd": "01", "cblc_qty": "6", "last_alct_qty": "0", "tot_alct_qty": "0", "last_alct_amt": "15000",
     "tax_amt": "2310", "cash_dfrm_dt": "20260930"},
]
api["info"] = {"024720": {"prdt_name": "콜마홀딩스보통주", "mket_id_cd": "STK", "std_pdno": "KR7024720005"},
               "440110": {"prdt_name": "파두", "mket_id_cd": "KSQ", "std_pdno": "KR7440110005"},
               "005380": {"prdt_name": "현대자동차보통주", "mket_id_cd": "STK", "std_pdno": "KR7005380001"}}
calls = []


def in_range(d, params, a, b):
    return params[a] <= d <= params[b]


def handler(req: httpx.Request) -> httpx.Response:
    if req.url.path == "/oauth2/tokenP":
        return httpx.Response(200, json={"access_token": "tok", "token_type": "Bearer", "expires_in": 86400,
                                         "access_token_token_expired": "2030-01-01 09:00:00"})
    h, p = req.headers, dict(req.url.params)
    calls.append((h["tr_id"], p.get("ORD_STRT_DT") or p.get("ERLM_STRT_DT") or p.get("INQR_STRT_DT"),
                  p.get("ORD_END_DT") or p.get("ERLM_END_DT") or p.get("INQR_END_DT"), h.get("tr_cont", "")))
    if h["tr_id"] == "TTTS3035R":
        assert p["CCLD_NCCS_DVSN"] == "01" and p["SORT_SQN"] == "DS" and p["PDNO"] == "%"
        rows = [o for o in api["orders"] if in_range(o["ord_dt"], p, "ORD_STRT_DT", "ORD_END_DT")]
        # two pages of 2 (real limit is 20)
        if p["CTX_AREA_NK200"] == "":
            more = len(rows) > 2
            return httpx.Response(200, headers={"tr_cont": "M" if more else "D"}, json={
                "rt_cd": "0", "msg_cd": "", "msg1": "", "ctx_area_fk200": "fk", "ctx_area_nk200": "page2" if more else "",
                "output": rows[:2]})
        assert h["tr_cont"] == "N" and p["CTX_AREA_NK200"] == "page2"
        return httpx.Response(200, headers={"tr_cont": "D"}, json={"rt_cd": "0", "msg_cd": "", "msg1": "",
                                                                    "ctx_area_fk200": "", "ctx_area_nk200": "", "output": rows[2:]})
    if h["tr_id"] in ("TTTC0081R", "CTSC9215R"):
        assert p["CCLD_DVSN"] == "01" and p["INQR_DVSN"] == "01" and p["EXCG_ID_DVSN_CD"] == "ALL"
        if h["tr_id"] == "CTSC9215R":
            from datetime import datetime as _dt
            span = (_dt.strptime(p["INQR_END_DT"], "%Y%m%d") - _dt.strptime(p["INQR_STRT_DT"], "%Y%m%d")).days
            if span > 365:
                return httpx.Response(200, json={"rt_cd": "1", "msg_cd": "APBK1633", "msg1": "조회기간은 1년 이내이어야 합니다."})
        rows = [o for o in api["dorders"] if in_range(o["ord_dt"], p, "INQR_STRT_DT", "INQR_END_DT")]
        return httpx.Response(200, headers={"tr_cont": "D"}, json={"rt_cd": "0", "msg_cd": "", "msg1": "", "ctx_area_fk100": "",
                                                                    "ctx_area_nk100": "", "output1": rows, "output2": {}})
    if h["tr_id"] == "TTTC8715R":
        rows = [r for r in api["dpl"] if in_range(r["trad_dt"], p, "INQR_STRT_DT", "INQR_END_DT")]
        return httpx.Response(200, headers={"tr_cont": "D"}, json={"rt_cd": "0", "msg_cd": "", "msg1": "", "ctx_area_fk100": "",
                                                                    "ctx_area_nk100": "", "output1": rows, "output2": {}})
    if h["tr_id"] == "CTRGA011R":
        assert p["INQR_DVSN"] == "03" and p["RGHT_TYPE_CD"] == ""
        rows = [r for r in api["rights"] if in_range(r["bass_dt"], p, "INQR_STRT_DT", "INQR_END_DT")]
        return httpx.Response(200, headers={"tr_cont": "D"}, json={"rt_cd": "0", "msg_cd": "", "msg1": "",
                                                                    "ctx_area_fk100": "", "ctx_area_nk100": "", "output": rows})
    if h["tr_id"] == "CTPF1002R":
        return httpx.Response(200, json={"rt_cd": "0", "msg_cd": "", "msg1": "", "output": api["info"].get(p["PDNO"], {})})
    if h["tr_id"] == "CTOS4001R":
        rows = [t for t in api["trans"] if in_range(t["trad_dt"], p, "ERLM_STRT_DT", "ERLM_END_DT")]
        return httpx.Response(200, headers={"tr_cont": "D"}, json={"rt_cd": "0", "msg_cd": "", "msg1": "",
                                                                    "ctx_area_fk100": "", "ctx_area_nk100": "", "output1": rows,
                                                                    "output2": {}})
    return httpx.Response(404, text="nope")


mock = httpx.MockTransport(handler)
_orig = httpx.Client
httpx.Client = lambda **kw: _orig(transport=mock, **{k: v for k, v in kw.items() if k != "transport"})
import brokers.kis.client as cm
try:
    # first run: whole history, 2 pages of overseas orders; domestic split into the recent TR and yearly old-TR chunks
    assert bf.main(["--to", "2026-09-20"]) == 0
    assert calls[0][1:3] == ("20150101", "20260920") and [c[3] for c in calls if c[0] == "TTTS3035R"] == ["", "N"]
    today = date.today()
    recent = [c for c in calls if c[0] == "TTTC0081R"]
    old = [c for c in calls if c[0] == "CTSC9215R"]
    assert len(recent) == 1 and recent[0][1] == (today - timedelta(days=bf.RECENT_TR_DAYS)).strftime("%Y%m%d")
    assert old and old[0][2] == (today - timedelta(days=bf.RECENT_TR_DAYS - bf.OLD_TR_OVERLAP_DAYS)).strftime("%Y%m%d")
    assert old[-1][1] == "20150101" and all(int(c[2]) > int(c[1]) for c in old)
    pl_calls = [c for c in calls if c[0] == "TTTC8715R"]
    assert len(pl_calls) == 1 and (date(2026, 9, 20) - date.fromisoformat(f"{pl_calls[0][1][:4]}-{pl_calls[0][1][4:6]}-{pl_calls[0][1][6:]}")).days < 3650
    assert len([c for c in calls if c[0] == "CTRGA011R"]) == 1
    # one instrument lookup per new domestic symbol, including one only seen in the rights rows (005380)
    assert len([c for c in calls if c[0] == "CTPF1002R"]) == 3
    with KisStore(config.db_path()) as st:
        acct = st.accounts()[0]
        assert acct == "12345678-01"
        fills = st.fills(acct, currency="USD")
        assert [f.order_id for f in fills] == ["A1", "A2", "A3", "A9@2026-03-10", "A9@2026-03-11", "A4"], [f.order_id for f in fills]
        assert fills[5].trading_date == date(2026, 9, 11) and fills[5].filled_at == "2026-09-12T00:50:58+09:00"
        assert fills[5].commission == "0" and json.loads(st.flagged_fills(acct, "overseas")[0]["flags"]) == ["unsettled"]
        assert fills[1].commission == "2.3518" and fills[2].commission == "4.6982"
        assert st.last_fetch(acct, "overseas") == ("2015-01-01", "2026-09-20")
        # the fills feed the common ledger (trading_date stated, no session rule needed)
        adj = ledger.apply_splits(fills, [], session_date=lambda s: (_ for _ in ()).throw(AssertionError("must not be called")))
        assert ledger.net_positions(adj) == {"VOO": Decimal("10"), "UNH": Decimal("30"), "PGY": Decimal("-10"), "NVDA": Decimal("3")}
        krw = st.fills(acct, currency="KRW")
        assert [(f.order_id, f.symbol, f.quantity, f.commission) for f in krw] == [("0008251000", "024720", "200", "116"), ("0004958400", "440110", "20", "81")]
        assert krw[1].filled_at == "2026-06-23T09:06:37+09:00" and krw[1].trading_date == date(2026, 6, 23)
        assert st.instruments()["440110"]["yahoo_symbol"] == "440110.KQ" and st.instruments()["024720"]["yahoo_symbol"] == "024720.KS"
        assert st.instruments()["440110"]["isin"] == "KR7440110005"
        assert set(st.instruments()) == {"024720", "440110", "005380"}
        stored = st.rights(acct)
        assert [(r["bass_dt"], r["pdno"], r["rght_type_cd"]) for r in stored] == [("20250815", "024720", "03"), ("20260831", "005380", "03")]
        div, pend = rm.dividends(stored, today=date(2026, 9, 21))
        assert [(d.symbol, str(d.amount), str(d.tax), d.estimated_tax) for d in div] == [("024720", "10000", "1540", True)]
        assert len(pend) == 1

    # second run: incremental window (45 days before the last fetched end), the PGY transaction has arrived
    api["trans"].append(kis_tran("20260911", "PGY", "01", "10", "20.52", "205.2", "0.18000", "0.010000", "IL0011858912"))
    calls.clear()
    assert bf.main(["--to", "2026-09-22"]) == 0
    assert calls[0][1] == (date(2026, 9, 20) - timedelta(days=45)).strftime("%Y%m%d") and calls[0][2] == "20260922"
    assert not [c for c in calls if c[0] == "CTSC9215R"], "a 45-day window needs the recent TR only"
    assert not [c for c in calls if c[0] == "CTPF1002R"], "instruments are looked up once"
    with KisStore(config.db_path()) as st:
        fills = st.fills(acct, currency="USD")
        assert len(fills) == 6, "re-fetch must not duplicate"
        assert len(st.fills(acct, currency="KRW")) == 2
        assert fills[5].commission == "0.18" and fills[5].tax == "0.01" and st.flagged_fills(acct, "overseas") == []
        assert sqlite3.connect(config.db_path()).execute("select count(*) from overseas_trans").fetchone()[0] == 4

    # --restart fetches everything again and stays idempotent
    calls.clear()
    assert bf.main(["--restart", "--to", "2026-09-22"]) == 0
    assert calls[0][1] == "20150101"
    with KisStore(config.db_path()) as st:
        assert len(st.fills(acct)) == 8
    # explicit --from; bad range
    calls.clear()
    assert bf.main(["--from", "2026-09-01", "--to", "2026-09-22", "--market", "overseas"]) == 0 and calls[0][1] == "20260901"
    try:
        bf.main(["--from", "2026-09-30", "--to", "2026-09-22"]); raise AssertionError("bad range accepted")
    except SystemExit:
        pass
    assert bf.main(["--kis-account", "nope"]) == 2
finally:
    httpx.Client = _orig

print("kis backfill tests OK")
