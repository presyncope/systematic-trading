# 해외증거금 통화별조회

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [해외주식] 주문/계좌 |
| API ID | 해외주식-035 |
| 실전 TR_ID | TTTC2101R |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/overseas-stock/v1/trading/foreign-margin |

## 개요

해외증거금 통화별조회 API입니다.
한국투자 HTS(eFriend Plus) &gt; [7718] 해외주식 증거금상세 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | TTTC2101R |
| tr_cont | 연속 거래 여부 | string | N | 1 | 공백 : 초기 조회<br>N : 다음 데이터 조회 (output header의 tr_cont가 M일 경우) |
| custtype | 고객 타입 | string | Y | 1 | B : 법인 <br>P : 개인 |
| seq_no | 일련번호 | string | N | 2 | [법인 필수] 001 |
| mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값 |
| phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호 <br>ex) 01011112222 (하이픈 등 구분값 제거) |
| ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address |
| gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함 |

## Request Query Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| CANO | 종합계좌번호 | string | Y | 8 |  |
| ACNT_PRDT_CD | 계좌상품코드 | string | Y | 2 |  |

## Response Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| tr_id | 거래ID | string | Y | 13 | 요청한 tr_id |
| tr_cont | 연속 거래 여부 | string | N | 1 | F or M : 다음 데이터 있음<br>D or E : 마지막 데이터 |
| gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함 |

## Response Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| rt_cd | 성공 실패 여부 | string | Y | 1 |  |
| msg_cd | 응답코드 | string | Y | 8 |  |
| msg1 | 응답메세지 | string | Y | 80 |  |
| output | 응답상세 | object array | Y |  | array |
| natn_name | 국가명 | string | Y | 60 |  |
| crcy_cd | 통화코드 | string | Y | 3 |  |
| frcr_dncl_amt1 | 외화예수금액 | string | Y | 186 |  |
| ustl_buy_amt | 미결제매수금액 | string | Y | 182 |  |
| ustl_sll_amt | 미결제매도금액 | string | Y | 182 |  |
| frcr_rcvb_amt | 외화미수금액 | string | Y | 182 |  |
| frcr_mgn_amt | 외화증거금액 | string | Y | 186 |  |
| frcr_gnrl_ord_psbl_amt | 외화일반주문가능금액 | string | Y | 182 |  |
| frcr_ord_psbl_amt1 | 외화주문가능금액 | string | Y | 186 | 원화주문가능환산금액 |
| itgr_ord_psbl_amt | 통합주문가능금액 | string | Y | 182 |  |
| bass_exrt | 기준환율 | string | Y | 238 |  |

## Request Example

```
CANO:12345678
ACNT_PRDT_CD:01
```

## Response Example

```json
{
  "output": [
    {
      "natn_name": "미국",
      "crcy_cd": "USD",
      "frcr_dncl_amt1": "698.190000",
      "ustl_buy_amt": "0.00",
      "ustl_sll_amt": "0.00",
      "frcr_rcvb_amt": "0.00",
      "frcr_mgn_amt": "0.000000",
      "frcr_gnrl_ord_psbl_amt": "694.37",
      "frcr_ord_psbl_amt1": "0.000000",
      "itgr_ord_psbl_amt": "1094.52",
      "bass_exrt": "1349.40000000"
    },
    {
      "natn_name": "홍콩",
      "crcy_cd": "HKD",
      "frcr_dncl_amt1": "0.000000",
      "ustl_buy_amt": "0.00",
      "ustl_sll_amt": "0.00",
      "frcr_rcvb_amt": "0.00",
      "frcr_mgn_amt": "0.000000",
      "frcr_gnrl_ord_psbl_amt": "0.00",
      "frcr_ord_psbl_amt1": "0.000000",
      "itgr_ord_psbl_amt": "8247.35",
      "bass_exrt": "172.97000000"
    },
    {
      "natn_name": "홍콩",
      "crcy_cd": "CNY",
      "frcr_dncl_amt1": "1459.110000",
      "ustl_buy_amt": "0.00",
      "ustl_sll_amt": "0.00",
      "frcr_rcvb_amt": "0.00",
      "frcr_mgn_amt": "0.000000",
      "frcr_gnrl_ord_psbl_amt": "0.00",
      "frcr_ord_psbl_amt1": "0.000000",
      "itgr_ord_psbl_amt": "7705.45",
      "bass_exrt": "186.89000000"
    },
    "... (47 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "KIOK0510",
  "msg1": "조회가 완료되었습니다                                                           "
}
```
