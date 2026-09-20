# 종목별 일별 대차거래추이

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 시세분석 |
| API ID | 국내주식-135 |
| 실전 TR_ID | HHPST074500C0 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 미지원 |
| URL 명 | /uapi/domestic-stock/v1/quotations/daily-loan-trans |

## 개요

종목별 일별 대차거래추이 API입니다.
한 번의 조회에 최대 100건까지 조회 가능하며, start_date, end_date 를 수정하여 다음 조회가 가능합니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | HHPST074500C0 |
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
| MRKT_DIV_CLS_CODE | 조회구분 | string | Y | 1 | 1(코스피), 2(코스닥), 3(종목) |
| MKSC_SHRN_ISCD | 종목코드 | string | Y | 9 | 종목코드 |
| START_DATE | 조회시작일시 | string | Y | 8 | 조회기간 ~ |
| END_DATE | 조회종료일시 | string | Y | 8 | ~ 조회기간 |
| CTS | 이전조회KEY | string | Y | 8 |  |

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
| bsop_date | 일자 | string | Y | 8 |  |
| stck_prpr | 주식 종가 | string | Y | 10 |  |
| prdy_vrss_sign | 전일 대비 부호 | string | Y | 1 |  |
| prdy_vrss | 전일 대비 | string | Y | 10 |  |
| prdy_ctrt | 전일 대비율 | string | Y | 8 |  |
| acml_vol | 누적 거래량 | string | Y | 18 |  |
| new_stcn | 당일 증가 주수 (체결) | string | Y | 16 |  |
| rdmp_stcn | 당일 감소 주수 (상환) | string | Y | 16 |  |
| prdy_rmnd_vrss | 대차거래 증감 | string | Y | 16 |  |
| rmnd_stcn | 당일 잔고 주수 | string | Y | 16 |  |
| rmnd_amt | 당일 잔고 금액 | string | Y | 20 |  |

## Request Example

```
mrkt_div_cls_code:1
mksc_shrn_iscd:005930
start_date:20240401
end_date:20240430
cts:
```

## Response Example

```json
{
  "output2": [
    {
      "bsop_date": "20240430",
      "stck_prpr": "2692.06",
      "prdy_vrss_sign": "2",
      "prdy_vrss": "4.62",
      "prdy_ctrt": "0.17",
      "acml_vol": "460083500",
      "new_stcn": "14379227",
      "rdmp_stcn": "13993603",
      "prdy_rmnd_vrss": "385624",
      "rmnd_stcn": "947521840",
      "rmnd_amt": "47504735"
    },
    {
      "bsop_date": "20240429",
      "stck_prpr": "2687.44",
      "prdy_vrss_sign": "2",
      "prdy_vrss": "31.11",
      "prdy_ctrt": "1.17",
      "acml_vol": "470546000",
      "new_stcn": "6028334",
      "rdmp_stcn": "13437664",
      "prdy_rmnd_vrss": "-7409330",
      "rmnd_stcn": "947136216",
      "rmnd_amt": "47367356"
    },
    {
      "bsop_date": "20240426",
      "stck_prpr": "2656.33",
      "prdy_vrss_sign": "2",
      "prdy_vrss": "27.71",
      "prdy_ctrt": "1.05",
      "acml_vol": "450520700",
      "new_stcn": "14406990",
      "rdmp_stcn": "12079739",
      "prdy_rmnd_vrss": "2327251",
      "rmnd_stcn": "954545546",
      "rmnd_amt": "46874865"
    },
    "... (18 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
