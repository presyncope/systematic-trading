"""KIS exporters through the shared pipeline: per-currency files/accounts, Yahoo symbols for KRX,
holdings reconciliation (USD + KRW), --cash from CTRP6504R / TTTC8434R, export_log keys, --kis-account."""

import csv
import json
import os
from datetime import date
from decimal import Decimal
from pathlib import Path

import httpx

SCRATCH = Path(__file__).parent
WORK = SCRATCH / "kis_export_test"
WORK.mkdir(exist_ok=True)
for f in WORK.glob("*"):
    if f.is_file():
        f.unlink()
os.environ["KIS_APP_KEY"] = "PSkey000000000000000000000000000000"
os.environ["KIS_APP_SECRET"] = "secret"
os.environ["KIS_ACCOUNT"] = "12345678-01"
os.environ["GHOSTFOLIO_ACCESS_TOKEN"] = "gf-secret"
(WORK / "config.toml").write_text(f"""[kis]
base_url = "https://kis.mock"
token_cache = "{WORK / 'token.json'}"
db = "{WORK / 'kis.sqlite'}"
tradesviz_csv = "{WORK / 'tv.csv'}"
ghostfolio_json = "{WORK / 'gf.json'}"
adjustments = "{WORK / 'adjustments.toml'}"

[ghostfolio]
url = "https://gf.local"
""")

from brokers.common import pipeline
from brokers.kis import config, export_ghostfolio as gf, export_tradesviz as tv
from brokers.kis.broker import KIS, _currency_path
from brokers.kis.store import FillRow, KisStore

config.load(WORK / "config.toml")

assert _currency_path(Path("a/b.json"), "USD") == Path("a/b.json") and _currency_path(Path("a/b.json"), None) == Path("a/b.json")
assert _currency_path(Path("a/b.json"), "KRW") == Path("a/b_krw.json")
assert KIS.ghostfolio_account("USD") == "KIS" and KIS.ghostfolio_account("KRW") == "KIS KRW"
assert KIS.normalize_account("1234567801") == "12345678-01"
assert pipeline.target_key("ghostfolio", "USD") == "ghostfolio" and pipeline.target_key("ghostfolio", None) == "ghostfolio"
assert pipeline.target_key("ghostfolio", "KRW") == "ghostfolio:KRW"

# --- fills in the store: 2 USD (NVDA open 3, GOOGL round trip), 2 KRW (005930 open 10, 440110 open 5) ---
acct = "12345678-01"
with KisStore(config.db_path()) as st:
    st.replace_fills(acct, "overseas", [
        FillRow("o1", "overseas", "NVDA", "BUY", Decimal(3), Decimal("100"), "USD", "2026-03-10T23:30:00+09:00", date(2026, 3, 10), Decimal("0.27"), Decimal(0), "order"),
        FillRow("o2", "overseas", "GOOGL", "BUY", Decimal(1), Decimal("300"), "USD", "2026-03-11T23:30:00+09:00", date(2026, 3, 11), Decimal("0.27"), Decimal(0), "order"),
        FillRow("o3", "overseas", "GOOGL", "SELL", Decimal(1), Decimal("310"), "USD", "2026-03-12T23:30:00+09:00", date(2026, 3, 12), Decimal("0.28"), Decimal("0.01"), "order"),
    ])
    st.replace_fills(acct, "domestic", [
        FillRow("d1", "domestic", "005930", "BUY", Decimal(10), Decimal("70000"), "KRW", "2026-03-10T09:30:00+09:00", date(2026, 3, 10), Decimal(105), Decimal(0), "order"),
        FillRow("d2", "domestic", "440110", "BUY", Decimal(5), Decimal("100000"), "KRW", "2026-03-11T09:30:00+09:00", date(2026, 3, 11), Decimal(75), Decimal(0), "order"),
    ])
    st.upsert_instrument("005930", "삼성전자보통주", "STK", "KR7005930003")
    st.upsert_instrument("440110", "파두", "KSQ", "KR7440110005")
    st.replace_rights([
        {"bass_dt": "20260331", "shtn_pdno": "005930", "pdno": "00000A005930", "prdt_name": "삼성전자", "rght_type_cd": "03",
         "rght_cblc_type_cd": "01", "cblc_qty": "10", "last_alct_qty": "0", "tot_alct_qty": "0", "last_alct_amt": "3610",
         "tax_amt": "0", "cash_dfrm_dt": "20260417"},
        {"bass_dt": "20261231", "shtn_pdno": "440110", "pdno": "00000A440110", "prdt_name": "파두", "rght_type_cd": "03",
         "rght_cblc_type_cd": "01", "cblc_qty": "5", "last_alct_qty": "0", "tot_alct_qty": "0", "last_alct_amt": "500",
         "tax_amt": "77", "cash_dfrm_dt": "20271231"},   # far future: pending, never exported
    ], acct, "20260101", "20271231")
    assert st.accounts() == [acct]

