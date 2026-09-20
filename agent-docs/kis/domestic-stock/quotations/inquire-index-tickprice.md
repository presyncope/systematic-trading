# 국내업종 시간별지수(초)

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 업종/기타 |
| API ID | 국내주식-064 |
| 실전 TR_ID | FHPUP02110100 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 미지원 |
| URL 명 | /uapi/domestic-stock/v1/quotations/inquire-index-tickprice |

## 개요

국내업종 시간별지수(초) API입니다. 
한국투자 HTS(eFriend Plus) &gt; [0211] 업종 시간별지수 화면에서 우측 '10초' 선택 시의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHPUP02110100 |
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
| FID_INPUT_ISCD | 입력 종목코드 | string | Y | 12 | 0001:거래소, 1001:코스닥, 2001:코스피200, 3003:KSQ150 |
| FID_COND_MRKT_DIV_CODE | 시장 분류 코드 | string | Y | 2 | 시장구분코드 (업종 U) |

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
| stck_cntg_hour | 주식 체결 시간 | string | Y | 6 |  |
| bstp_nmix_prpr | 업종 지수 현재가 | string | Y | 112 |  |
| bstp_nmix_prdy_vrss | 업종 지수 전일 대비 | string | Y | 112 |  |
| prdy_vrss_sign | 전일 대비 부호 | string | Y | 1 |  |
| bstp_nmix_prdy_ctrt | 업종 지수 전일 대비율 | string | Y | 82 |  |
| acml_tr_pbmn | 누적 거래 대금 | string | Y | 18 |  |
| acml_vol | 누적 거래량 | string | Y | 18 |  |
| cntg_vol | 체결 거래량 | string | Y | 18 |  |

## Request Example

```
fid_cond_mrkt_div_code:U
fid_input_iscd:1001
```

## Response Example

```
{
    "output": [
        {
            "stck_cntg_hour": "100520",
            "bstp_nmix_prpr": "916.59",
            "bstp_nmix_prdy_vrss": "11.09",
            "prdy_vrss_sign": "2",
            "bstp_nmix_prdy_ctrt": "1.22",
            "acml_tr_pbmn": "3818437",
            "acml_vol": "311514",
            "cntg_vol": "378"
        },
        {
            "stck_cntg_hour": "100510",
            "bstp_nmix_prpr": "916.56",
            "bstp_nmix_prdy_vrss": "11.06",
            "prdy_vrss_sign": "2",
            "bstp_nmix_prdy_ctrt": "1.22",
            "acml_tr_pbmn": "3814862",
            "acml_vol": "311136",
            "cntg_vol": "389"
        },
        {
            "stck_cntg_hour": "100500",
            "bstp_nmix_prpr": "916.60",
            "bstp_nmix_prdy_vrss": "11.10",
            "prdy_vrss_sign": "2",
            "bstp_nmix_prdy_ctrt": "1.23",
            "acml_tr_pbmn": "3811191",
            "acml_vol": "310747",
            "cntg_vol": "460"
        },
        {
            "stck_cntg_hour": "100450",
            "bstp_nmix_prpr": "916.71",
            "bstp_nmix_prdy_vrss": "11.21",
            "prdy_vrss_sign": "2",
            "bstp_nmix_prdy_ctrt": "1.24",
            "acml_tr_pbmn": "3806215",
            "acml_vol": "310287",
            "cntg_vol": "347"
        },
        {
            "stck_cntg_hour": "100440",
            "bstp_nmix_prpr": "916.71",
            "bstp_nmix_prdy_vrss": "11.21",
            "prdy_vrss_sign": "2",
            "bstp_nmix_prdy_ctrt": "1.24",
            "acml_tr_pbmn": "3802603",
            "acml_vol": "309940",
            "cntg_vol": "378"
        },
        {
            "stck_cntg_hour": "100430",
            "bstp_nmix_prpr": "916.87",
            "bstp_nmix_prdy_vrss": "11.37",
            "prdy_vrss_sign": "2",
            "bstp_nmix_prdy_ctrt": "1.26",
            "acml_tr_pbmn": "3798885",
            "acml_vol": "309562",
... (908 more lines omitted)
```
