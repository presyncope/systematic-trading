"""KIS auth + client against a MockTransport: token cache/re-issue, tr_cont paging, errors, rate limit."""

import json
import os
import time
from pathlib import Path

import httpx

SCRATCH = Path(__file__).parent
WORK = SCRATCH / "kis_test"
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
""")

from brokers.kis import auth, client as cm, config

config.load(WORK / "config.toml")
assert config.base_url() == "https://kis.mock"
assert config.account() == ("12345678", "01")
assert config.parse_account("1234567801") == ("12345678", "01")
try:
    config.parse_account("123-4")
    raise AssertionError("bad account accepted")
except ValueError:
    pass

state = {"tokens": 0, "calls": [], "fail_next": [], "token_bad": False, "revoked": []}


def handler(req: httpx.Request) -> httpx.Response:
    if req.url.path == "/oauth2/tokenP":
        body = json.loads(req.content)
        assert body == {"grant_type": "client_credentials", "appkey": os.environ["KIS_APP_KEY"], "appsecret": "secret"}
        state["tokens"] += 1
        return httpx.Response(200, json={
            "access_token": f"tok{state['tokens']}", "token_type": "Bearer", "expires_in": 86400,
            "access_token_token_expired": "2030-01-01 09:00:00",
        })
    if req.url.path == "/oauth2/revokeP":
        state["revoked"].append(json.loads(req.content)["token"])
        return httpx.Response(200, json={"code": 200, "message": "ok"})

    h = req.headers
    assert h["appkey"] == os.environ["KIS_APP_KEY"] and h["appsecret"] == "secret" and h["custtype"] == "P"
    state["calls"].append((h["tr_id"], h.get("tr_cont", ""), dict(req.url.params)))
    if state["token_bad"] and h["authorization"] == "Bearer tok1":
        return httpx.Response(500, json={"rt_cd": "1", "msg_cd": "EGW00123", "msg1": "기간이 만료된 token 입니다."})
    if state["fail_next"]:
        return state["fail_next"].pop(0)

    if h["tr_id"] == "TTTC8434R":
        nk = req.url.params.get("CTX_AREA_NK100", "")
        assert h["authorization"].startswith("Bearer tok")
        if nk == "":
            assert h.get("tr_cont", "") == ""
            return httpx.Response(200, headers={"tr_cont": "M"}, json={
                "rt_cd": "0", "msg_cd": "KIOK0510", "msg1": "조회되었습니다",
                "ctx_area_fk100": "12345678^01^N^^01^01^N^N^00^", "ctx_area_nk100": "005930  ",
                "output1": [{"pdno": "005930", "prdt_name": "삼성전자", "hldg_qty": "10"}], "output2": [],
            })
        assert h["tr_cont"] == "N" and nk == "005930" and req.url.params["CTX_AREA_FK100"].startswith("12345678")
        return httpx.Response(200, headers={"tr_cont": "D"}, json={
            "rt_cd": "0", "msg_cd": "KIOK0510", "msg1": "조회되었습니다", "ctx_area_fk100": "", "ctx_area_nk100": "",
            "output1": [{"pdno": "035420", "prdt_name": "NAVER", "hldg_qty": "3"}],
            "output2": [{"dnca_tot_amt": "1234567"}],
        })
    if h["tr_id"] == "TTTS3012R":
        assert req.url.params["OVRS_EXCG_CD"] == "NASD" and req.url.params["CTX_AREA_NK200"] == ""
        return httpx.Response(200, headers={"tr_cont": "D"}, json={
            "rt_cd": "0", "msg_cd": "", "msg1": "", "ctx_area_fk200": "", "ctx_area_nk200": "",
            "output1": [{"ovrs_pdno": "AAPL", "ovrs_item_name": "애플", "ovrs_cblc_qty": "5"}], "output2": {},
        })
    if h["tr_id"] == "BAD":
        return httpx.Response(200, json={"rt_cd": "1", "msg_cd": "OPSQ2000", "msg1": "조회 오류"})
    return httpx.Response(404, text="nope")


mock = httpx.MockTransport(handler)
http = httpx.Client(transport=mock)

# --- auth: issue, cache, reuse; expiry from access_token_token_expired (KST) ---
tok = auth.get_access_token(client=http)
assert tok == "tok1" and state["tokens"] == 1
cached = json.loads((WORK / "token.json").read_text())
assert cached["access_token"] == "tok1"
assert abs(cached["expires_at"] - (time.mktime(time.strptime("2030-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")) - time.timezone + 0)) < 10 * 3600  # sanity only
assert auth.get_access_token(client=http) == "tok1" and state["tokens"] == 1, "cache must be reused"
assert auth.get_access_token(client=http, force=True) == "tok2" and state["tokens"] == 2
assert auth.main(["--status"]) == 0
assert (WORK / "token.json").stat().st_mode & 0o777 == 0o600

# --- client: two-page continuation on TTTC8434R, ctx 200 on TTTS3012R ---
c = cm.KisClient(http=http, min_interval=0)
pages = c.domestic_balance(("12345678", "01"))
assert len(pages) == 2 and [r["pdno"] for p in pages for r in p["output1"]] == ["005930", "035420"]
assert [(t, tc) for t, tc, _ in state["calls"] if t == "TTTC8434R"] == [("TTTC8434R", ""), ("TTTC8434R", "N")]
assert pages[1]["output2"][0]["dnca_tot_amt"] == "1234567"
pages = c.overseas_balance(("12345678", "01"))
assert len(pages) == 1 and pages[0]["output1"][0]["ovrs_pdno"] == "AAPL"

# --- rt_cd != "0" with HTTP 200 -> KisApiError ---
try:
    c.request("GET", "/x", tr_id="BAD")
    raise AssertionError("rt_cd=1 accepted")
except cm.KisApiError as e:
    assert e.msg_cd == "OPSQ2000" and e.status == 200 and "조회 오류" in str(e)

# --- rate limit then success; token expiry -> re-issue once ---
state["fail_next"] = [httpx.Response(500, json={"rt_cd": "1", "msg_cd": "EGW00201", "msg1": "초당 거래건수를 초과하였습니다. (token)"})]
n = len(state["calls"])
pages = c.overseas_balance(("12345678", "01"))
assert len(pages) == 1 and len(state["calls"]) == n + 2 and state["tokens"] == 2, "one retry, no token re-issue"

c2 = cm.KisClient(http=http, min_interval=0)  # picks up tok2 from the cache
(WORK / "token.json").write_text(json.dumps({**cached, "access_token": "tok1"}))  # simulate a stale cached token
c3 = cm.KisClient(http=http, min_interval=0)
state["token_bad"] = True
pages = c3.domestic_balance(("12345678", "01"))
assert len(pages) == 2 and state["tokens"] == 3, "expired token re-issued exactly once"
state["token_bad"] = False

# --- 5xx without a KIS body: retried; 4xx: raised ---
state["fail_next"] = [httpx.Response(502, text="bad gateway")]
pages = c.overseas_balance(("12345678", "01"))
assert len(pages) == 1
state["fail_next"] = [httpx.Response(403, json={"rt_cd": "1", "msg_cd": "EGW00002", "msg1": "권한 없음"})]
try:
    c.overseas_balance(("12345678", "01"))
    raise AssertionError("403 accepted")
except cm.KisApiError as e:
    assert e.status == 403 and e.msg_cd == "EGW00002"

# --- revoke ---
assert auth.revoke_token(client=http) is True and state["revoked"] == ["tok3"] and not (WORK / "token.json").exists()
assert auth.revoke_token(client=http) is False

# --- probe CLI (uses its own httpx client; patch the constructor) ---
_orig = httpx.Client
httpx.Client = lambda **kw: _orig(transport=mock, **{k: v for k, v in kw.items() if k != "transport"})
try:
    assert cm.main(["--probe"]) == 0
    assert cm.main(["--probe", "--account", "bad"]) == 2
finally:
    httpx.Client = _orig

print("kis client tests OK")
