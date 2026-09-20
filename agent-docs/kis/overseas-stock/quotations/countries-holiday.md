# 해외결제일자조회

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [해외주식] 기본시세 |
| API ID | 해외주식-017 |
| 실전 TR_ID | CTOS5011R |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/overseas-stock/v1/quotations/countries-holiday |

## 개요

해외결제일자조회 API입니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | CTOS5011R |
| tr_cont | 연속 거래 여부 | string | N | 1 | tr_cont를 이용한 다음조회 불가 API |
| custtype | 고객 타입 | string | N | 1 | B : 법인 <br>P : 개인 |
| seq_no | 일련번호 | string | N | 2 | [법인 필수] 001 |
| mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값 |
| phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호 <br>ex) 01011112222 (하이픈 등 구분값 제거) |
| ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address |
| gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함 |

## Request Query Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| TRAD_DT | 기준일자 | string | Y | 8 | 기준일자(YYYYMMDD) |
| CTX_AREA_NK | 연속조회키 | string | Y | 20 | 공백으로 입력 |
| CTX_AREA_FK | 연속조회검색조건 | string | Y | 20 | 공백으로 입력 |

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
| output | 응답상세1 | object | Y |  |  |
| prdt_type_cd | 상품유형코드 | string | Y | 3 | 512  미국 나스닥 / 513  미국 뉴욕거래소 / 529  미국 아멕스 <br>515  일본<br>501  홍콩 / 543  홍콩CNY / 558  홍콩USD<br>507  베트남 하노이거래소 / 508  베트남 호치민거래소<br>551  중국 상해A / 552  중국 심천A |
| tr_natn_cd | 거래국가코드 | string | Y | 3 | 840 미국 / 392 일본 / 344 홍콩<br>704 베트남 / 156 중국 |
| tr_natn_name | 거래국가명 | string | Y | 60 |  |
| natn_eng_abrv_cd | 국가영문약어코드 | string | Y | 2 | US 미국 / JP 일본 / HK 홍콩<br>VN 베트남 / CN 중국 |
| tr_mket_cd | 거래시장코드 | string | Y | 2 |  |
| tr_mket_name | 거래시장명 | string | Y | 60 |  |
| acpl_sttl_dt | 현지결제일자 | string | Y | 8 | 현지결제일자(YYYYMMDD) |
| dmst_sttl_dt | 국내결제일자 | string | Y | 8 | 국내결제일자(YYYYMMDD) |

## Request Example

```json
{
  "TRAD_DT": "20221227",
  "CTX_AREA_NK": "",
  "CTX_AREA_FK": ""
}
```

## Response Example

```json
{
  "ctx_area_fk": "20221227            ",
  "ctx_area_nk": "                    ",
  "output": [
    {
      "prdt_type_cd": "507",
      "tr_natn_cd": "704",
      "tr_natn_name": "베트남",
      "natn_eng_abrv_cd": "VN",
      "tr_mket_cd": "01",
      "tr_mket_name": "하노이거래소",
      "acpl_sttl_dt": "20221229",
      "dmst_sttl_dt": "20221229"
    },
    {
      "prdt_type_cd": "508",
      "tr_natn_cd": "704",
      "tr_natn_name": "베트남",
      "natn_eng_abrv_cd": "VN",
      "tr_mket_cd": "02",
      "tr_mket_name": "호치민거래소",
      "acpl_sttl_dt": "20221229",
      "dmst_sttl_dt": "20221229"
    },
    {
      "prdt_type_cd": "512",
      "tr_natn_cd": "840",
      "tr_natn_name": "미국",
      "natn_eng_abrv_cd": "US",
      "tr_mket_cd": "01",
      "tr_mket_name": "나스닥",
      "acpl_sttl_dt": "20221229",
      "dmst_sttl_dt": "20221230"
    },
    "... (6 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "KIOK0460",
  "msg1": "조회 되었습니다. (마지막 자료)                                                  "
}
```
