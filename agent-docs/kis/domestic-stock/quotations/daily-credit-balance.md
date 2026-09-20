# 국내주식 신용잔고 일별추이

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 시세분석 |
| API ID | 국내주식-110 |
| 실전 TR_ID | FHPST04760000 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/domestic-stock/v1/quotations/daily-credit-balance |

## 개요

국내주식 신용잔고 일별추이 API입니다.
한국투자 HTS(eFriend Plus) &gt; [0476] 국내주식 신용잔고 일별추이 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
한 번의 호출에 최대 30건 확인 가능하며, fid_input_date_1 을 입력하여 다음 조회가 가능합니다.

※ 상환수량은 "매도상환수량+현금상환수량"의 합계 수치입니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHPST04760000 |
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
| fid_cond_mrkt_div_code | 시장 분류 코드 | string | Y | 2 | 시장구분코드 (주식 J) |
| fid_cond_scr_div_code | 화면 분류 코드 | string | Y | 5 | Unique key(20476) |
| fid_input_iscd | 종목코드 | string | Y | 12 | 종목코드 (ex 005930) |
| fid_input_date_1 | 결제일자 | string | Y | 10 | 결제일자 (ex 20240313) |

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
| deal_date | 매매 일자 | string | Y | 8 |  |
| stck_prpr | 주식 현재가 | string | Y | 10 |  |
| prdy_vrss_sign | 전일 대비 부호 | string | Y | 1 |  |
| prdy_vrss | 전일 대비 | string | Y | 10 |  |
| prdy_ctrt | 전일 대비율 | string | Y | 82 |  |
| acml_vol | 누적 거래량 | string | Y | 18 |  |
| stlm_date | 결제 일자 | string | Y | 8 |  |
| whol_loan_new_stcn | 전체 융자 신규 주수 | string | Y | 18 | 단위: 주 |
| whol_loan_rdmp_stcn | 전체 융자 상환 주수 | string | Y | 18 | 단위: 주 |
| whol_loan_rmnd_stcn | 전체 융자 잔고 주수 | string | Y | 18 | 단위: 주 |
| whol_loan_new_amt | 전체 융자 신규 금액 | string | Y | 18 | 단위: 만원 |
| whol_loan_rdmp_amt | 전체 융자 상환 금액 | string | Y | 18 | 단위: 만원 |
| whol_loan_rmnd_amt | 전체 융자 잔고 금액 | string | Y | 18 | 단위: 만원 |
| whol_loan_rmnd_rate | 전체 융자 잔고 비율 | string | Y | 84 |  |
| whol_loan_gvrt | 전체 융자 공여율 | string | Y | 82 |  |
| whol_stln_new_stcn | 전체 대주 신규 주수 | string | Y | 18 | 단위: 주 |
| whol_stln_rdmp_stcn | 전체 대주 상환 주수 | string | Y | 18 | 단위: 주 |
| whol_stln_rmnd_stcn | 전체 대주 잔고 주수 | string | Y | 18 | 단위: 주 |
| whol_stln_new_amt | 전체 대주 신규 금액 | string | Y | 18 | 단위: 만원 |
| whol_stln_rdmp_amt | 전체 대주 상환 금액 | string | Y | 18 | 단위: 만원 |
| whol_stln_rmnd_amt | 전체 대주 잔고 금액 | string | Y | 18 | 단위: 만원 |
| whol_stln_rmnd_rate | 전체 대주 잔고 비율 | string | Y | 84 |  |
| whol_stln_gvrt | 전체 대주 공여율 | string | Y | 82 |  |
| stck_oprc | 주식 시가2 | string | Y | 10 |  |
| stck_hgpr | 주식 최고가 | string | Y | 10 |  |
| stck_lwpr | 주식 최저가 | string | Y | 10 |  |

## Request Example

```json
{
  "fid_cond_mrkt_div_code": "J",
  "fid_cond_scr_div_code": "20476",
  "fid_input_iscd": "005930",
  "fid_input_date_1": "20240315"
}
```

## Response Example

```json
{
  "output": [
    {
      "deal_date": "20240313",
      "stck_prpr": "74100",
      "prdy_vrss_sign": "2",
      "prdy_vrss": "800",
      "prdy_ctrt": "1.09",
      "acml_vol": "15243134",
      "stlm_date": "20240315",
      "whol_loan_new_stcn": "253817",
      "whol_loan_rdmp_stcn": "603451",
      "whol_loan_rmnd_stcn": "7155720",
      "whol_loan_new_amt": "1678904",
      "whol_loan_rdmp_amt": "3982732",
      "whol_loan_rmnd_amt": "47321639",
      "whol_loan_rmnd_rate": "0.11",
      "whol_loan_gvrt": "1.65",
      "whol_stln_new_stcn": "0",
      "whol_stln_rdmp_stcn": "0",
      "whol_stln_rmnd_stcn": "6861",
      "whol_stln_new_amt": "0",
      "whol_stln_rdmp_amt": "0",
      "whol_stln_rmnd_amt": "43104",
      "whol_stln_rmnd_rate": "0.00",
      "whol_stln_gvrt": "0.00",
      "stck_oprc": "73700",
      "stck_hgpr": "74100",
      "stck_lwpr": "73500"
    },
    {
      "deal_date": "20240312",
      "stck_prpr": "73300",
      "prdy_vrss_sign": "2",
      "prdy_vrss": "900",
      "prdy_ctrt": "1.24",
      "acml_vol": "13011654",
      "stlm_date": "20240314",
      "whol_loan_new_stcn": "357971",
      "whol_loan_rdmp_stcn": "429002",
      "whol_loan_rmnd_stcn": "7507526",
      "whol_loan_new_amt": "2370294",
      "whol_loan_rdmp_amt": "2871401",
      "whol_loan_rmnd_amt": "49639923",
      "whol_loan_rmnd_rate": "0.12",
      "whol_loan_gvrt": "2.74",
      "whol_stln_new_stcn": "0",
      "whol_stln_rdmp_stcn": "0",
      "whol_stln_rmnd_stcn": "6861",
      "whol_stln_new_amt": "0",
      "whol_stln_rdmp_amt": "0",
      "whol_stln_rmnd_amt": "43104",
      "whol_stln_rmnd_rate": "0.00",
      "whol_stln_gvrt": "0.00",
      "stck_oprc": "72600",
      "stck_hgpr": "73500",
      "stck_lwpr": "72100"
    },
    {
      "deal_date": "20240311",
      "stck_prpr": "72400",
      "prdy_vrss_sign": "5",
      "prdy_vrss": "-900",
      "prdy_ctrt": "-1.23",
      "acml_vol": "9740504",
      "stlm_date": "20240313",
      "whol_loan_new_stcn": "395234",
      "whol_loan_rdmp_stcn": "242330",
      "whol_loan_rmnd_stcn": "7586197",
      "whol_loan_new_amt": "2579480",
      "whol_loan_rdmp_amt": "1479272",
      "whol_loan_rmnd_amt": "50194590",
      "whol_loan_rmnd_rate": "0.12",
      "whol_loan_gvrt": "4.05",
      "whol_stln_new_stcn": "0",
      "whol_stln_rdmp_stcn": "0",
      "whol_stln_rmnd_stcn": "6861",
      "whol_stln_new_amt": "0",
      "whol_stln_rdmp_amt": "0",
      "whol_stln_rmnd_amt": "43104",
      "whol_stln_rmnd_rate": "0.00",
      "whol_stln_gvrt": "0.00",
      "stck_oprc": "72900",
      "stck_hgpr": "73100",
      "stck_lwpr": "72300"
    },
    "... (27 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
