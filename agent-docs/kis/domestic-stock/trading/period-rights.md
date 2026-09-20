# 기간별계좌권리현황조회

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 주문/계좌 |
| API ID | 국내주식-211 |
| 실전 TR_ID | CTRGA011R |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/domestic-stock/v1/trading/period-rights |

## 개요

기간별계좌권리현황조회 API입니다.
한국투자 HTS(eFriend Plus) &gt; [7344] 권리유형별 현황조회 화면을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | CTRGA011R |
| tr_cont | 연속 거래 여부 | string | N | 1 | 공백 : 초기 조회<br>N : 다음 데이터 조회 (output header의 tr_cont가 M일 경우) |
| custtype | 고객 타입 | string | Y | 1 | B : 법인 <br>P : 개인 |
| seq_no | 일련번호 | string | N | 2 | [법인 필수] 001 |
| mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값 |
| phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호 <br>ex) 01011112222 (하이픈 등 구분값 제거) |
| ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address |
| gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함 |

## Request Query Parameter

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| INQR_DVSN | 조회구분 | string | Y | 2 | 03 입력 |
| CUST_RNCNO25 | 고객실명확인번호25 | string | Y | 25 | 공란 |
| HMID | 홈넷ID | string | Y | 8 | 공란 |
| CANO | 종합계좌번호 | string | Y | 8 | 계좌번호 8자리 입력 (ex.12345678) |
| ACNT_PRDT_CD | 계좌상품코드 | string | Y | 2 | 상품계좌번호 2자리 입력(ex. 01 or 22) |
| INQR_STRT_DT | 조회시작일자 | string | Y | 8 | 조회시작일자(YYYYMMDD) |
| INQR_END_DT | 조회종료일자 | string | Y | 8 | 조회종료일자(YYYYMMDD) |
| RGHT_TYPE_CD | 권리유형코드 | string | Y | 2 | 공란 |
| PDNO | 상품번호 | string | Y | 12 | 공란 |
| PRDT_TYPE_CD | 상품유형코드 | string | Y | 3 | 공란 |
| CTX_AREA_NK100 | 연속조회키100 | string | Y | 100 | 다음조회시 입력 |
| CTX_AREA_FK100 | 연속조회검색조건100 | string | Y | 100 | 다음조회시 입력 |

## Response Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| tr_id | 거래ID | string | Y | 13 | 요청한 tr_id |
| tr_cont | 연속 거래 여부 | string | N | 1 | F or M : 다음 데이터 있음<br>D or E : 마지막 데이터 |
| gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함 |

