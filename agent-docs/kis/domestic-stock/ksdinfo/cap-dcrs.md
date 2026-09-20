# 예탁원정보(자본감소일정)

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 종목정보 |
| API ID | 국내주식-149 |
| 실전 TR_ID | HHKDB669106C0 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 미지원 |
| URL 명 | /uapi/domestic-stock/v1/ksdinfo/cap-dcrs |

## 개요

예탁원정보(자본감소일정) API입니다. 
한국투자 HTS(eFriend Plus) &gt; [0665] 자본감소 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

※ 예탁원에서 제공한 자료이므로 정보용으로만 사용하시기 바랍니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | HHKDB669106C0 |
| tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API |
| custtype | 고객 타입 | string | Y | 1 | B : 법인 <br>P : 개인 |
| seq_no | 일련번호 | string | N | 2 | [법인 필수] 001 |
| mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값 |
| phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호 <br>ex) 01011112222 (하이픈 등 구분값 제거) |
| ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address |
| gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함 |

## Request Query Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| CTS | CTS | string | Y | 17 | 공백 |
| F_DT | 조회일자From | string | Y | 8 | 일자 ~ |
| T_DT | 조회일자To | string | Y | 8 | ~ 일자 |
| SHT_CD | 종목코드 | string | Y | 9 | 공백: 전체,  특정종목 조회시 : 종목코드 |

## Response Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| tr_id | 거래ID | string | Y | 13 | 요청한 tr_id |
| tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API |
| gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함 |

## Response Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| rt_cd | 성공 실패 여부 | string | Y | 1 |  |
| msg_cd | 응답코드 | string | Y | 8 |  |
| msg1 | 응답메세지 | string | Y | 80 |  |
| output1 | 응답상세 | object array | Y |  | array |
| record_date | 기준일 | string | Y | 8 |  |
| sht_cd | 종목코드 | string | Y | 9 |  |
| isin_name | 종목명 | string | Y | 40 |  |
| stk_kind | 주식종류 | string | Y | 10 |  |
| reduce_cap_type | 감자구분 | string | Y | 9 |  |
| reduce_cap_rate | 감자배정율 | string | Y | 142 |  |
| comp_way | 계산방법 | string | Y | 6 |  |
| td_stop_dt | 매매거래정지기간 | string | Y | 23 |  |
| list_dt | 상장/등록일 | string | Y | 10 |  |

## Request Example

```
cts:
f_dt:20230301
t_dt:20240326
sht_cd:
```

## Response Example

```
{
    "output1": [
        {
            "record_date": "20240315",
            "sht_cd": "067390",
            "isin_name": "아스트",
            "stk_kind": "보통",
            "reduce_cap_type": "무상감자",
            "reduce_cap_rate": " 1.00",
            "comp_way": "곱하기",
            "td_stop_dt": "2024/03/14 ~ 2024/03/31",
            "list_dt": "2024/04/01"
        },
        {
            "record_date": "20240226",
            "sht_cd": "000040",
            "isin_name": "케이알모터스",
            "stk_kind": "보통",
            "reduce_cap_type": "무상감자",
            "reduce_cap_rate": " 0.30",
            "comp_way": "곱하기",
            "td_stop_dt": "2024/02/23 ~ 2024/03/17",
            "list_dt": "2024/03/18"
        },
        {
            "record_date": "20240208",
            "sht_cd": "033180",
            "isin_name": "케이에이치필룩스",
            "stk_kind": "보통",
            "reduce_cap_type": "무상감자",
            "reduce_cap_rate": " 0.20",
            "comp_way": "곱하기",
            "td_stop_dt": "2024/02/07 ~ 2024/02/28",
            "list_dt": "2024/02/29"
        },
        {
            "record_date": "20240207",
            "sht_cd": "219750",
            "isin_name": "지티지웰니스",
            "stk_kind": "보통",
            "reduce_cap_type": "무상감자",
            "reduce_cap_rate": " 4.00",
            "comp_way": "나누기",
            "td_stop_dt": "",
            "list_dt": ""
        },
        {
            "record_date": "20240129",
            "sht_cd": "057880",
            "isin_name": "피에이치씨",
            "stk_kind": "보통",
            "reduce_cap_type": "무상감자",
            "reduce_cap_rate": " 0.05",
            "comp_way": "곱하기",
            "td_stop_dt": "2024/01/26 ~ 2024/02/20",
            "list_dt": "2024/02/21"
        },
        {
            "record_date": "20240115",
            "sht_cd": "001140",
... (957 more lines omitted)
```
