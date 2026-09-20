# 국내주식 당사 신용가능종목

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 종목정보 |
| API ID | 국내주식-111 |
| 실전 TR_ID | FHPST04770000 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/domestic-stock/v1/quotations/credit-by-company |

## 개요

국내주식 당사 신용가능종목 API입니다.
한국투자 HTS(eFriend Plus) &gt; [0477] 당사 신용가능 종목 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
최대 100건 확인 가능하며, 다음 조회가 불가합니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHPST04770000 |
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
| fid_rank_sort_cls_code | 순위 정렬 구분 코드 | string | Y | 2 | 0:코드순, 1:이름순 |
| fid_slct_yn | 선택 여부 | string | Y | 1 | 0:신용주문가능, 1: 신용주문불가 |
| fid_input_iscd | 입력 종목코드 | string | Y | 12 | 0000:전체, 0001:거래소, 1001:코스닥, 2001:코스피200, 4001: KRX100 |
| fid_cond_scr_div_code | 조건 화면 분류 코드 | string | Y | 5 | Unique key(20477) |
| fid_cond_mrkt_div_code | 조건 시장 분류 코드 | string | Y | 2 | 시장구분코드 (주식 J) |

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
| stck_shrn_iscd | 주식 단축 종목코드 | string | Y | 9 |  |
| hts_kor_isnm | HTS 한글 종목명 | string | Y | 40 |  |
| crdt_rate | 신용 비율 | string | Y | 84 |  |

## Request Example

```json
{
  "fid_cond_mrkt_div_code": "J",
  "fid_cond_scr_div_code": "20477",
  "fid_input_iscd": "0000",
  "fid_slct_yn": "0",
  "fid_rank_sort_cls_code": "1"
}
```

## Response Example

```json
{
  "output": [
    {
      "stck_shrn_iscd": "473440",
      "hts_kor_isnm": "ACE 11월만기자동연장회사채AA-이상액티브",
      "crdt_rate": "50.00"
    },
    {
      "stck_shrn_iscd": "105190",
      "hts_kor_isnm": "ACE 200",
      "crdt_rate": "40.00"
    },
    {
      "stck_shrn_iscd": "332500",
      "hts_kor_isnm": "ACE 200TR",
      "crdt_rate": "50.00"
    },
    "... (97 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
