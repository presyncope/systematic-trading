# ELW 변동성 추이(일별)

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] ELW 시세 |
| API ID | 국내주식-178 |
| 실전 TR_ID | FHPEW02840200 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 미지원 |
| URL 명 | /uapi/elw/v1/quotations/volatility-trend-daily |

## 개요

ELW 변동성 추이(일별) API입니다.
한국투자 HTS(eFriend Plus) &gt; [0284] ELW 변동성 추이 화면의 "일별" 변동성 추이 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHPEW02840200 |
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
| FID_COND_MRKT_DIV_CODE | 조건시장분류코드 | string | Y | 2 | 시장구분코드 (W) |
| FID_INPUT_ISCD | 입력종목코드 | string | Y | 12 | ex) 58J297(KBJ297삼성전자콜) |

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
| stck_bsop_date | 주식 영업 일자 | string | Y | 8 |  |
| elw_prpr | ELW 현재가 | string | Y | 10 |  |
| prdy_vrss | 전일대비 | string | Y | 10 |  |
| prdy_vrss_sign | 전일대비부호 | string | Y | 1 |  |
| prdy_ctrt | 전일대비율 | string | Y | 8 |  |
| elw_oprc | elw 시가2 | string | Y | 10 |  |
| elw_hgpr | elw 최고가 | string | Y | 10 |  |
| elw_lwpr | elw 최저가 | string | Y | 10 |  |
| acml_vol | 누적 거래량 | string | Y | 18 |  |
| d10_hist_vltl | 10일 역사적 변동성 | string | Y | 11 |  |
| d20_hist_vltl | 20일 역사적 변동성 | string | Y | 11 |  |
| d30_hist_vltl | 30일 역사적 변동성 | string | Y | 11 |  |
| d60_hist_vltl | 60일 역사적 변동성 | string | Y | 11 |  |
| d90_hist_vltl | 90일 역사적 변동성 | string | Y | 11 |  |
| hts_ints_vltl | HTS 내재 변동성 | string | Y | 11 |  |

## Request Example

```
FID_COND_MRKT_DIV_CODE:W
FID_INPUT_ISCD:57JS61
```

## Response Example

```
{
    "output": [
        {
            "stck_bsop_date": "20240503",
            "elw_prpr": "5",
            "prdy_vrss": "0",
            "prdy_vrss_sign": "3",
            "prdy_ctrt": "0.00",
            "elw_oprc": "5",
            "elw_hgpr": "5",
            "elw_lwpr": "5",
            "acml_vol": "76410",
            "d10_hist_vltl": "21.05",
            "d20_hist_vltl": "20.32",
            "d30_hist_vltl": "19.58",
            "d60_hist_vltl": "17.91",
            "d90_hist_vltl": "18.33",
            "hts_ints_vltl": "23.37"
        },
        {
            "stck_bsop_date": "20240502",
            "elw_prpr": "5",
            "prdy_vrss": "-15",
            "prdy_vrss_sign": "5",
            "prdy_ctrt": "-75.00",
            "elw_oprc": "20",
            "elw_hgpr": "20",
            "elw_lwpr": "5",
            "acml_vol": "6509850",
            "d10_hist_vltl": "23.00",
            "d20_hist_vltl": "21.31",
            "d30_hist_vltl": "20.17",
            "d60_hist_vltl": "19.07",
            "d90_hist_vltl": "18.33",
            "hts_ints_vltl": "20.16"
        },
        {
            "stck_bsop_date": "20240430",
            "elw_prpr": "20",
            "prdy_vrss": "-5",
            "prdy_vrss_sign": "5",
            "prdy_ctrt": "-20.00",
            "elw_oprc": "25",
            "elw_hgpr": "25",
            "elw_lwpr": "15",
            "acml_vol": "1839420",
            "d10_hist_vltl": "23.69",
            "d20_hist_vltl": "21.39",
            "d30_hist_vltl": "20.42",
            "d60_hist_vltl": "19.43",
            "d90_hist_vltl": "18.33",
            "hts_ints_vltl": "23.45"
        },
        {
            "stck_bsop_date": "20240429",
            "elw_prpr": "25",
            "prdy_vrss": "-40",
            "prdy_vrss_sign": "5",
            "prdy_ctrt": "-61.54",
            "elw_oprc": "35",
... (355 more lines omitted)
```
