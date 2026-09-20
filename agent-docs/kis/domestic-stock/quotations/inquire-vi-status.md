# 변동성완화장치(VI) 현황

| 항목 | 값 |
|---|---|
| API 통신방식 | REST |
| 메뉴 위치 | [국내주식] 업종/기타 |
| API ID | v1_국내주식-055 |
| 실전 TR_ID | FHPST01390000 |
| 모의 TR_ID | 모의투자 미지원 |
| HTTP Method | GET |
| 실전 Domain | https://openapi.koreainvestment.com:9443 |
| 모의 Domain | 모의투자 미지원 |
| URL 명 | /uapi/domestic-stock/v1/quotations/inquire-vi-status |

## 개요

HTS(eFriend Plus) [0139] 변동성 완화장치(VI) 현황 데이터를 확인할 수 있는 API입니다.

최근 30건까지 확인 가능합니다.

## Request Header

| Element | 한글명 | Type | Required | Length | Description |
|---|---|---|---|---|---|
| content-type | 컨텐츠타입 | string | Y | 40 | application/json; charset=utf-8 |
| authorization | 접근토큰 | string | Y | 350 | OAuth 토큰이 필요한 API 경우 발급한 Access token <br>일반고객(Access token 유효기간 1일, OAuth 2.0의 Client Credentials Grant 절차를 준용) <br>법인(Access token 유효기간 3개월, Refresh token 유효기간 1년, OAuth 2.0의 Authorization Code Grant 절차를 준용) |
| appkey | 앱키 | string | Y | 36 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| appsecret | 앱시크릿키 | string | Y | 180 | 한국투자증권 홈페이지에서 발급받은 appkey (절대 노출되지 않도록 주의해주세요.) |
| personalseckey | 고객식별키 | string | N | 180 | [법인 필수] 제휴사 회원 관리를 위한 고객식별키 |
| tr_id | 거래ID | string | Y | 13 | FHPST01390000 |
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
| FID_DIV_CLS_CODE | FID 분류 구분 코드 | string | Y | 2 | 0:전체 1:상승 2:하락 |
| FID_COND_SCR_DIV_CODE | FID 조건 화면 분류 코드 | string | Y | 5 | 20139 |
| FID_MRKT_CLS_CODE | FID 시장 구분 코드 | string | Y | 2 | 0:전체 K:거래소 Q:코스닥 |
| FID_INPUT_ISCD | FID 입력 종목코드 | string | Y | 12 |  |
| FID_RANK_SORT_CLS_CODE | FID 순위 정렬 구분 코드 | string | Y | 2 | 0:전체1:정적2:동적3:정적&동적 |
| FID_INPUT_DATE_1 | FID 입력 날짜1 | string | Y | 10 | 영업일 |
| FID_TRGT_CLS_CODE | FID 대상 구분 코드 | string | Y | 32 |  |
| FID_TRGT_EXLS_CLS_CODE | FID 대상 제외 구분 코드 | string | Y | 32 |  |

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
| output | 응답상세 | object | Y |  |  |
| hts_kor_isnm | HTS 한글 종목명 | string | Y | 40 |  |
| mksc_shrn_iscd | 유가증권 단축 종목코드 | string | Y | 9 |  |
| vi_cls_code | VI발동상태 | string | Y | 1 | Y: 발동 / N: 해제 |
| bsop_date | 영업 일자 | string | Y | 8 |  |
| cntg_vi_hour | VI발동시간 | string | Y | 6 | VI발동시간 |
| vi_cncl_hour | VI해제시간 | string | Y | 6 | VI해제시간 |
| vi_kind_code | VI종류코드 | string | Y | 1 | 1:정적 2:동적 3:정적&동적 |
| vi_prc | VI발동가격 | string | Y | 10 |  |
| vi_stnd_prc | 정적VI발동기준가격 | string | Y | 10 |  |
| vi_dprt | 정적VI발동괴리율 | string | Y | 82 | % |
| vi_dmc_stnd_prc | 동적VI발동기준가격 | string | Y | 10 |  |
| vi_dmc_dprt | 동적VI발동괴리율 | string | Y | 82 | % |
| vi_count | VI발동횟수 | string | Y | 7 |  |

## Request Example

```json
{
  "fid_cond_scr_div_code": "20139",
  "fid_mrkt_cls_code": "0",
  "fid_input_iscd": "",
  "fid_rank_sort_cls_code": "0",
  "fid_input_date_1": "20240126",
  "fid_trgt_cls_code": "",
  "fid_trgt_exls_cls_code": "",
  "fid_div_cls_code": "0"
}
```

## Response Example

```json
{
  "output": [
    {
      "hts_kor_isnm": "KODEX Fn멀티팩터",
      "mksc_shrn_iscd": "337120",
      "vi_cls_code": "N",
      "bsop_date": "20240126",
      "cntg_vi_hour": "174012",
      "vi_cncl_hour": "174212",
      "vi_kind_code": "2",
      "vi_prc": "12135",
      "vi_stnd_prc": "0",
      "vi_dprt": "0.00",
      "vi_dmc_stnd_prc": "13275",
      "vi_dmc_dprt": "-8.59",
      "vi_count": "2"
    },
    {
      "hts_kor_isnm": "루멘스",
      "mksc_shrn_iscd": "038060",
      "vi_cls_code": "N",
      "bsop_date": "20240126",
      "cntg_vi_hour": "174008",
      "vi_cncl_hour": "174210",
      "vi_kind_code": "2",
      "vi_prc": "1337",
      "vi_stnd_prc": "0",
      "vi_dprt": "0.00",
      "vi_dmc_stnd_prc": "1241",
      "vi_dmc_dprt": "7.74",
      "vi_count": "1"
    },
    {
      "hts_kor_isnm": "DL건설",
      "mksc_shrn_iscd": "001880",
      "vi_cls_code": "N",
      "bsop_date": "20240126",
      "cntg_vi_hour": "173030",
      "vi_cncl_hour": "173234",
      "vi_kind_code": "2",
      "vi_prc": "14000",
      "vi_stnd_prc": "0",
      "vi_dprt": "0.00",
      "vi_dmc_stnd_prc": "14990",
      "vi_dmc_dprt": "-6.60",
      "vi_count": "2"
    },
    "... (27 more items omitted)"
  ],
  "rt_cd": "0",
  "msg_cd": "MCA00000",
  "msg1": "정상처리 되었습니다."
}
```
