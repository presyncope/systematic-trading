# 국내주식 대차대조표

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 종목정보 |
| API ID | v1_국내주식-078 |
| 실전 TR_ID | FHKST66430100 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/domestic-stock/v1/finance/balance-sheet |

## 개요

국내주식 대차대조표 API입니다.
한국투자 HTS(eFriend Plus) &gt; [0635] 재무분석종합 화면의 하단 '1. 대차대조표' 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHKST66430100 |
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
| FID_DIV_CLS_CODE | 분류 구분 코드 | string | Y | 2 | 0: 년, 1: 분기 |
| fid_cond_mrkt_div_code | 조건 시장 분류 코드 | string | Y | 2 | J |
| fid_input_iscd | 입력 종목코드 | string | Y | 12 | 000660 : 종목코드 |

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
| stac_yymm | 결산 년월 | string | Y | 6 |  |
| cras | 유동자산 | string | Y | 112 |  |
| fxas | 고정자산 | string | Y | 112 |  |
| total_aset | 자산총계 | string | Y | 102 |  |
| flow_lblt | 유동부채 | string | Y | 112 |  |
| fix_lblt | 고정부채 | string | Y | 112 |  |
| total_lblt | 부채총계 | string | Y | 102 |  |
| cpfn | 자본금 | string | Y | 22 |  |
| cfp_surp | 자본 잉여금 | string | Y | 182 | 출력되지 않는 데이터(99.99 로 표시) |
| prfi_surp | 이익 잉여금 | string | Y | 182 | 출력되지 않는 데이터(99.99 로 표시) |
| total_cptl | 자본총계 | string | Y | 102 |  |

## Request Example

```json
{
  "fid_cond_mrkt_div_code": "J",
  "fid_input_iscd": "005930",
  "fid_div_cls_code": "1"
}
```

## Response Example

```json
{
  "output": [
    {
      "stac_yymm": "202312",
      "cras": "1959366.00",
      "fxas": "2599694.00",
      "total_aset": "4559060.00",
      "flow_lblt": "757195.00",
      "fix_lblt": "165087.00",
      "total_lblt": "922281.00",
      "cpfn": "8975",
      "cfp_surp": "99.99",
      "prfi_surp": "99.99",
      "total_cptl": "3636779.00"
    },
    {
      "stac_yymm": "202309",
      "cras": "2064386.00",
      "fxas": "2480278.00",
      "total_aset": "4544664.00",
      "flow_lblt": "736252.00",
      "fix_lblt": "169486.00",
      "total_lblt": "905738.00",
      "cpfn": "8975",
      "cfp_surp": "99.99",
      "prfi_surp": "99.99",
      "total_cptl": "3638926.00"
    },
    {
      "stac_yymm": "202306",
      "cras": "2039754.00",
      "fxas": "2440252.00",
      "total_aset": "4480006.00",
      "flow_lblt": "707806.00",
      "fix_lblt": "182443.00",
      "total_lblt": "890249.00",
      "cpfn": "8975",
      "cfp_surp": "99.99",
      "prfi_surp": "99.99",
      "total_cptl": "3589756.00"
    },
    "... (27 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
