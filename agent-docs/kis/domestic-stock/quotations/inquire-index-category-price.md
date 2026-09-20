# 국내업종 구분별전체시세

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 업종/기타 |
| API ID | v1_국내주식-066 |
| 실전 TR_ID | FHPUP02140000 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/domestic-stock/v1/quotations/inquire-index-category-price |

## 개요

국내업종 구분별전체시세 API입니다.
한국투자 HTS(eFriend Plus) &gt; [0214] 업종 전체시세 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHPUP02140000 |
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
| FID_COND_MRKT_DIV_CODE | FID 조건 시장 분류 코드 | string | Y | 2 | 시장구분코드 (업종 U) |
| FID_INPUT_ISCD | FID 입력 종목코드 | string | Y | 12 | 코스피(0001), 코스닥(1001), 코스피200(2001)<br>...<br>포탈 (FAQ : 종목정보 다운로드(국내) - 업종코드 참조) |
| FID_COND_SCR_DIV_CODE | FID 조건 화면 분류 코드 | string | Y | 5 | Unique key( 20214 ) |
| FID_MRKT_CLS_CODE | FID 시장 구분 코드 | string | Y | 2 | 시장구분코드(K:거래소, Q:코스닥, K2:코스피200) |
| FID_BLNG_CLS_CODE | FID 소속 구분 코드 | string | Y | 2 | 시장구분코드에 따라 아래와 같이 입력<br>시장구분코드(K:거래소) 0:전업종, 1:기타구분, 2:자본금구분 3:상업별구분<br>시장구분코드(Q:코스닥) 0:전업종, 1:기타구분, 2:벤처구분 3:일반구분<br>시장구분코드(K2:코스닥) 0:전업종 |

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
| output1 | 응답상세1 | object | Y |  |  |
| bstp_nmix_prpr | 업종 지수 현재가 | string | Y | 112 |  |
| bstp_nmix_prdy_vrss | 업종 지수 전일 대비 | string | Y | 112 |  |
| prdy_vrss_sign | 전일 대비 부호 | string | Y | 1 |  |
| bstp_nmix_prdy_ctrt | 업종 지수 전일 대비율 | string | Y | 82 |  |
| acml_vol | 누적 거래량 | string | Y | 18 |  |
| acml_tr_pbmn | 누적 거래 대금 | string | Y | 18 |  |
| bstp_nmix_oprc | 업종 지수 시가2 | string | Y | 112 |  |
| bstp_nmix_hgpr | 업종 지수 최고가 | string | Y | 112 |  |
| bstp_nmix_lwpr | 업종 지수 최저가 | string | Y | 112 |  |
| prdy_vol | 전일 거래량 | string | Y | 18 |  |
| ascn_issu_cnt | 상승 종목 수 | string | Y | 7 |  |
| down_issu_cnt | 하락 종목 수 | string | Y | 7 |  |
| stnr_issu_cnt | 보합 종목 수 | string | Y | 7 |  |
| uplm_issu_cnt | 상한 종목 수 | string | Y | 7 |  |
| lslm_issu_cnt | 하한 종목 수 | string | Y | 7 |  |
| prdy_tr_pbmn | 전일 거래 대금 | string | Y | 18 |  |
| dryy_bstp_nmix_hgpr_date | 연중업종지수최고가일자 | string | Y | 8 |  |
| dryy_bstp_nmix_hgpr | 연중업종지수최고가 | string | Y | 112 |  |
| dryy_bstp_nmix_lwpr | 연중업종지수최저가 | string | Y | 112 |  |
| dryy_bstp_nmix_lwpr_date | 연중업종지수최저가일자 | string | Y | 8 |  |
| output2 | 응답상세2 | object array | Y |  | array |
| bstp_cls_code | 업종 구분 코드 | string | Y | 4 |  |
| hts_kor_isnm | HTS 한글 종목명 | string | Y | 40 |  |
| bstp_nmix_prpr | 업종 지수 현재가 | string | Y | 112 |  |
| bstp_nmix_prdy_vrss | 업종 지수 전일 대비 | string | Y | 112 |  |
| prdy_vrss_sign | 전일 대비 부호 | string | Y | 1 |  |
| bstp_nmix_prdy_ctrt | 업종 지수 전일 대비율 | string | Y | 82 |  |
| acml_vol | 누적 거래량 | string | Y | 18 |  |
| acml_tr_pbmn | 누적 거래 대금 | string | Y | 18 |  |
| acml_vol_rlim | 누적 거래량 비중 | string | Y | 72 |  |
| acml_tr_pbmn_rlim | 누적 거래 대금 비중 | string | Y | 72 |  |

## Request Example

```json
{
  "fid_cond_mrkt_div_code": "U",
  "fid_input_iscd": "0001",
  "fid_cond_scr_div_code": "20214",
  "fid_mrkt_cls_code": "K2",
  "fid_blng_cls_code": "0"
}
```

## Response Example

```
{
    "output1": {
        "bstp_nmix_prpr": "2648.76",
        "bstp_nmix_prdy_vrss": "34.96",
        "prdy_vrss_sign": "2",
        "bstp_nmix_prdy_ctrt": "1.34",
        "acml_vol": "584715",
        "acml_tr_pbmn": "10001487",
        "bstp_nmix_oprc": "2635.63",
        "bstp_nmix_hgpr": "2648.76",
        "bstp_nmix_lwpr": "2625.01",
        "prdy_vol": "621363",
        "ascn_issu_cnt": "628",
        "down_issu_cnt": "250",
        "stnr_issu_cnt": "58",
        "uplm_issu_cnt": "0",
        "lslm_issu_cnt": "0",
        "prdy_tr_pbmn": "10691024",
        "dryy_bstp_nmix_hgpr_date": "20240102",
        "dryy_bstp_nmix_hgpr": "2675.80",
        "dryy_bstp_nmix_lwpr": "2429.12",
        "dryy_bstp_nmix_lwpr_date": "20240118"
    },
    "output2": [
        {
            "bstp_cls_code": "2001",
            "hts_kor_isnm": "KOSPI200",
            "bstp_nmix_prpr": "355.52",
            "bstp_nmix_prdy_vrss": "4.31",
            "prdy_vrss_sign": "2",
            "bstp_nmix_prdy_ctrt": "1.23",
            "acml_vol": "118963",
            "acml_tr_pbmn": "7078909",
            "acml_vol_rlim": "100.00",
            "acml_tr_pbmn_rlim": ""
        },
        {
            "bstp_cls_code": "2007",
            "hts_kor_isnm": "KOSPI100",
            "bstp_nmix_prpr": "2691.34",
            "bstp_nmix_prdy_vrss": "33.27",
            "prdy_vrss_sign": "2",
            "bstp_nmix_prdy_ctrt": "1.25",
            "acml_vol": "76784",
            "acml_tr_pbmn": "6124444",
            "acml_vol_rlim": "64.54",
            "acml_tr_pbmn_rlim": ""
        },
        {
            "bstp_cls_code": "2008",
            "hts_kor_isnm": "KOSPI50",
            "bstp_nmix_prpr": "2478.39",
            "bstp_nmix_prdy_vrss": "28.83",
            "prdy_vrss_sign": "2",
            "bstp_nmix_prdy_ctrt": "1.18",
            "acml_vol": "52269",
            "acml_tr_pbmn": "5222300",
            "acml_vol_rlim": "43.94",
            "acml_tr_pbmn_rlim": ""
        },
... (881 more lines omitted)
```
