# 국내주식 성장성비율

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 종목정보 |
| API ID | v1_국내주식-085 |
| 실전 TR_ID | FHKST66430800 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/domestic-stock/v1/finance/growth-ratio |

## 개요

국내주식 성장성비율 API입니다.
한국투자 HTS(eFriend Plus) &gt; [0635] 재무분석종합 화면의 하단 '7.성장성비율' 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHKST66430800 |
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
| fid_input_iscd | 입력 종목코드 | string | Y | 12 | ex : 000660 |
| fid_div_cls_code | 분류 구분 코드 | string | Y | 2 | 0: 년, 1: 분기 |
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
| stac_yymm | 결산 년월 | string | Y | 6 |  |
| grs | 매출액 증가율 | string | Y | 124 |  |
| bsop_prfi_inrt | 영업 이익 증가율 | string | Y | 124 |  |
| equt_inrt | 자기자본 증가율 | string | Y | 92 |  |
| totl_aset_inrt | 총자산 증가율 | string | Y | 92 |  |

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
      "grs": "-14.33",
      "bsop_prfi_inrt": "-84.86",
      "equt_inrt": "2.52",
      "totl_aset_inrt": "1.67"
    },
    {
      "stac_yymm": "202309",
      "grs": "-17.52",
      "bsop_prfi_inrt": "-90.42",
      "equt_inrt": "5.50",
      "totl_aset_inrt": "-3.36"
    },
    {
      "stac_yymm": "202306",
      "grs": "-20.15",
      "bsop_prfi_inrt": "-95.36",
      "equt_inrt": "9.47",
      "totl_aset_inrt": "-0.01"
    },
    "... (27 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