state = {"holdings_usd": {"NVDA": "3"}, "holdings_krw": {"005930": "10", "440110": "5"}, "gf_balances": [], "gf_accounts": [
    {"id": "11111111-2222-3333-4444-555555555555", "name": "KIS", "currency": "USD"},
    {"id": "66666666-2222-3333-4444-555555555555", "name": "KIS KRW", "currency": "KRW"},
]}


def handler(req: httpx.Request) -> httpx.Response:
    if req.url.host == "gf.local":
        if req.url.path == "/api/v1/auth/anonymous":
            return httpx.Response(201, json={"authToken": "jwt"})
        if req.url.path == "/api/v1/account":
            return httpx.Response(200, json={"accounts": state["gf_accounts"]})
        if req.url.path == "/api/v1/account-balance":
            state["gf_balances"].append(json.loads(req.content))
            return httpx.Response(201, json={})
        return httpx.Response(404, json={})
    if req.url.path == "/oauth2/tokenP":
        return httpx.Response(200, json={"access_token": "tok", "token_type": "Bearer", "expires_in": 86400,
                                         "access_token_token_expired": "2030-01-01 09:00:00"})
    tr = req.headers["tr_id"]
    ok = {"rt_cd": "0", "msg_cd": "", "msg1": "", "ctx_area_fk100": "", "ctx_area_nk100": "", "ctx_area_fk200": "", "ctx_area_nk200": ""}
    if tr == "TTTS3012R":
        return httpx.Response(200, headers={"tr_cont": "D"}, json={**ok, "output1": [
            {"ovrs_pdno": s, "ovrs_item_name": s, "ovrs_cblc_qty": q, "tr_crcy_cd": "USD"} for s, q in state["holdings_usd"].items()], "output2": {}})
    if tr == "TTTC8434R":
        return httpx.Response(200, headers={"tr_cont": "D"}, json={**ok, "output1": [
            {"pdno": s, "prdt_name": s, "hldg_qty": q} for s, q in state["holdings_krw"].items()], "output2": [{"dnca_tot_amt": "358883"}]})
    if tr == "CTRP6504R":
        return httpx.Response(200, json={**ok, "output1": [], "output2": [{"crcy_cd": "USD", "frcr_dncl_amt_2": "314.220000"}], "output3": {}})
    return httpx.Response(404, text="nope")


