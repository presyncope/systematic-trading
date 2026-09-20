# 국내주식 매물대/거래비중

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 시세분석 |
| API ID | 국내주식-196 |
| 실전 TR_ID | FHPST01130000 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 미지원 |
| URL 명 | /uapi/domestic-stock/v1/quotations/pbar-tratio |

## 개요

국내주식 매물대/거래비중 API입니다.
한국투자 HTS(eFriend Plus) &gt; [0113] 당일가격대별 매물대 화면의 데이터 중 일부를 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHPST01130000 |
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
| FID_COND_MRKT_DIV_CODE | 조건시장분류코드 | string | Y | 2 | J:KRX, NX:NXT, UN:통합 |
| FID_INPUT_ISCD | 입력종목코드 | string | Y | 12 | 주식단축종목코드 |
| FID_COND_SCR_DIV_CODE | 조건화면분류코드 | string | Y | 5 | Uniquekey(20113) |
| FID_INPUT_HOUR_1 | 입력시간1 | string | Y | 10 | 공백 |

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
| output1 | 응답상세 | object | Y |  |  |
| rprs_mrkt_kor_name | 대표시장한글명 | string | Y | 40 |  |
| stck_shrn_iscd | 주식단축종목코드 | string | Y | 9 |  |
| hts_kor_isnm | HTS한글종목명 | string | Y | 40 |  |
| stck_prpr | 주식현재가 | string | Y | 10 |  |
| prdy_vrss_sign | 전일대비부호 | string | Y | 1 |  |
| prdy_vrss | 전일대비 | string | Y | 10 |  |
| prdy_ctrt | 전일대비율 | string | Y | 82 |  |
| acml_vol | 누적거래량 | string | Y | 18 |  |
| prdy_vol | 전일거래량 | string | Y | 18 |  |
| wghn_avrg_stck_prc | 가중평균주식가격 | string | Y | 192 |  |
| lstn_stcn | 상장주수 | string | Y | 18 |  |
| output2 | 응답상세 | object array | Y |  | array |
| data_rank | 데이터순위 | string | Y | 10 |  |
| stck_prpr | 주식현재가 | string | Y | 10 |  |
| cntg_vol | 체결거래량 | string | Y | 18 |  |
| acml_vol_rlim | 누적거래량비중 | string | Y | 72 |  |

## Request Example

```
FID_COND_MRKT_DIV_CODE:J
FID_INPUT_ISCD:136480
FID_COND_SCR_DIV_CODE:20113
FID_INPUT_HOUR_1:
```

## Response Example

```json
{
  "output1": {
    "rprs_mrkt_kor_name": "KOSDAQ",
    "stck_shrn_iscd": "136480",
    "hts_kor_isnm": "하림",
    "stck_prpr": "3240",
    "prdy_vrss_sign": "5",
    "prdy_vrss": "-65",
    "prdy_ctrt": "-1.97",
    "acml_vol": "847563",
    "prdy_vol": "974060",
    "wghn_avrg_stck_prc": "3256.34",
    "lstn_stcn": "106209702"
  },
  "output2": [
    {
      "data_rank": "1",
      "stck_prpr": "3255",
      "cntg_vol": "124515",
      "acml_vol_rlim": "14.69"
    },
    {
      "data_rank": "2",
      "stck_prpr": "3260",
      "cntg_vol": "123909",
      "acml_vol_rlim": "14.62"
    },
    {
      "data_rank": "3",
      "stck_prpr": "3250",
      "cntg_vol": "87983",
      "acml_vol_rlim": "10.38"
    },
    "... (15 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
