# 예탁원정보(공모주청약일정)

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 종목정보 |
| API ID | 국내주식-151 |
| 실전 TR_ID | HHKDB669108C0 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 미지원 |
| URL 명 | /uapi/domestic-stock/v1/ksdinfo/pub-offer |

## 개요

예탁원정보(공모주청약일정) API입니다. 
한국투자 HTS(eFriend Plus) &gt; [0667] 공모주청약 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

※ 예탁원에서 제공한 자료이므로 정보용으로만 사용하시기 바랍니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | HHKDB669108C0 |
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
| SHT_CD | 종목코드 | string | Y | 9 | 공백: 전체,  특정종목 조회시 : 종목코드 |
| CTS | CTS | string | Y | 17 | 공백 |
| F_DT | 조회일자From | string | Y | 8 | 일자 ~ |
| T_DT | 조회일자To | string | Y | 8 | ~ 일자 |

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
| fix_subscr_pri | 공모가 | string | Y | 12 |  |
| face_value | 액면가 | string | Y | 9 |  |
| subscr_dt | 청약기간 | string | Y | 23 |  |
| pay_dt | 납입일 | string | Y | 10 |  |
| refund_dt | 환불일 | string | Y | 10 |  |
| list_dt | 상장/등록일 | string | Y | 10 |  |
| lead_mgr | 주간사 | string | Y | 41 |  |
| pub_bf_cap | 공모전자본금 | string | Y | 12 |  |
| pub_af_cap | 공모후자본금 | string | Y | 12 |  |
| assign_stk_qty | 당사배정물량 | string | Y | 12 |  |

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
            "record_date": "20240325",
            "sht_cd": "461030",
            "isin_name": "아이엠비디엑스",
            "fix_subscr_pri": "       13000",
            "face_value": "000000100",
            "subscr_dt": "2024/03/25 ~ 2024/03/26",
            "pay_dt": "2024/03/28",
            "refund_dt": "2024/03/28",
            "list_dt": "",
            "lead_mgr": "미래에셋증권",
            "pub_bf_cap": "     1141762",
            "pub_af_cap": "       62500",
            "assign_stk_qty": "           0"
        },
        {
            "record_date": "20240318",
            "sht_cd": "475240",
            "isin_name": "하나32호기업인수목적",
            "fix_subscr_pri": "        2000",
            "face_value": "000000100",
            "subscr_dt": "2024/03/18 ~ 2024/03/19",
            "pay_dt": "2024/03/21",
            "refund_dt": "2024/03/21",
            "list_dt": "2024/03/27",
            "lead_mgr": "하나증권",
            "pub_bf_cap": "       20000",
            "pub_af_cap": "       75000",
            "assign_stk_qty": "           0"
        },
        {
            "record_date": "20240314",
            "sht_cd": "455900",
            "isin_name": "엔젤로보틱스",
            "fix_subscr_pri": "       20000",
            "face_value": "000000500",
            "subscr_dt": "2024/03/14 ~ 2024/03/15",
            "pay_dt": "2024/03/19",
            "refund_dt": "2024/03/19",
            "list_dt": "2024/03/26",
            "lead_mgr": "NH투자증권",
            "pub_bf_cap": "     6648690",
            "pub_af_cap": "      240000",
            "assign_stk_qty": "           0"
        },
        {
            "record_date": "20240312",
            "sht_cd": "437730",
            "isin_name": "삼현",
            "fix_subscr_pri": "       30000",
            "face_value": "000000500",
            "subscr_dt": "2024/03/12 ~ 2024/03/13",
            "pay_dt": "2024/03/15",
            "refund_dt": "2024/03/15",
            "list_dt": "2024/03/21",
            "lead_mgr": "한국투자증권",
            "pub_bf_cap": "     4267928",
            "pub_af_cap": "      250000",
... (821 more lines omitted)
```
