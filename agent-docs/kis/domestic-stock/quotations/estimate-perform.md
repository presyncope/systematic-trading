# 국내주식 종목추정실적

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 종목정보 |
| API ID | 국내주식-187 |
| 실전 TR_ID | HHKST668300C0 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 미지원 |
| URL 명 | /uapi/domestic-stock/v1/quotations/estimate-perform |

## 개요

국내주식 종목추정실적 API입니다.
한국투자 HTS(eFriend Plus) &gt; [0613] 종목추정실적 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다. 
 
※ 본 화면의 추정실적 및 투자의견은 당월 초의 애널리스트의 의견사항이므로 월중 변동 사항이 있을 수 있음을 유의하시기 바랍니다.
※ 종목별 수익추정은 리서치본부에서 매월 발표되는 거래소, 코스닥 160여개 기업에 한정합니다. 구체적인 종목 리스트는 추정종목리스트를 참고하기 바랍니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | HHKST668300C0 |
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
| SHT_CD | 종목코드 | string | Y | 2 | ex) 265520 |

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
| sht_cd | ELW단축종목코드 | string | Y | 9 |  |
| item_kor_nm | HTS한글종목명 | string | Y | 40 |  |
| name1 | ELW현재가 | string | Y | 10 |  |
| name2 | 전일대비 | string | Y | 10 |  |
| estdate | 전일대비부호 | string | Y | 1 |  |
| rcmd_name | 전일대비율 | string | Y | 82 |  |
| capital | 누적거래량 | string | Y | 18 |  |
| forn_item_lmtrt | 행사가 | string | Y | 112 |  |
| output2 | 응답상세 | object array | Y |  | '(추정손익계산서-6개 array)<br>  매출액, 매출액증감율,<br>  영업이익, 영업이익증감율,<br>  순이익, 순이익증감율,' |
| data1 | DATA1 | string | Y | 15 | 결산연월(outblock4) 참조 |
| data2 | DATA2 | string | Y | 15 | 결산연월(outblock4) 참조 |
| data3 | DATA3 | string | Y | 15 | 결산연월(outblock4) 참조 |
| data4 | DATA4 | string | Y | 15 | 결산연월(outblock4) 참조 |
| data5 | DATA5 | string | Y | 15 | 결산연월(outblock4) 참조 |
| output3 | 응답상세 | object array | Y |  | '(투자지표-8개 array)<br>  EBITDA(십억원), EPS(원), <br>  EPS 증감율(0.1%),  PER(배, 0.1%), <br>  EV/EBITDA(배, 0.1), ROE(0.1%),<br>  부채비율(0.1%), 이자보상배율(0.1%)' |
| data1 | DATA1 | string | Y | 15 | 결산연월(outblock4) 참조 |
| data2 | DATA2 | string | Y | 15 | 결산연월(outblock4) 참조 |
| data3 | DATA3 | string | Y | 15 | 결산연월(outblock4) 참조 |
| data4 | DATA4 | string | Y | 15 | 결산연월(outblock4) 참조 |
| data5 | DATA5 | string | Y | 15 | 결산연월(outblock4) 참조 |
| output4 | 응답상세 | object array | Y |  | array |
| dt | 결산년월 | string | Y | 8 | DATA1 ~5 결산월 정보 |

## Request Example

```
SHT_CD:005930
```

## Response Example

```json
{
  "output1": {
    "sht_cd": "A005930",
    "item_kor_nm": "삼성전자",
    "name1": "김한국",
    "name2": "",
    "estdate": "20240109",
    "rcmd_name": "매수",
    "capital": "8975.0",
    "forn_item_lmtrt": "0.00"
  },
  "output2": [
    {
      "data1": "2796048.0",
      "data2": "3022314.0",
      "data3": "2581509.0",
      "data4": "3048945.0",
      "data5": "3295675.0"
    },
    {
      "data1": "181.0",
      "data2": "81.0",
      "data3": "-146.0",
      "data4": "181.0",
      "data5": "81.0"
    },
    {
      "data1": "516339.0",
      "data2": "433766.0",
      "data3": "65405.0",
      "data4": "330172.0",
      "data5": "555410.0"
    },
    "... (3 more items omitted)"
  ],
  "output3": [
    {
      "data1": "858812.0",
      "data2": "824843.0",
      "data3": "483199.0",
      "data4": "792602.0",
      "data5": "1043367.0"
    },
    {
      "data1": "57770.0",
      "data2": "80570.0",
      "data3": "15609.0",
      "data4": "36983.0",
      "data5": "61483.0"
    },
    {
      "data1": "504.0",
      "data2": "395.0",
      "data3": "-806.0",
      "data4": "1369.0",
      "data5": "662.0"
    },
    "... (5 more items omitted)"
  ],
  "output4": [
    {
      "dt": "2021.12"
    },
    {
      "dt": "2022.12"
    },
    {
      "dt": "2023.12E"
    },
    "... (2 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
