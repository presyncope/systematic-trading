# 국내주식 실시간프로그램매매 (NXT)

| 항목 | 값 |
|---|---|
| API 통신방식 | WEBSOCKET |
| 메뉴 위치 | [국내주식] 실시간시세 |
| API ID | 국내주식 실시간프로그램매매 (NXT) |
| 실전 TR_ID | H0NXPGM0 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | POST |
| 실전 Domain | ws://ops.koreainvestment.com:21000 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /tryitout/H0NXPGM0 |

## 개요

_(없음)_

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| approval_key | 웹소켓 접속키 | string | N | 286 | 실시간 (웹소켓) 접속키 발급 API(/oauth2/Approval)를 사용하여 발급받은 웹소켓 접속키 |
| custtype | 고객타입 | string | N | 1 | 'B : 법인<br>P : 개인' |
| tr_type | 거래타입 | string | N | 1 | '1 : 등록<br>2 : 해제' |
| content-type | 컨텐츠타입 | string | N | 1 | '	utf-8' |

## Request Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| tr_id | 거래ID | string | Y | 2 | H0NXPGM0 : 실시간 주식프로그램매매 (NXT) |
| tr_key | 구분값 | string | Y | 12 | 종목코드 (ex 005930 삼성전자) |

## Response Body

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| MKSC_SHRN_ISCD | 유가증권 단축 종목코드 | string | Y | 9 |  |
| STCK_CNTG_HOUR | 주식 체결 시간 | string | Y | 6 |  |
| SELN_CNQN | 매도 체결량 | string | Y | 8 |  |
| SELN_TR_PBMN | 매도 거래 대금 | string | Y | 8 |  |
| SHNU_CNQN | 매수2 체결량 | string | Y | 8 |  |
| SHNU_TR_PBMN | 매수2 거래 대금 | string | Y | 8 |  |
| NTBY_CNQN | 순매수 체결량 | string | Y | 8 |  |
| NTBY_TR_PBMN | 순매수 거래 대금 | string | Y | 8 |  |
| SELN_RSQN | 매도호가잔량 | string | Y | 8 |  |
| SHNU_RSQN | 매수호가잔량 | string | Y | 8 |  |
| WHOL_NTBY_QTY | 전체순매수호가잔량 | string | Y | 8 |  |

## Request Example

_(없음)_

## Response Example

_(없음)_
