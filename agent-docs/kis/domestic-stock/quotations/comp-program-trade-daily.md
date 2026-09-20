# 프로그램매매 종합현황(일별)

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 시세분석 |
| API ID | 국내주식-115 |
| 실전 TR_ID | FHPPG04600001 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/domestic-stock/v1/quotations/comp-program-trade-daily |

## 개요

프로그램매매 종합현황(일별) API입니다. 
한국투자 HTS(eFriend Plus) &gt; [0460] 프로그램매매 종합현황 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

* 8개월 이상 과거 조회는 불가하며 에러메시지가 발생합니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | '※ 구TR은 사전고지 없이 막힐 수 있으므로 반드시 신TR로 변경이용 부탁드립니다.<br>[실전투자]<br>(구)FHPPG04600000 → (신)FHPPG04600001' |
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
| FID_COND_MRKT_DIV_CODE | 시장 분류 코드 | string | Y | 2 | J : KRX, NX : NXT, UN : 통합 |
| FID_MRKT_CLS_CODE | 시장 구분 코드 | string | Y | 2 | K:코스피, Q:코스닥 |
| FID_INPUT_DATE_1 | 검색시작일 | string | Y | 10 | 공백 입력, 입력 시 ~ 입력일자까지 조회됨<br>* 8개월 이상 과거 조회 불가 |
| FID_INPUT_DATE_2 | 검색종료일 | string | Y | 10 | 공백 입력 |

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
| nabt_entm_seln_tr_pbmn | 비차익 위탁 매도 거래 대금 | string | Y | 18 |  |
| nabt_onsl_seln_vol | 비차익 자기 매도 거래량 | string | Y | 18 |  |
| whol_onsl_seln_tr_pbmn | 전체 자기 매도 거래 대금 | string | Y | 18 |  |
| arbt_smtn_shnu_vol | 차익 합계 매수2 거래량 | string | Y | 18 |  |
| nabt_smtn_shnu_tr_pbmn | 비차익 합계 매수2 거래 대금 | string | Y | 18 |  |
| arbt_entm_ntby_qty | 차익 위탁 순매수 수량 | string | Y | 18 |  |
| nabt_entm_ntby_tr_pbmn | 비차익 위탁 순매수 거래 대금 | string | Y | 18 |  |
| arbt_entm_seln_vol | 차익 위탁 매도 거래량 | string | Y | 18 |  |
| nabt_entm_seln_vol_rate | 비차익 위탁 매도 거래량 비율 | string | Y | 82 |  |
| nabt_onsl_seln_vol_rate | 비차익 자기 매도 거래량 비율 | string | Y | 82 |  |
| whol_onsl_seln_tr_pbmn_rate | 전체 자기 매도 거래 대금 비율 | string | Y | 82 |  |
| arbt_smtm_shun_vol_rate | 차익 합계 매수 거래량 비율 | string | Y | 72 |  |
| nabt_smtm_shun_tr_pbmn_rate | 비차익 합계 매수 거래대금 비율 | string | Y | 72 |  |
| arbt_entm_ntby_qty_rate | 차익 위탁 순매수 수량 비율 | string | Y | 82 |  |
| nabt_entm_ntby_tr_pbmn_rate | 비차익 위탁 순매수 거래 대금 | string | Y | 82 |  |
| arbt_entm_seln_vol_rate | 차익 위탁 매도 거래량 비율 | string | Y | 82 |  |
| nabt_entm_seln_tr_pbmn_rate | 비차익 위탁 매도 거래 대금 비 | string | Y | 82 |  |
| nabt_onsl_seln_tr_pbmn | 비차익 자기 매도 거래 대금 | string | Y | 18 |  |
| whol_smtn_seln_vol | 전체 합계 매도 거래량 | string | Y | 18 |  |
| arbt_smtn_shnu_tr_pbmn | 차익 합계 매수2 거래 대금 | string | Y | 18 |  |
| whol_entm_shnu_vol | 전체 위탁 매수2 거래량 | string | Y | 18 |  |
| arbt_entm_ntby_tr_pbmn | 차익 위탁 순매수 거래 대금 | string | Y | 18 |  |
| nabt_onsl_ntby_qty | 비차익 자기 순매수 수량 | string | Y | 18 |  |
| arbt_entm_seln_tr_pbmn | 차익 위탁 매도 거래 대금 | string | Y | 18 |  |
| nabt_onsl_seln_tr_pbmn_rate | 비차익 자기 매도 거래 대금 비 | string | Y | 82 |  |
| whol_seln_vol_rate | 전체 매도 거래량 비율 | string | Y | 72 |  |
| arbt_smtm_shun_tr_pbmn_rate | 차익 합계 매수 거래대금 비율 | string | Y | 72 |  |
| whol_entm_shnu_vol_rate | 전체 위탁 매수 거래량 비율 | string | Y | 82 |  |
| arbt_entm_ntby_tr_pbmn_rate | 차익 위탁 순매수 거래 대금 비 | string | Y | 82 |  |
| nabt_onsl_ntby_qty_rate | 비차익 자기 순매수 수량 비율 | string | Y | 82 |  |
| arbt_entm_seln_tr_pbmn_rate | 차익 위탁 매도 거래 대금 비율 | string | Y | 82 |  |
| nabt_smtn_seln_vol | 비차익 합계 매도 거래량 | string | Y | 18 |  |
| whol_smtn_seln_tr_pbmn | 전체 합계 매도 거래 대금 | string | Y | 18 |  |
| nabt_entm_shnu_vol | 비차익 위탁 매수2 거래량 | string | Y | 18 |  |
| whol_entm_shnu_tr_pbmn | 전체 위탁 매수2 거래 대금 | string | Y | 18 |  |
| arbt_onsl_ntby_qty | 차익 자기 순매수 수량 | string | Y | 18 |  |
| nabt_onsl_ntby_tr_pbmn | 비차익 자기 순매수 거래 대금 | string | Y | 18 |  |
| arbt_onsl_seln_tr_pbmn | 차익 자기 매도 거래 대금 | string | Y | 18 |  |
| nabt_smtm_seln_vol_rate | 비차익 합계 매도 거래량 비율 | string | Y | 72 |  |
| whol_seln_tr_pbmn_rate | 전체 매도 거래대금 비율 | string | Y | 72 |  |
| nabt_entm_shnu_vol_rate | 비차익 위탁 매수 거래량 비율 | string | Y | 82 |  |
| whol_entm_shnu_tr_pbmn_rate | 전체 위탁 매수 거래 대금 비율 | string | Y | 82 |  |
| arbt_onsl_ntby_qty_rate | 차익 자기 순매수 수량 비율 | string | Y | 82 |  |
| nabt_onsl_ntby_tr_pbmn_rate | 비차익 자기 순매수 거래 대금 | string | Y | 82 |  |
| arbt_onsl_seln_tr_pbmn_rate | 차익 자기 매도 거래 대금 비율 | string | Y | 82 |  |
| nabt_smtn_seln_tr_pbmn | 비차익 합계 매도 거래 대금 | string | Y | 18 |  |
| arbt_entm_shnu_vol | 차익 위탁 매수2 거래량 | string | Y | 18 |  |
| nabt_entm_shnu_tr_pbmn | 비차익 위탁 매수2 거래 대금 | string | Y | 18 |  |
| whol_onsl_shnu_vol | 전체 자기 매수2 거래량 | string | Y | 18 |  |
| arbt_onsl_ntby_tr_pbmn | 차익 자기 순매수 거래 대금 | string | Y | 18 |  |
| nabt_smtn_ntby_qty | 비차익 합계 순매수 수량 | string | Y | 18 |  |
| arbt_onsl_seln_vol | 차익 자기 매도 거래량 | string | Y | 18 |  |
| nabt_smtm_seln_tr_pbmn_rate | 비차익 합계 매도 거래대금 비율 | string | Y | 72 |  |
| arbt_entm_shnu_vol_rate | 차익 위탁 매수 거래량 비율 | string | Y | 82 |  |
| nabt_entm_shnu_tr_pbmn_rate | 비차익 위탁 매수 거래 대금 비 | string | Y | 82 |  |
| whol_onsl_shnu_tr_pbmn | 전체 자기 매수2 거래 대금 | string | Y | 18 |  |
| arbt_onsl_ntby_tr_pbmn_rate | 차익 자기 순매수 거래 대금 비 | string | Y | 82 |  |
| nabt_smtm_ntby_qty_rate | 비차익 합계 순매수 수량 비율 | string | Y | 72 |  |
| arbt_onsl_seln_vol_rate | 차익 자기 매도 거래량 비율 | string | Y | 82 |  |
| whol_entm_seln_vol | 전체 위탁 매도 거래량 | string | Y | 18 |  |
| arbt_entm_shnu_tr_pbmn | 차익 위탁 매수2 거래 대금 | string | Y | 18 |  |
| nabt_onsl_shnu_vol | 비차익 자기 매수2 거래량 | string | Y | 18 |  |
| whol_onsl_shnu_tr_pbmn_rate | 전체 자기 매수 거래 대금 비율 | string | Y | 82 |  |
| arbt_smtn_ntby_qty | 차익 합계 순매수 수량 | string | Y | 18 |  |
| nabt_smtn_ntby_tr_pbmn | 비차익 합계 순매수 거래 대금 | string | Y | 18 |  |
| arbt_smtn_seln_vol | 차익 합계 매도 거래량 | string | Y | 18 |  |
| whol_entm_seln_tr_pbmn | 전체 위탁 매도 거래 대금 | string | Y | 18 |  |
| arbt_entm_shnu_tr_pbmn_rate | 차익 위탁 매수 거래 대금 비율 | string | Y | 82 |  |
| nabt_onsl_shnu_vol_rate | 비차익 자기 매수 거래량 비율 | string | Y | 82 |  |
| whol_onsl_shnu_vol_rate | 전체 자기 매수 거래량 비율 | string | Y | 82 |  |
| arbt_smtm_ntby_qty_rate | 차익 합계 순매수 수량 비율 | string | Y | 72 |  |
| nabt_smtm_ntby_tr_pbmn_rate | 비차익 합계 순매수 거래대금 비 | string | Y | 72 |  |
| arbt_smtm_seln_vol_rate | 차익 합계 매도 거래량 비율 | string | Y | 72 |  |
| whol_entm_seln_vol_rate | 전체 위탁 매도 거래량 비율 | string | Y | 82 |  |
| arbt_onsl_shnu_vol | 차익 자기 매수2 거래량 | string | Y | 18 |  |
| nabt_onsl_shnu_tr_pbmn | 비차익 자기 매수2 거래 대금 | string | Y | 18 |  |
| whol_smtn_shnu_vol | 전체 합계 매수2 거래량 | string | Y | 18 |  |
| arbt_smtn_ntby_tr_pbmn | 차익 합계 순매수 거래 대금 | string | Y | 18 |  |
| whol_entm_ntby_qty | 전체 위탁 순매수 수량 | string | Y | 18 |  |
| arbt_smtn_seln_tr_pbmn | 차익 합계 매도 거래 대금 | string | Y | 18 |  |
| whol_entm_seln_tr_pbmn_rate | 전체 위탁 매도 거래 대금 비율 | string | Y | 82 |  |
| arbt_onsl_shnu_vol_rate | 차익 자기 매수 거래량 비율 | string | Y | 82 |  |
| nabt_onsl_shnu_tr_pbmn_rate | 비차익 자기 매수 거래 대금 비 | string | Y | 82 |  |
| whol_shun_vol_rate | 전체 매수 거래량 비율 | string | Y | 72 |  |
| arbt_smtm_ntby_tr_pbmn_rate | 차익 합계 순매수 거래대금 비율 | string | Y | 72 |  |
| whol_entm_ntby_qty_rate | 전체 위탁 순매수 수량 비율 | string | Y | 82 |  |
| arbt_smtm_seln_tr_pbmn_rate | 차익 합계 매도 거래대금 비율 | string | Y | 72 |  |
| whol_onsl_seln_vol | 전체 자기 매도 거래량 | string | Y | 18 |  |
| arbt_onsl_shnu_tr_pbmn | 차익 자기 매수2 거래 대금 | string | Y | 18 |  |
| nabt_smtn_shnu_vol | 비차익 합계 매수2 거래량 | string | Y | 18 |  |
| whol_smtn_shnu_tr_pbmn | 전체 합계 매수2 거래 대금 | string | Y | 18 |  |
| nabt_entm_ntby_qty | 비차익 위탁 순매수 수량 | string | Y | 18 |  |
| whol_entm_ntby_tr_pbmn | 전체 위탁 순매수 거래 대금 | string | Y | 18 |  |
| nabt_entm_seln_vol | 비차익 위탁 매도 거래량 | string | Y | 18 |  |
| whol_onsl_seln_vol_rate | 전체 자기 매도 거래량 비율 | string | Y | 82 |  |
| arbt_onsl_shnu_tr_pbmn_rate | 차익 자기 매수 거래 대금 비율 | string | Y | 82 |  |
| nabt_smtm_shun_vol_rate | 비차익 합계 매수 거래량 비율 | string | Y | 72 |  |
| whol_shun_tr_pbmn_rate | 전체 매수 거래대금 비율 | string | Y | 72 |  |
| nabt_entm_ntby_qty_rate | 비차익 위탁 순매수 수량 비율 | string | Y | 82 |  |