mock = httpx.MockTransport(handler)
_orig = httpx.Client
httpx.Client = lambda **kw: _orig(transport=mock, **{k: v for k, v in kw.items() if k != "transport"})
import brokers.kis.client as cm
try:
    # USD: default file, account "KIS", symbols unchanged, cash pushed to the USD account
    assert gf.main(["--cash"]) == 0
    doc = json.load((WORK / "gf.json").open())
    assert doc["accounts"][0]["name"] == "KIS" and doc["accounts"][0]["currency"] == "USD"
    assert doc["accounts"][0]["balances"][0]["value"] == 314.22
    assert [a["symbol"] for a in doc["activities"]] == ["NVDA", "GOOGL", "GOOGL"] and all(a["currency"] == "USD" for a in doc["activities"])
    assert state["gf_balances"][-1]["accountId"] == "11111111-2222-3333-4444-555555555555" and state["gf_balances"][-1]["balance"] == 314.22

    # USD export carries no dividends (CTRGA011R is domestic)
    assert not [a for a in doc["activities"] if a["type"] == "DIVIDEND"]

    # KRW: _krw file, account "KIS KRW", Yahoo symbols, KRW 예수금 pushed to the KRW account
    assert gf.main(["--currency", "KRW", "--cash"]) == 0
    doc = json.load((WORK / "gf_krw.json").open())
    assert doc["accounts"][0]["name"] == "KIS KRW" and doc["accounts"][0]["currency"] == "KRW" and doc["accounts"][0]["balances"][0]["value"] == 358883.0
    assert all(a["currency"] == "KRW" for a in doc["activities"])
    assert [(a["symbol"], a["type"]) for a in doc["activities"]] == [
        ("005930.KS", "BUY"), ("440110.KQ", "BUY"), ("005930.KS", "DIVIDEND")], doc["activities"]
    assert [a["date"] for a in doc["activities"]] == sorted(a["date"] for a in doc["activities"])
    assert doc["activities"][0]["fee"] == 105.0 and doc["activities"][0]["unitPrice"] == 70000.0
    # the paid dividend: shares held x per share, withholding tax (estimated) as the fee
    div = doc["activities"][2]
    assert div["date"] == "2026-04-17T00:00:00.000Z" and div["quantity"] == 10.0 and div["unitPrice"] == 361.0
    assert div["fee"] == 555.0 and div["comment"] is None  # 3610 x 15.4% truncated
    # --from filters dividends too
    assert gf.main(["--currency", "KRW", "--from", "2026-05-01", "--offline"]) == 0
    assert not [a for a in json.load((WORK / "gf_krw.json").open())["activities"] if a["type"] == "DIVIDEND"]
    assert gf.main(["--currency", "KRW", "--offline"]) == 0
    assert state["gf_balances"][-1]["accountId"] == "66666666-2222-3333-4444-555555555555" and state["gf_balances"][-1]["balance"] == 358883.0
    with KisStore(config.db_path()) as st:
        assert st.last_export("ghostfolio") is not None and st.last_export("ghostfolio:KRW") is not None
        assert st.last_export("tradesviz") is None

    # TradesViz: raw KRX codes, whole-won fees, no dividend rows; per-currency file
    assert tv.main(["--currency", "KRW", "--offline"]) == 0
    rows = list(csv.DictReader((WORK / "tv_krw.csv").open()))
    assert [(r["symbol"], r["quantity"], r["price"], r["currency"], r["commission"]) for r in rows] == [
        ("005930", "10", "70000", "KRW", "105"), ("440110", "5", "100000", "KRW", "75")]
    assert tv.main(["--offline"]) == 0 and (WORK / "tv.csv").exists()
    with KisStore(config.db_path()) as st:
        assert st.last_export("tradesviz") is not None and st.last_export("tradesviz:KRW") is not None

    # holdings mismatch (KRW) -> exit 4, file still written; --kis-account accepts the compact form
    state["holdings_krw"]["440110"] = "6"
    assert gf.main(["--currency", "KRW", "--kis-account", "1234567801"]) == 4
    state["holdings_krw"]["440110"] = "5"
finally:
    httpx.Client = _orig

try:
    gf.main(["--kis-account", "99999999-01", "--offline"])
    raise AssertionError("unknown account accepted")
except SystemExit as e:
    assert "not in the DB" in str(e)
try:
    gf.main(["--currency", "ALL", "--offline"])
    raise AssertionError("--currency ALL accepted for a multi-account broker")
except SystemExit as e:
    assert e.code == 2

print("kis export tests OK")
