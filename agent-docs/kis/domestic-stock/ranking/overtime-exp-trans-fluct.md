# 국내주식 시간외예상체결등락률

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 시세분석 |
| API ID | 국내주식-140 |
| 실전 TR_ID | FHKST11860000 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/domestic-stock/v1/ranking/overtime-exp-trans-fluct |

## 개요

국내주식 시간외예상체결등락률 API입니다. 
한국투자 HTS(eFriend Plus) &gt; [0236] 시간외 예상체결등락률 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHKST11860000 |
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
| FID_COND_MRKT_DIV_CODE | 조건 시장 분류 코드 | string | Y | 2 | 시장구분코드 (J: 주식) |
| FID_COND_SCR_DIV_CODE | 조건 화면 분류 코드 | string | Y | 5 | Unique key(11186) |
| FID_INPUT_ISCD | 입력 종목코드 | string | Y | 12 | 0000(전체), 0001(코스피), 1001(코스닥) |
| FID_RANK_SORT_CLS_CODE | 순위 정렬 구분 코드 | string | Y | 2 | 0(상승률), 1(상승폭), 2(보합), 3(하락률), 4(하락폭) |
| FID_DIV_CLS_CODE | 분류 구분 코드 | string | Y | 2 | '0(전체), 1(관리종목), 2(투자주의), 3(투자경고),<br> 4(투자위험예고), 5(투자위험), 6(보통주), 7(우선주)' |
| FID_INPUT_PRICE_1 | 입력 가격1 | string | Y | 12 | 가격 ~ |
| FID_INPUT_PRICE_2 | 입력 가격2 | string | Y | 12 | 공백 |
| FID_INPUT_VOL_1 | 입력 거래량 | string | Y | 18 | 거래량 ~ |

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
| output | 응답상세 | object | Y |  |  |
| data_rank | 데이터 순위 | string | Y | 10 |  |
| iscd_stat_cls_code | 종목 상태 구분 코드 | string | Y | 3 |  |
| stck_shrn_iscd | 주식 단축 종목코드 | string | Y | 9 |  |
| hts_kor_isnm | HTS 한글 종목명 | string | Y | 40 |  |
| ovtm_untp_antc_cnpr | 시간외 단일가 예상 체결가 | string | Y | 10 |  |
| ovtm_untp_antc_cntg_vrss | 시간외 단일가 예상 체결 대비 | string | Y | 10 |  |
| ovtm_untp_antc_cntg_vrsssign | 시간외 단일가 예상 체결 대비 | string | Y | 1 |  |
| ovtm_untp_antc_cntg_ctrt | 시간외 단일가 예상 체결 대비율 | string | Y | 82 |  |
| ovtm_untp_askp_rsqn1 | 시간외 단일가 매도호가 잔량1 | string | Y | 12 |  |
| ovtm_untp_bidp_rsqn1 | 시간외 단일가 매수호가 잔량1 | string | Y | 12 |  |
| ovtm_untp_antc_cnqn | 시간외 단일가 예상 체결량 | string | Y | 18 |  |
| itmt_vol | 장중 거래량 | string | Y | 18 |  |
| stck_prpr | 주식 현재가 | string | Y | 10 |  |

## Request Example

```
FID_COND_MRKT_DIV_CODE:J
FID_COND_SCR_DIV_CODE:11186
FID_INPUT_ISCD:0000
FID_RANK_SORT_CLS_CODE:0
FID_DIV_CLS_CODE:0
FID_INPUT_PRICE_1:
FID_INPUT_PRICE_2:
FID_INPUT_VOL_1:
```

## Response Example

```json
{
  "output": [
    {
      "data_rank": "1",
      "iscd_stat_cls_code": "57",
      "stck_shrn_iscd": "025820",
      "hts_kor_isnm": "이구산업",
      "ovtm_untp_antc_cnpr": "6270",
      "ovtm_untp_antc_cntg_vrss": "570",
      "ovtm_untp_antc_cntg_vrss_sign": "1",
      "ovtm_untp_antc_cntg_ctrt": "10.00",
      "ovtm_untp_askp_rsqn1": "231200",
      "ovtm_untp_bidp_rsqn1": "394",
      "ovtm_untp_antc_cnqn": "253267",
      "itmt_vol": "14355442",
      "stck_prpr": "5700"
    },
    {
      "data_rank": "2",
      "iscd_stat_cls_code": "57",
      "stck_shrn_iscd": "024840",
      "hts_kor_isnm": "KBI메탈",
      "ovtm_untp_antc_cnpr": "1805",
      "ovtm_untp_antc_cntg_vrss": "164",
      "ovtm_untp_antc_cntg_vrss_sign": "1",
      "ovtm_untp_antc_cntg_ctrt": "9.99",
      "ovtm_untp_askp_rsqn1": "0",
      "ovtm_untp_bidp_rsqn1": "1512765",
      "ovtm_untp_antc_cnqn": "25869",
      "itmt_vol": "13518874",
      "stck_prpr": "1641"
    },
    {
      "data_rank": "3",
      "iscd_stat_cls_code": "57",
      "stck_shrn_iscd": "097800",
      "hts_kor_isnm": "윈팩",
      "ovtm_untp_antc_cnpr": "1334",
      "ovtm_untp_antc_cntg_vrss": "121",
      "ovtm_untp_antc_cntg_vrss_sign": "1",
      "ovtm_untp_antc_cntg_ctrt": "9.98",
      "ovtm_untp_askp_rsqn1": "150248",
      "ovtm_untp_bidp_rsqn1": "300",
      "ovtm_untp_antc_cnqn": "40546",
      "itmt_vol": "1020359",
      "stck_prpr": "1213"
    },
    "... (27 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
