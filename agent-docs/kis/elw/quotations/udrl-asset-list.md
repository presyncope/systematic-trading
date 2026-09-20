# ELW 기초자산 목록조회

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] ELW 시세 |
| API ID | 국내주식-185 |
| 실전 TR_ID | FHKEW154100C0 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/elw/v1/quotations/udrl-asset-list |

## 개요

ELW 기초자산 목록조회 API입니다.
한국투자 HTS(eFriend Plus) &gt; [0288] ELW 기초자산별 ELW 시세 화면 의 "왼쪽 기초자산 목록" 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHKEW154100C0 |
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
| FID_COND_SCR_DIV_CODE | 조건화면분류코드 | string | Y | 5 | 11541(Primary key) |
| FID_RANK_SORT_CLS_CODE | 순위정렬구분코드 | string | Y | 2 | 0(종목명순), 1(콜발행종목순), 2(풋발행종목순), 3(전일대비 상승율순), 4(전일대비 하락율순), 5(현재가 크기순), 6(종목코드순) |
| FID_INPUT_ISCD | 입력종목코드 | string | Y | 12 | 00000(전체), 00003(한국투자증권), 00017(KB증권), 00005(미래에셋) |

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
| unas_shrn_iscd | 기초자산단축종목코드 | string | Y | 9 |  |
| unas_isnm | 기초자산종목명 | string | Y | 40 |  |
| unas_prpr | 기초자산현재가 | string | Y | 112 |  |
| unas_prdy_vrss | 기초자산전일대비 | string | Y | 112 |  |
| unas_prdy_vrss_sign | 기초자산전일대비부호 | string | Y | 1 |  |
| unas_prdy_ctrt | 기초자산전일대비율 | string | Y | 82 |  |

## Request Example

```
FID_COND_SCR_DIV_CODE:11541
FID_RANK_SORT_CLS_CODE:0
FID_INPUT_ISCD:00000
```

## Response Example

```
{
    "output": [
        {
            "unas_shrn_iscd": "2001",
            "unas_isnm": "KOSPI200",
            "unas_prpr": "371.33",
            "unas_prdy_vrss": "0.17",
            "unas_prdy_vrss_sign": "2",
            "unas_prdy_ctrt": "0.05"
        },
        {
            "unas_shrn_iscd": "000990",
            "unas_isnm": "DB하이텍",
            "unas_prpr": "40850.00",
            "unas_prdy_vrss": "-300.00",
            "unas_prdy_vrss_sign": "5",
            "unas_prdy_ctrt": "-0.73"
        },
        {
            "unas_shrn_iscd": "009540",
            "unas_isnm": "HD한국조선해양",
            "unas_prpr": "135400.00",
            "unas_prdy_vrss": "1100.00",
            "unas_prdy_vrss_sign": "2",
            "unas_prdy_ctrt": "0.82"
        },
        {
            "unas_shrn_iscd": "267260",
            "unas_isnm": "HD현대일렉트릭",
            "unas_prpr": "302500.00",
            "unas_prdy_vrss": "9000.00",
            "unas_prdy_vrss_sign": "2",
            "unas_prdy_ctrt": "3.07"
        },
        {
            "unas_shrn_iscd": "028300",
            "unas_isnm": "HLB",
            "unas_prpr": "64700.00",
            "unas_prdy_vrss": "8500.00",
            "unas_prdy_vrss_sign": "2",
            "unas_prdy_ctrt": "15.12"
        },
        {
            "unas_shrn_iscd": "011200",
            "unas_isnm": "HMM",
            "unas_prpr": "18010.00",
            "unas_prdy_vrss": "460.00",
            "unas_prdy_vrss_sign": "2",
            "unas_prdy_ctrt": "2.62"
        },
        {
            "unas_shrn_iscd": "403870",
            "unas_isnm": "HPSP",
            "unas_prpr": "45200.00",
            "unas_prdy_vrss": "2900.00",
            "unas_prdy_vrss_sign": "2",
            "unas_prdy_ctrt": "6.86"
        },
        {
            "unas_shrn_iscd": "035900",
... (51 more lines omitted)
```
