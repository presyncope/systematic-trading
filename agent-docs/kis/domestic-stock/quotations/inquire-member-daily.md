# 주식현재가 회원사 종목매매동향

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 시세분석 |
| API ID | 국내주식-197 |
| 실전 TR_ID | FHPST04540000 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 미지원 |
| URL 명 | /uapi/domestic-stock/v1/quotations/inquire-member-daily |

## 개요

주식현재가 회원사 종목매매동향 API입니다.
한국투자 HTS(eFriend Plus) &gt; [0454] 증권사 종목매매동향 화면을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHPST04540000 |
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
| FID_COND_MRKT_DIV_CODE | 조건시장분류코드 | string | Y | 2 | J: KRX, NX: NXT, UN: 통합 |
| FID_INPUT_ISCD | 입력종목코드 | string | Y | 12 | 주식종목코드입력 |
| FID_INPUT_ISCD_2 | 회원사코드 | string | Y | 8 | 회원사코드 (kis developers 포탈 사이트 포럼-> FAQ -> 종목정보 다운로드(국내) > 회원사 참조) |
| FID_INPUT_DATE_1 | 입력날짜1 | string | Y | 10 | 날짜 ~ |
| FID_INPUT_DATE_2 | 입력날짜2 | string | Y | 10 | ~ 날짜 |
| FID_SCTN_CLS_CODE | 구간구분코드 | string | Y | 2 | 공백 |

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
| output | 응답상세 | object array | Y |  | array |
| stck_bsop_date | 주식영업일자 | string | Y | 8 |  |
| total_seln_qty | 총매도수량 | string | Y | 18 |  |
| total_shnu_qty | 총매수2수량 | string | Y | 18 |  |
| ntby_qty | 순매수수량 | string | Y | 18 |  |
| stck_prpr | 주식현재가 | string | Y | 10 |  |
| prdy_vrss | 전일대비 | string | Y | 10 |  |
| prdy_vrss_sign | 전일대비부호 | string | Y | 1 |  |
| prdy_ctrt | 전일대비율 | string | Y | 82 |  |
| acml_vol | 누적거래량 | string | Y | 18 |  |

## Request Example

```
FID_COND_MRKT_DIV_CODE:J
FID_INPUT_ISCD:136480
FID_INPUT_ISCD_2:00003
FID_INPUT_DATE_1:20240501
FID_INPUT_DATE_2:20240530
FID_SCTN_CLS_CODE:
```

## Response Example

```json
{
  "output": [
    {
      "stck_bsop_date": "20240530",
      "total_seln_qty": "55432",
      "total_shnu_qty": "81112",
      "ntby_qty": "25680",
      "stck_prpr": "3240",
      "prdy_vrss": "-65",
      "prdy_vrss_sign": "5",
      "prdy_ctrt": "-1.97",
      "acml_vol": "862835"
    },
    {
      "stck_bsop_date": "20240529",
      "total_seln_qty": "53901",
      "total_shnu_qty": "130678",
      "ntby_qty": "76777",
      "stck_prpr": "3305",
      "prdy_vrss": "-30",
      "prdy_vrss_sign": "5",
      "prdy_ctrt": "-0.90",
      "acml_vol": "974060"
    },
    {
      "stck_bsop_date": "20240528",
      "total_seln_qty": "139470",
      "total_shnu_qty": "209017",
      "ntby_qty": "69547",
      "stck_prpr": "3335",
      "prdy_vrss": "-30",
      "prdy_vrss_sign": "5",
      "prdy_ctrt": "-0.89",
      "acml_vol": "1553914"
    },
    "... (16 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
