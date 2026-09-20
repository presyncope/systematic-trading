# 금리 종합(국내채권/금리)

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 업종/기타 |
| API ID | 국내주식-155 |
| 실전 TR_ID | (구) FHPST07020000 (신)HHPST070200C0 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/domestic-stock/v1/quotations/comp-interest |

## 개요

금리 종합(국내채권/금리) API입니다.
한국투자 HTS(eFriend Plus) &gt; [0702] 금리 종합 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

※ 11:30 이후에 신규데이터가 수신되는 점 참고하시기 바랍니다.

구 TR_ID FHPST07020000는 1달 뒤 삭제될 예정이오니 
참고하시기 바랍니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHPST07020000<br>HHPST070200C0 |
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
| FID_COND_MRKT_DIV_CODE | 조건시장분류코드 | string | Y | 2 | Unique key(I) |
| FID_COND_SCR_DIV_CODE | 조건화면분류코드 | string | Y | 5 | Unique key(20702) |
| FID_DIV_CLS_CODE | 분류구분코드 | string | Y | 2 | 0 입력 |
| FID_DIV_CLS_CODE1 | 분류구분코드 | string | Y | 2 | 1 입력 |
| DATA_GB | 구분코드 | string | Y | 1 | 신규 TR_ID HHPST070200C0의 입력값입니다.<br>1 : 장외  최종호가 2 : 해외금리지표 3 : 장내 국고채 |

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
| output1 | 응답상세 | object | Y |  | array |
| bcdt_code | 자료코드 | string | Y | 5 |  |
| hts_kor_isnm | HTS한글종목명 | string | Y | 40 |  |
| bond_mnrt_prpr | 채권금리현재가 | string | Y | 114 |  |
| prdy_vrss_sign | 전일대비부호 | string | Y | 1 |  |
| bond_mnrt_prdy_vrss | 채권금리전일대비 | string | Y | 114 |  |
| prdy_ctrt | 전일대비율 | string | Y | 82 |  |
| stck_bsop_date | 주식영업일자 | string | Y | 8 |  |
| indicator_nm | 금리명 | string | Y | 24 |  |
| indicator_nm | 금리명 | string | Y | 24 | 신규 TR_ID HHPST070200C0의 결과값입니다. |
| bond_cntg_ert | 수익률 | string | Y | 10 | 신규 TR_ID HHPST070200C0의 결과값입니다. |
| prdy_vrss_sign | 전일 대비 부호 | string | Y | 1 | 신규 TR_ID HHPST070200C0의 결과값입니다. |
| prdy_vrss | 전일 대비 | string | Y | 10 | 신규 TR_ID HHPST070200C0의 결과값입니다. |
| prdy_ctrt | 전일 대비율 | string | Y | 8 | 신규 TR_ID HHPST070200C0의 결과값입니다. |
| date_time | 일자+시간 | string | Y | 16 | 신규 TR_ID HHPST070200C0의 결과값입니다. |
| bond_stnd_iscd | 국고채 표준코드 | string | Y | 12 | 신규 TR_ID HHPST070200C0의 결과값입니다. |
| output2 | 응답상세 | object array | Y |  | array |
| bcdt_code | 자료코드 | string | Y | 5 |  |
| hts_kor_isnm | HTS한글종목명 | string | Y | 40 |  |
| bond_mnrt_prpr | 채권금리현재가 | string | Y | 114 |  |
| prdy_vrss_sign | 전일대비부호 | string | Y | 1 |  |
| bond_mnrt_prdy_vrss | 채권금리전일대비 | string | Y | 114 |  |
| bstp_nmix_prdy_ctrt | 업종지수전일대비율 | string | Y | 82 |  |
| stck_bsop_date | 주식영업일자 | string | Y | 8 |  |

## Request Example

```
FID_COND_MRKT_DIV_CODE:I
FID_COND_SCR_DIV_CODE:20702
FID_DIV_CLS_CODE:1
FID_DIV_CLS_CODE1:
DATA_GB :
```

## Response Example

```json
{
  "output1": [
    {
      "bcdt_code": "Y0201",
      "hts_kor_isnm": "미국 30년T-BOND",
      "bond_mnrt_prpr": "4.6500",
      "prdy_vrss_sign": "2",
      "bond_mnrt_prdy_vrss": "0.0100",
      "prdy_ctrt": "0.22",
      "stck_bsop_date": "20240411"
    },
    {
      "bcdt_code": "Y0202",
      "hts_kor_isnm": "미국 10년T-NOTE 수익률",
      "bond_mnrt_prpr": "4.5600",
      "prdy_vrss_sign": "2",
      "bond_mnrt_prdy_vrss": "0.0100",
      "prdy_ctrt": "0.22",
      "stck_bsop_date": "20240411"
    },
    {
      "bcdt_code": "Y0203",
      "hts_kor_isnm": "미국 1년T-BILL",
      "bond_mnrt_prpr": "5.1700",
      "prdy_vrss_sign": "5",
      "bond_mnrt_prdy_vrss": "-0.0200",
      "prdy_ctrt": "-0.39",
      "stck_bsop_date": "20240411"
    },
    "... (4 more items omitted)"
  ],
  "output2": [
    {
      "bcdt_code": "Y0101",
      "hts_kor_isnm": "국고채 3년",
      "bond_mnrt_prpr": "3.4080",
      "prdy_vrss_sign": "5",
      "bond_mnrt_prdy_vrss": "-0.0580",
      "bstp_nmix_prdy_ctrt": "-1.67",
      "stck_bsop_date": "20240412"
    },
    {
      "bcdt_code": "Y0102",
      "hts_kor_isnm": "회사채 무보증 3년AA-",
      "bond_mnrt_prpr": "3.9630",
      "prdy_vrss_sign": "5",
      "bond_mnrt_prdy_vrss": "-0.0530",
      "bstp_nmix_prdy_ctrt": "-1.32",
      "stck_bsop_date": "20240412"
    },
    {
      "bcdt_code": "Y0103",
      "hts_kor_isnm": "회사채 3년 BBB-",
      "bond_mnrt_prpr": "10.1690",
      "prdy_vrss_sign": "5",
      "bond_mnrt_prdy_vrss": "-0.0510",
      "bstp_nmix_prdy_ctrt": "-0.50",
      "stck_bsop_date": "20240412"
    },
    "... (16 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
