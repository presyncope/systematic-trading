# VI변동성완화 (NXT)

| 항목 | 값 |
|---|---|
| API 통신방식 | WEBSOCKET |
| 메뉴 위치 | [국내주식] 실시간시세 |
| API ID | VI변동성완화 (NXT) |
| 실전 TR_ID | H0NXVIC0 |
| 모의 TR_ID |  |
| HTTP Method | POST |
| 실전 Domain | ws://ops.koreainvestment.com:21000 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /tryitout/H0NXVIC0 |

## 개요

_(없음)_

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | ' 	VI변동성완화 (NXT) H0NXVIC0' |
| tr_cont | 연속 거래 여부 | string | N | 1 | 공백 : 초기 조회 <br>N : 다음 데이터 조회 (output header의 tr_cont가 M일 경우) |
| custtype | 고객 타입 | string | Y | 1 | B : 법인 <br>P : 개인 |
| seq_no | 일련번호 | string | N | 2 | [법인 필수] 001 |
| mac_address | 맥주소 | string | N | 12 | 법인고객 혹은 개인고객의 Mac address 값 |
| phone_number | 핸드폰번호 | string | N | 12 | [법인 필수] 제휴사APP을 사용하는 경우 사용자(회원) 핸드폰번호 <br>ex) 01011112222 (하이픈 등 구분값 제거) |
| ip_addr | 접속 단말 공인 IP | string | N | 12 | [법인 필수] 사용자(회원)의 IP Address |
| gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함 |

## Request Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| TR_ID | 거래ID | string | Y | 2 | '[실전/모의투자]<br>H0NXVIC0 : VI변동성완화 (NXT) ' |
| TR_KEY | 구분값 | string | Y | 12 | 종목코드 (ex 005930 삼성전자) |

## Response Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| tr_id | 거래ID | string | Y | 13 | 요청한 tr_id |
| tr_cont | 연속 거래 여부 | string | N | 1 | 공백 : 초기 조회 <br>N : 다음 데이터 조회 (output header의 tr_cont가 M일 경우) |
| gt_uid | Global UID | string | N | 32 | [법인 전용] 거래고유번호로 사용하므로 거래별로 UNIQUE해야 함 |

## Response Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| BSOP_DATE | 영업일자 | string | Y | 8 |  |
| MKSC_SHRN_ISCD | 종목코드 | string | Y | 9 |  |
| HTS_KOR_ISNM | HTS한글종목명 | string | Y | 40 |  |
| MRKT_DIV_CLS_CODE | 장분류구분코드 | string | Y | 1 |  |
| VI_CLS_CODE | VI적용구분코드 | string | Y | 1 |  |
| vi_cncl_hour | VI해제시각 | string | Y | 6 |  |
| CNTG_VI_HOUR | VI발동시간 | string | Y | 6 |  |
| VI_KIND_CODE | VI종류코드 | string | Y | 1 |  |
| VI_PRC | VI발동가격 | string | Y | 4 |  |
| VI_STND_PRC | 정적VI발동기준가 | string | Y | 4 |  |
| VI_DPRT | 정적VI발동괴리율 | string | Y | 8 |  |
| VI_DMC_STND_PRC | 동적VI발동기준가 | string | Y | 4 |  |
| VI_DMC_DPRT | 동적VI발동괴리율 | string | Y | 8 |  |
| VI_COUNT | VI발동횟수 | string | Y | 4 |  |
| ETP_YN | ETP 여부 | string | Y | 1 | Y : 예 N : 아니오 |

## Request Example

_(없음)_

## Response Example

_(없음)_