## Request Example

```
FID_COND_MRKT_DIV_CODE:UN
FID_MRKT_CLS_CODE:K
FID_INPUT_DATE_1:
FID_INPUT_DATE_2:
```

## Response Example

```
{
    "output": [
        {
            "stck_bsop_date": "20240404",
            "arbt_entm_seln_vol": "945",
            "arbt_entm_seln_vol_rate": "0.20",
            "arbt_entm_seln_tr_pbmn": "60184",
            "arbt_entm_seln_tr_pbmn_rate": "0.50",
            "arbt_onsl_seln_tr_pbmn": "116742",
            "arbt_onsl_seln_tr_pbmn_rate": "0.97",
            "arbt_onsl_seln_vol": "1893",
            "arbt_onsl_seln_vol_rate": "0.40",
            "arbt_smtn_seln_vol": "2839",
            "arbt_smtm_seln_vol_rate": "0.59",
            "arbt_smtn_seln_tr_pbmn": "176926",
            "arbt_smtm_seln_tr_pbmn_rate": "1.48",
            "nabt_entm_seln_vol": "72995",
            "nabt_entm_seln_tr_pbmn": "2335987",
            "nabt_entm_seln_vol_rate": "15.27",
            "nabt_entm_seln_tr_pbmn_rate": "19.50",
            "nabt_onsl_seln_vol": "335",
            "nabt_onsl_seln_vol_rate": "0.07",
            "nabt_onsl_seln_tr_pbmn": "18428",
            "nabt_onsl_seln_tr_pbmn_rate": "0.15",
            "nabt_smtn_seln_vol": "73331",
            "nabt_smtm_seln_vol_rate": "15.34",
            "nabt_smtn_seln_tr_pbmn": "2354415",
            "nabt_smtm_seln_tr_pbmn_rate": "19.66",
            "whol_entm_seln_vol": "73940",
            "whol_entm_seln_tr_pbmn": "2396171",
            "whol_entm_seln_vol_rate": "15.47",
            "whol_entm_seln_tr_pbmn_rate": "20.00",
            "whol_onsl_seln_vol": "2229",
            "whol_onsl_seln_vol_rate": "0.47",
            "whol_onsl_seln_tr_pbmn": "135170",
            "whol_onsl_seln_tr_pbmn_rate": "1.13",
            "whol_smtn_seln_vol": "76169",
            "whol_seln_vol_rate": "15.94",
            "whol_smtn_seln_tr_pbmn": "2531340",
            "whol_seln_tr_pbmn_rate": "21.13",
            "arbt_entm_shnu_vol": "798",
            "arbt_entm_shnu_vol_rate": "0.17",
            "arbt_entm_shnu_tr_pbmn": "50818",
            "arbt_entm_shnu_tr_pbmn_rate": "0.42",
            "arbt_onsl_shnu_vol": "247",
            "arbt_onsl_shnu_vol_rate": "0.05",
            "arbt_onsl_shnu_tr_pbmn": "15309",
            "arbt_onsl_shnu_tr_pbmn_rate": "0.13",
            "arbt_smtn_shnu_vol": "1045",
            "arbt_smtm_shun_vol_rate": "0.22",
            "arbt_smtn_shnu_tr_pbmn": "66127",
            "arbt_smtm_shun_tr_pbmn_rate": "0.55",
            "nabt_entm_shnu_vol": "73441",
            "nabt_entm_shnu_vol_rate": "15.37",
            "nabt_entm_shnu_tr_pbmn": "2581806",
            "nabt_entm_shnu_tr_pbmn_rate": "21.55",
            "nabt_onsl_shnu_vol": "250",
            "nabt_onsl_shnu_vol_rate": "0.05",
            "nabt_onsl_shnu_tr_pbmn": "11652",
            "nabt_onsl_shnu_tr_pbmn_rate": "0.10",
... (289 more lines omitted)
```
