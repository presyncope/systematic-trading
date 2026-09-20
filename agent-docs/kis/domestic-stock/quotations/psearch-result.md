# 종목조건검색조회

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 시세분석 |
| API ID | 국내주식-039 |
| 실전 TR_ID | HHKST03900400 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/domestic-stock/v1/quotations/psearch-result |

## 개요

HTS(efriend Plus) [0110] 조건검색에서 등록 및 서버저장한 나의 조건 목록을 확인할 수 있는 API입니다.
종목조건검색 목록조회 API(/uapi/domestic-stock/v1/quotations/psearch-title)의 output인 'seq'을 종목조건검색조회 API(/uapi/domestic-stock/v1/quotations/psearch-result)의 input으로 사용하시면 됩니다.

※ 시스템 안정성을 위해 API로 제공되는 조건검색 결과의 경우 조건당 100건으로 제한을 둔 점 양해 부탁드립니다.

※ [0110] 화면의 '대상변경' 설정사항은 HTS [0110] 사용자 조건검색 화면에만 적용됨에 유의 부탁드립니다.

※ '조회가 계속 됩니다. (다음을 누르십시오.)' 오류 발생 시 해결방법
→ HTS(efriend Plus) [0110] 조건검색 화면에서 조건을 등록하신 후, 왼쪽 하단의 "사용자조건 서버저장" 클릭하셔서 등록한 조건들을 서버로 보낸 후 다시 API 호출 시도 부탁드립니다.

※ {"rt_cd":"1","msg_cd":"MCA05918","msg1":"종목코드 오류입니다."} 메시지 발생 이유
→ 조건검색 결과 검색된 종목이 0개인 경우 위 응답값을 수신하게 됩니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | HHKST03900400 |
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
| user_id | 사용자 HTS ID | string | Y | 40 |  |
| seq | 사용자조건 키값 | string | Y | 10 | 종목조건검색 목록조회 API의 output인 'seq'을 이용<br>(0 부터 시작) |

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
| output2 | 응답상세 | object array | Y |  | Array |
| code | 종목코드 | string | Y | 6 |  |
| name | 종목명 | string | Y | 20 |  |
| daebi | 전일대비부호 | string | Y | 1 | 1. 상한 2. 상승 3. 보합 4. 하한 5. 하락 |
| price | 현재가 | string | Y | 16 |  |
| chgrate | 등락율 | string | Y | 16 |  |
| acml_vol | 거래량 | string | Y | 16 |  |
| trade_amt | 거래대금 | string | Y | 16 |  |
| change | 전일대비 | string | Y | 16 |  |
| cttr | 체결강도 | string | Y | 16 |  |
| open | 시가 | string | Y | 16 |  |
| high | 고가 | string | Y | 16 |  |
| low | 저가 | string | Y | 16 |  |
| high52 | 52주최고가 | string | Y | 16 |  |
| low52 | 52주최저가 | string | Y | 16 |  |
| expprice | 예상체결가 | string | Y | 16 |  |
| expchange | 예상대비 | string | Y | 16 |  |
| expchggrate | 예상등락률 | string | Y | 16 |  |
| expcvol | 예상체결수량 | string | Y | 16 |  |
| chgrate2 | 전일거래량대비율 | string | Y | 16 |  |
| expdaebi | 예상대비부호 | string | Y | 1 |  |
| recprice | 기준가 | string | Y | 16 |  |
| uplmtprice | 상한가 | string | Y | 16 |  |
| dnlmtprice | 하한가 | string | Y | 16 |  |
| stotprice | 시가총액 | string | Y | 16 |  |

## Request Example

```json
{
  "user_id": "abcd4321",
  "seq": "0"
}
```

## Response Example

```json
{
  "output2": [
    {
      "code": "000120",
      "name": "CJ대한통운",
      "daebi": "0",
      "price": "00000138600.0000",
      "chgrate": "          0.0000",
      "acml_vol": "          0.0000",
      "trade_amt": "          0.0000",
      "change": "          0.0000",
      "cttr": "          0.0000",
      "open": "          0.0000",
      "high": "          0.0000",
      "low": "          0.0000",
      "high52": "     148600.0000",
      "low52": "      69000.0000",
      "expprice": "00000000000.0000",
      "expchange": "          0.0000",
      "expchggrate": "       -100.0000",
      "expcvol": "          0.0000",
      "chgrate2": "          0.0000",
      "expdaebi": "5",
      "recprice": "     138600.0000",
      "uplmtprice": "     180100.0000",
      "dnlmtprice": "      97100.0000",
      "stotprice": "      31617.9088"
    },
    {
      "code": "002320",
      "name": "한진",
      "daebi": "0",
      "price": "00000024350.0000",
      "chgrate": "          0.0000",
      "acml_vol": "          0.0000",
      "trade_amt": "          0.0000",
      "change": "          0.0000",
      "cttr": "          0.0000",
      "open": "          0.0000",
      "high": "          0.0000",
      "low": "          0.0000",
      "high52": "      27300.0000",
      "low52": "      18010.0000",
      "expprice": "00000000000.0000",
      "expchange": "          0.0000",
      "expchggrate": "       -100.0000",
      "expcvol": "          0.0000",
      "chgrate2": "          0.0000",
      "expdaebi": "5",
      "recprice": "      24350.0000",
      "uplmtprice": "      31650.0000",
      "dnlmtprice": "      17050.0000",
      "stotprice": "       3639.7474"
    },
    {
      "code": "002680",
      "name": "한탑",
      "daebi": "0",
      "price": "00000001234.0000",
      "chgrate": "          0.0000",
      "acml_vol": "          0.0000",
      "trade_amt": "          0.0000",
      "change": "          0.0000",
      "cttr": "          0.0000",
      "open": "          0.0000",
      "high": "          0.0000",
      "low": "          0.0000",
      "high52": "       2275.0000",
      "low52": "       1125.0000",
      "expprice": "00000000000.0000",
      "expchange": "          0.0000",
      "expchggrate": "       -100.0000",
      "expcvol": "          0.0000",
      "chgrate2": "          0.0000",
      "expdaebi": "5",
      "recprice": "       1234.0000",
      "uplmtprice": "       1604.0000",
      "dnlmtprice": "        864.0000",
      "stotprice": "        398.7893"
    },
    "... (27 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