## Response Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| rt_cd | 성공 실패 여부 | string | Y | 1 |  |
| msg_cd | 응답코드 | string | Y | 8 |  |
| msg1 | 응답메세지 | string | Y | 80 |  |
| output1 | 응답상세 | object array | Y |  | array |
| acno10 | 계좌번호10 | string | Y | 10 |  |
| rght_type_cd | 권리유형코드 | string | Y | 2 | 1	유상<br>2	무상<br>3	배당<br>4	매수청구<br>5	공개매수<br>6	주주총회<br>7	신주인수권증서<br>8	반대의사<br>9	신주인수권증권<br>11	합병<br>12	회사분할<br>13	주식교환<br>14	액면분할<br>15	액면병합<br>16	종목변경<br>17	감자<br>18	신구주합병<br>21	후합병<br>22	후회사분할<br>23	후주식교환<br>24	후액면분할<br>25	후액면병합<br>26	후종목변경<br>27	후감자<br>28	후신구주합병<br>31	뮤츄얼펀드<br>32	ETF<br>33	선박투자회사<br>34	투융자회사<br>35	해외자원<br>36	부동산신탁(Ritz)<br>37	상장수익증권<br>41	ELW만기<br>42	ELS분배<br>43	DLS분배<br>44	하일드펀드<br>45	ETN<br>51	전환청구<br>52	교환청구<br>53	BW청구<br>54	WRT청구<br>55	채권풋옵션청구<br>56	전환우선주청구<br>57	전환조건부청구<br>58	전자증권일괄입고<br>59	클라우드펀딩일괄입고<br>61	원리금상환<br>62	스트립채권<br>71	WRT소멸<br>72	WRT증권<br>73	DR전환<br>74	배당옵션<br>75	특별배당<br>76	ISINCODE변경<br>77	실권주청약<br>81	해외분배금(청산)<br>82	해외분배금(조기상환)<br>83	해외분배금(상장폐지)<br>84	DR FEE<br>85	SECTION 871M<br>86	종목전환<br>87	재매수<br>88	종목교환<br>89	기타이벤트<br>91	공모주<br>92	청약<br>93	환매<br>99	기타권리사유 |
| bass_dt | 기준일자 | string | Y | 8 |  |
| rght_cblc_type_cd | 권리잔고유형코드 | string | Y | 2 | 1	입고<br>2	출고<br>3	출고입고<br>4	출고입금<br>5	출고출금<br>10	현금입금<br>11	단수주대금입금<br>12	교부금입금<br>13	유상감자대금입금<br>14	지연이자입금<br>15	이자지급<br>16	대주권리금출금<br>17	분할상환<br>18	만기상환<br>19	조기상환<br>20	출금<br>21	입고&입금<br>22	입고&입금&단수주대금입금<br>25	유상환불금입금<br>26	중도상환<br>27	분할합병세금출금 |
| rptt_pdno | 대표상품번호 | string | Y | 12 |  |
| pdno | 상품번호 | string | Y | 12 |  |
| prdt_type_cd | 상품유형코드 | string | Y | 3 |  |
| shtn_pdno | 단축상품번호 | string | Y | 12 |  |
| prdt_name | 상품명 | string | Y | 60 |  |
| cblc_qty | 잔고수량 | string | Y | 19 |  |
| last_alct_qty | 최종배정수량 | string | Y | 19 |  |
| excs_alct_qty | 초과배정수량 | string | Y | 19 |  |
| tot_alct_qty | 총배정수량 | string | Y | 19 |  |
| last_ftsk_qty | 최종단수주수량 | string | Y | 191 |  |
| last_alct_amt | 최종배정금액 | string | Y | 19 |  |
| last_ftsk_chgs | 최종단수주대금 | string | Y | 19 |  |
| rdpt_prca | 상환원금 | string | Y | 19 |  |
| dlay_int_amt | 지연이자금액 | string | Y | 19 |  |
| lstg_dt | 상장일자 | string | Y | 8 |  |
| sbsc_end_dt | 청약종료일자 | string | Y | 8 |  |
| cash_dfrm_dt | 현금지급일자 | string | Y | 8 |  |
| rqst_qty | 신청수량 | string | Y | 19 |  |
| rqst_amt | 신청금액 | string | Y | 19 |  |
| rqst_dt | 신청일자 | string | Y | 8 |  |
| rfnd_dt | 환불일자 | string | Y | 8 |  |
| rfnd_amt | 환불금액 | string | Y | 19 |  |
| lstg_stqt | 상장주수 | string | Y | 19 |  |
| tax_amt | 세금금액 | string | Y | 19 |  |
| sbsc_unpr | 청약단가 | string | Y | 224 |  |

## Request Example

```
INQR_DVSN:03
CUST_RNCNO25:
HMID:
CANO:12345678
ACNT_PRDT_CD:01
INQR_STRT_DT:20240508
INQR_END_DT:20241106
RGHT_TYPE_CD:
PDNO:
PRDT_TYPE_CD:
CTX_AREA_NK100:
CTX_AREA_FK100:
```

## Response Example

```json
{
  "ctx_area_nk100": "                                                                                                    ",
  "ctx_area_fk100": "03!^!^!^12345678!^01!^20240508!^20241106!^!^!^                                                      ",
  "output": [
    {
      "acno10": "1234567801",
      "rght_type_cd": "01",
      "bass_dt": "20240919",
      "rght_cblc_type_cd": "01",
      "rptt_pdno": "00000A357880",
      "pdno": "00000A357880",
      "prdt_type_cd": "300",
      "shtn_pdno": "357880",
      "prdt_name": "비트나인",
      "cblc_qty": "1000",
      "last_alct_qty": "1050",
      "excs_alct_qty": "0",
      "tot_alct_qty": "1050",
      "last_ftsk_qty": "0.0000000000",
      "last_alct_amt": "0",
      "last_ftsk_chgs": "0",
      "rdpt_prca": "0",
      "dlay_int_amt": "0",
      "lstg_dt": "",
      "sbsc_end_dt": "20241011",
      "cash_dfrm_dt": "",
      "rqst_qty": "1000",
      "rqst_amt": "1865000",
      "rqst_dt": "20241011",
      "rfnd_dt": "",
      "rfnd_amt": "0",
      "lstg_stqt": "0",
      "tax_amt": "0",
      "sbsc_unpr": "1865.0000"
    }
  ],
  "rt_cd": "0",
  "msg_cd": "KIOK0460",
  "msg1": "조회 되었습니다. (마지막 자료)                                                  "
}
```
