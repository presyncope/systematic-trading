# 국내주식 시가총액 상위

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 순위분석 |
| API ID | v1_국내주식-091 |
| 실전 TR_ID | FHPST01740000 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/domestic-stock/v1/ranking/market-cap |

## 개요

국내주식 시가총액 상위 API입니다.
한국투자 HTS(eFriend Plus) &gt; [0174] 시가총액 상위 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
최대 30건 확인 가능하며, 다음 조회가 불가합니다.

※ 30건 이상의 목록 조회가 필요한 경우, 대안으로 종목조건검색 API를 이용해서 원하는 종목 100개까지 검색할 수 있는 기능을 제공하고 있습니다.
종목조건검색 API는 HTS(efriend Plus) [0110] 조건검색에서 등록 및 서버저장한 나의 조건 목록을 확인할 수 있는 API로,
자세한 사용 방법은 공지사항 - [조건검색 필독] 조건검색 API 이용안내 참고 부탁드립니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHPST01740000 |
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
| fid_input_price_2 | 입력 가격2 | string | Y | 12 | 입력값 없을때 전체 (~ 가격) |
| fid_cond_mrkt_div_code | 조건 시장 분류 코드 | string | Y | 2 | 시장구분코드 (J:KRX, NX:NXT) |
| fid_cond_scr_div_code | 조건 화면 분류 코드 | string | Y | 5 | Unique key( 20174 ) |
| fid_div_cls_code | 분류 구분 코드 | string | Y | 2 | 0: 전체,  1:보통주,  2:우선주 |
| fid_input_iscd | 입력 종목코드 | string | Y | 12 | 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200 |
| fid_trgt_cls_code | 대상 구분 코드 | string | Y | 32 | 0 : 전체 |
| fid_trgt_exls_cls_code | 대상 제외 구분 코드 | string | Y | 32 | 0 : 전체 |
| fid_input_price_1 | 입력 가격1 | string | Y | 12 | 입력값 없을때 전체 (가격 ~) |
| fid_vol_cnt | 거래량 수 | string | Y | 12 | 입력값 없을때 전체 (거래량 ~) |

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
| mksc_shrn_iscd | 유가증권 단축 종목코드 | string | Y | 9 |  |
| data_rank | 데이터 순위 | string | Y | 10 |  |
| hts_kor_isnm | HTS 한글 종목명 | string | Y | 40 |  |
| stck_prpr | 주식 현재가 | string | Y | 10 |  |
| prdy_vrss | 전일 대비 | string | Y | 10 |  |
| prdy_vrss_sign | 전일 대비 부호 | string | Y | 1 |  |
| prdy_ctrt | 전일 대비율 | string | Y | 82 |  |
| acml_vol | 누적 거래량 | string | Y | 18 |  |
| lstn_stcn | 상장 주수 | string | Y | 18 |  |
| stck_avls | 시가 총액 | string | Y | 18 |  |
| mrkt_whol_avls_rlim | 시장 전체 시가총액 비중 | string | Y | 52 |  |

## Request Example

```
{
"fid_cond_mrkt_div_code":"J",
"fid_cond_scr_div_code":"20174",
"fid_div_cls_code":"0",
"fid_input_iscd":"0000",
"fid_trgt_cls_code":"0"
"fid_trgt_exls_cls_code":"0",
"fid_input_price_1":"",
"fid_input_price_2":"",
"fid_vol_cnt":"",
}
```

## Response Example

```json
{
  "output": [
    {
      "mksc_shrn_iscd": "005930",
      "data_rank": "1",
      "hts_kor_isnm": "삼성전자",
      "stck_prpr": "72700",
      "prdy_vrss": "400",
      "prdy_vrss_sign": "2",
      "prdy_ctrt": "0.55",
      "acml_vol": "3686661",
      "lstn_stcn": "5969782550",
      "stck_avls": "4340032",
      "mrkt_whol_avls_rlim": "15.77"
    },
    {
      "mksc_shrn_iscd": "000660",
      "data_rank": "2",
      "hts_kor_isnm": "SK하이닉스",
      "stck_prpr": "162300",
      "prdy_vrss": "1100",
      "prdy_vrss_sign": "2",
      "prdy_ctrt": "0.68",
      "acml_vol": "807093",
      "lstn_stcn": "728002365",
      "stck_avls": "1181548",
      "mrkt_whol_avls_rlim": "4.29"
    },
    {
      "mksc_shrn_iscd": "373220",
      "data_rank": "3",
      "hts_kor_isnm": "LG에너지솔루션",
      "stck_prpr": "404000",
      "prdy_vrss": "5500",
      "prdy_vrss_sign": "2",
      "prdy_ctrt": "1.38",
      "acml_vol": "43109",
      "lstn_stcn": "234000000",
      "stck_avls": "945360",
      "mrkt_whol_avls_rlim": "3.43"
    },
    "... (27 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
