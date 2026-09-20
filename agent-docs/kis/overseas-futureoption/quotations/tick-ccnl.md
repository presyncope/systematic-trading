# 해외선물 체결추이(틱)

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [해외선물옵션] 기본시세 |
| API ID | 해외선물-019 |
| 실전 TR_ID | HHDFC55020200 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/overseas-futureoption/v1/quotations/tick-ccnl |

## 개요

해외선물옵션 체결추이(틱) API입니다. 
한국투자 HTS(eFriend Plus) &gt; [5502] 해외선물옵션 체결추이 화면에서 "Tick" 선택 시 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

(중요) 해외선물시세 출력값을 해석하실 때 ffcode.mst(해외선물종목마스터 파일)에 있는 sCalcDesz(계산 소수점) 값을 활용하셔야 정확한 값을 받아오실 수 있습니다.

- ffcode.mst(해외선물종목마스터 파일) 다운로드 방법 2가지
  1) 한국투자증권 Github의 파이썬 샘플코드를 사용하여 mst 파일 다운로드 및 excel 파일로 정제   
     https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/overseas_future_code.py
   
  2) 혹은 포럼 - FAQ - 종목정보 다운로드(해외) - 해외지수선물 클릭하셔서 ffcode.mst(해외선물종목마스터 파일)을 다운로드 후
     Github의 헤더정보(https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/해외선물정보.h)를 참고하여 해석

- 소수점 계산 시, ffcode.mst(해외선물종목마스터 파일)의 sCalcDesz(계산 소수점) 값 참고
  EX) ffcode.mst 파일의 sCalcDesz(계산 소수점) 값
       품목코드 6A 계산소수점 -4 → 시세 6882.5 수신 시 0.68825 로 해석
       품목코드 GC 계산소수점 -1 → 시세 19225 수신 시 1922.5 로 해석

※ CME, SGX 거래소 API시세는 유료시세로 HTS/MTS에서 유료가입 후 익일부터 시세 이용 가능합니다.
포럼 &gt; FAQ &gt; 해외선물옵션 API 유료시세 신청방법(CME, SGX 거래소)

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | HHDFC55020200 |
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
| SRS_CD | 종목코드 | string | Y | 32 | 예) 6AM24 |
| EXCH_CD | 거래소코드 | string | Y | 10 | 예) CME |
| START_DATE_TIME | 조회시작일시 | string | Y | 12 | 공백 |
| CLOSE_DATE_TIME | 조회종료일시 | string | Y | 12 | 예) 20240402 |
| QRY_TP | 조회구분 | string | Y | 1 | Q : 최초조회시 , P : 다음키(INDEX_KEY) 입력하여 조회시 |
| QRY_CNT | 요청개수 | string | Y | 4 | 예) 30 (최대 40) |
| QRY_GAP | 묶음개수 | string | Y | 3 | 공백 (분만 사용) |
| INDEX_KEY | 이전조회KEY | string | Y | 30 | 공백 |

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
| tret_cnt | 자료개수 | string | Y | 4 |  |
| last_n_cnt | N틱최종개수 | string | Y | 4 |  |
| index_key | 이전조회KEY | string | Y | 30 |  |
| output2 | 응답상세 | object array | Y |  | array |
| data_date | 일자 | string | Y | 8 |  |
| data_time | 시각 | string | Y | 6 |  |
| open_price | 시가 | string | Y | 15 |  |
| high_price | 고가 | string | Y | 15 |  |
| low_price | 저가 | string | Y | 15 |  |
| last_price | 체결가격 | string | Y | 15 | 체결가격<br>※ ffcode.mst(해외선물종목마스터 파일)의 sCalcDesz(계산 소수점) 값 참고 |
| last_qntt | 체결수량 | string | Y | 10 |  |
| vol | 누적거래수량 | string | Y | 10 |  |
| prev_diff_flag | 전일대비구분 | string | Y | 1 |  |
| prev_diff_price | 전일대비가격 | string | Y | 15 |  |
| prev_diff_rate | 전일대비율 | string | Y | 10 |  |

## Request Example

```
SRS_CD:6AM24
EXCH_CD:CME
START_DATE_TIME:
CLOSE_DATE_TIME:20240423
QRY_TP:Q
QRY_CNT:40
QRY_GAP:
INDEX_KEY:
```

## Response Example

```json
{
  "output1": {
    "ret_cnt": "0040",
    "last_n_cnt": "0001",
    "index_key": "20240423      6445"
  },
  "output2": [
    {
      "data_date": "20240423",
      "data_time": "164434",
      "open_price": "         6464.5",
      "high_price": "         6464.5",
      "low_price": "         6464.5",
      "last_price": "         6464.5",
      "last_qntt": "         4",
      "vol": "27806",
      "prev_diff_flag": "2",
      "prev_diff_price": "            4.5",
      "prev_diff_rate": "      0.07"
    },
    {
      "data_date": "20240423",
      "data_time": "164434",
      "open_price": "         6464.5",
      "high_price": "         6464.5",
      "low_price": "         6464.5",
      "last_price": "         6464.5",
      "last_qntt": "         1",
      "vol": "27807",
      "prev_diff_flag": "2",
      "prev_diff_price": "            4.5",
      "prev_diff_rate": "      0.07"
    },
    {
      "data_date": "20240423",
      "data_time": "164450",
      "open_price": "         6464.5",
      "high_price": "         6464.5",
      "low_price": "         6464.5",
      "last_price": "         6464.5",
      "last_qntt": "         5",
      "vol": "27812",
      "prev_diff_flag": "2",
      "prev_diff_price": "            4.5",
      "prev_diff_rate": "      0.07"
    },
    "... (37 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
