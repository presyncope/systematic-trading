# 한국투자증권 Open API 문서 색인

원본: KIS 개발자 포털 전체문서 export (`한국투자증권_오픈API_전체문서_20260920_030008.xlsx`), `scripts/convert_kis_docs.py`로 변환. API 338개, 각 API의 헤더/파라미터/응답 필드/예제는 링크된 파일 참조.

- 실전 REST: `https://openapi.koreainvestment.com:9443` / 모의: `https://openapivts.koreainvestment.com:29443`
- 실전 WebSocket: `ws://ops.koreainvestment.com:21000` / 모의: `ws://ops.koreainvestment.com:31000` (실시간 API 대부분은 모의투자 미지원)
- 인증(`/oauth2/*`)을 제외한 모든 REST 호출은 `authorization: Bearer <access_token>`, `appkey`, `appsecret`, `tr_id` 헤더 필요 (토큰 발급: [oauth/tokenP.md](oauth/tokenP.md), 웹소켓 접속키: [oauth/Approval.md](oauth/Approval.md))
- `모의 TR_ID`가 `모의투자 미지원`이면 모의투자 도메인에서 호출 불가

## OAuth인증

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 실시간 (웹소켓) 접속키 발급 |  |  | POST | [/oauth2/Approval](oauth/Approval.md) |
| 접근토큰폐기(P) |  |  | POST | [/oauth2/revokeP](oauth/revokeP.md) |
| 접근토큰발급(P) |  |  | POST | [/oauth2/tokenP](oauth/tokenP.md) |

## [국내주식] 주문/계좌

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 기간별계좌권리현황조회 | CTRGA011R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/period-rights](domestic-stock/trading/period-rights.md) |
| 투자계좌자산현황조회 | CTRP6548R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/inquire-account-balance](domestic-stock/trading/inquire-account-balance.md) |
| 퇴직연금 예수금조회 | TTTC0506R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/pension/inquire-deposit](domestic-stock/trading/pension/inquire-deposit.md) |
| 주식예약주문정정취소 | (예약취소) CTSC0009U (예약정정) CTSC0013U | 모의투자 미지원 | POST | [/uapi/domestic-stock/v1/trading/order-resv-rvsecncl](domestic-stock/trading/order-resv-rvsecncl.md) |
| 신용매수가능조회 | TTTC8909R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/inquire-credit-psamount](domestic-stock/trading/inquire-credit-psamount.md) |
| 주식통합증거금 현황 | TTTC0869R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/intgr-margin](domestic-stock/trading/intgr-margin.md) |
| 퇴직연금 미체결내역 | TTTC2201R(기존 KRX만 가능), TTTC2210R (KRX,NXT/SOR) | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/pension/inquire-daily-ccld](domestic-stock/trading/pension/inquire-daily-ccld.md) |
| 기간별매매손익현황조회 | TTTC8715R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/inquire-period-trade-profit](domestic-stock/trading/inquire-period-trade-profit.md) |
| 주식주문(정정취소) | TTTC0013U | VTTC0013U | POST | [/uapi/domestic-stock/v1/trading/order-rvsecncl](domestic-stock/trading/order-rvsecncl.md) |
| 주식예약주문조회 | CTSC0004R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/order-resv-ccnl](domestic-stock/trading/order-resv-ccnl.md) |
| 퇴직연금 매수가능조회 | TTTC0503R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/pension/inquire-psbl-order](domestic-stock/trading/pension/inquire-psbl-order.md) |
| 주식잔고조회 | TTTC8434R | VTTC8434R | GET | [/uapi/domestic-stock/v1/trading/inquire-balance](domestic-stock/trading/inquire-balance.md) |
| 퇴직연금 체결기준잔고 | TTTC2202R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/pension/inquire-present-balance](domestic-stock/trading/pension/inquire-present-balance.md) |
| 매수가능조회 | TTTC8908R | VTTC8908R | GET | [/uapi/domestic-stock/v1/trading/inquire-psbl-order](domestic-stock/trading/inquire-psbl-order.md) |
| 기간별손익일별합산조회 | TTTC8708R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/inquire-period-profit](domestic-stock/trading/inquire-period-profit.md) |
| 주식주문(현금) | (매도) TTTC0011U (매수) TTTC0012U | (매도) VTTC0011U (매수) VTTC0012U | POST | [/uapi/domestic-stock/v1/trading/order-cash](domestic-stock/trading/order-cash.md) |
| 매도가능수량조회 | TTTC8408R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/inquire-psbl-sell](domestic-stock/trading/inquire-psbl-sell.md) |
| 주식일별주문체결조회 | (3개월이내) TTTC0081R (3개월이전) CTSC9215R | (3개월이내) VTTC0081R (3개월이전) VTSC9215R | GET | [/uapi/domestic-stock/v1/trading/inquire-daily-ccld](domestic-stock/trading/inquire-daily-ccld.md) |
| 주식정정취소가능주문조회 | TTTC0084R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl](domestic-stock/trading/inquire-psbl-rvsecncl.md) |
| 주식예약주문 | CTSC0008U | 모의투자 미지원 | POST | [/uapi/domestic-stock/v1/trading/order-resv](domestic-stock/trading/order-resv.md) |
| 주식주문(신용) | (매도) TTTC0051U (매수) TTTC0052U | 모의투자 미지원 | POST | [/uapi/domestic-stock/v1/trading/order-credit](domestic-stock/trading/order-credit.md) |
| 퇴직연금 잔고조회 | TTTC2208R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/pension/inquire-balance](domestic-stock/trading/pension/inquire-balance.md) |
| 주식잔고조회_실현손익 | TTTC8494R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/trading/inquire-balance-rlz-pl](domestic-stock/trading/inquire-balance-rlz-pl.md) |

## [국내주식] 기본시세

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 주식현재가 일자별 | FHKST01010400 | FHKST01010400 | GET | [/uapi/domestic-stock/v1/quotations/inquire-daily-price](domestic-stock/quotations/inquire-daily-price.md) |
| 주식현재가 시세 | FHKST01010100 | FHKST01010100 | GET | [/uapi/domestic-stock/v1/quotations/inquire-price](domestic-stock/quotations/inquire-price.md) |
| 국내주식 시간외현재가 | FHPST02300000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-overtime-price](domestic-stock/quotations/inquire-overtime-price.md) |
| ETF 구성종목시세 | FHKST121600C0 | 모의투자 미지원 | GET | [/uapi/etfetn/v1/quotations/inquire-component-stock-price](etfetn/quotations/inquire-component-stock-price.md) |
| 주식현재가 시간외시간별체결 | FHPST02310000 | FHPST02310000 | GET | [/uapi/domestic-stock/v1/quotations/inquire-time-overtimeconclusion](domestic-stock/quotations/inquire-time-overtimeconclusion.md) |
| NAV 비교추이(종목) | FHPST02440000 | 모의투자 미지원 | GET | [/uapi/etfetn/v1/quotations/nav-comparison-trend](etfetn/quotations/nav-comparison-trend.md) |
| 주식현재가 시간외일자별주가 | FHPST02320000 | FHPST02320000 | GET | [/uapi/domestic-stock/v1/quotations/inquire-daily-overtimeprice](domestic-stock/quotations/inquire-daily-overtimeprice.md) |
| 국내주식 시간외호가 | FHPST02300400 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-overtime-asking-price](domestic-stock/quotations/inquire-overtime-asking-price.md) |
| 주식현재가 당일시간대별체결 | FHPST01060000 | FHPST01060000 | GET | [/uapi/domestic-stock/v1/quotations/inquire-time-itemconclusion](domestic-stock/quotations/inquire-time-itemconclusion.md) |
| 주식현재가 시세2 | FHPST01010000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-price-2](domestic-stock/quotations/inquire-price-2.md) |
| ETF 현재가 호가 | FHPST02400200 |  | GET | [/uapi/etfetn/v1/quotations/inquire-asking-price](etfetn/quotations/inquire-asking-price.md) |
| 주식일별분봉조회 | FHKST03010230 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice](domestic-stock/quotations/inquire-time-dailychartprice.md) |
| 국내주식기간별시세(일/주/월/년) | FHKST03010100 | FHKST03010100 | GET | [/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice](domestic-stock/quotations/inquire-daily-itemchartprice.md) |
| NAV 비교추이(일) | FHPST02440200 | 모의투자 미지원 | GET | [/uapi/etfetn/v1/quotations/nav-comparison-daily-trend](etfetn/quotations/nav-comparison-daily-trend.md) |
| 주식현재가 호가/예상체결 | FHKST01010200 | FHKST01010200 | GET | [/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn](domestic-stock/quotations/inquire-asking-price-exp-ccn.md) |
| 주식현재가 체결 | FHKST01010300 | FHKST01010300 | GET | [/uapi/domestic-stock/v1/quotations/inquire-ccnl](domestic-stock/quotations/inquire-ccnl.md) |
| 주식현재가 회원사 | FHKST01010600 | FHKST01010600 | GET | [/uapi/domestic-stock/v1/quotations/inquire-member](domestic-stock/quotations/inquire-member.md) |
| NAV 비교추이(분) | FHPST02440100 | 모의투자 미지원 | GET | [/uapi/etfetn/v1/quotations/nav-comparison-time-trend](etfetn/quotations/nav-comparison-time-trend.md) |
| 주식현재가 투자자 | FHKST01010900 | FHKST01010900 | GET | [/uapi/domestic-stock/v1/quotations/inquire-investor](domestic-stock/quotations/inquire-investor.md) |
| ETF/ETN 현재가 | FHPST02400000 | 모의투자 미지원 | GET | [/uapi/etfetn/v1/quotations/inquire-price](etfetn/quotations/inquire-price.md) |
| 국내주식 장마감 예상체결가 | FHKST117300C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/exp-closing-price](domestic-stock/quotations/exp-closing-price.md) |
| 주식당일분봉조회 | FHKST03010200 | FHKST03010200 | GET | [/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice](domestic-stock/quotations/inquire-time-itemchartprice.md) |

## [국내주식] ELW 시세

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| ELW 현재가 시세 | FHKEW15010000 | FHKEW15010000 | GET | [/uapi/domestic-stock/v1/quotations/inquire-elw-price](domestic-stock/quotations/inquire-elw-price.md) |
| ELW 신규상장종목 | FHKEW154800C0 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/newly-listed](elw/quotations/newly-listed.md) |
| ELW 투자지표추이(일별) | FHPEW02740200 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/indicator-trend-daily](elw/quotations/indicator-trend-daily.md) |
| ELW 민감도 순위 | FHPEW02850000 | 모의투자 미지원 | GET | [/uapi/elw/v1/ranking/sensitivity](elw/ranking/sensitivity.md) |
| ELW 기초자산별 종목시세 | FHKEW154101C0 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/udrl-asset-price](elw/quotations/udrl-asset-price.md) |
| ELW 종목검색 | FHKEW15100000 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/cond-search](elw/quotations/cond-search.md) |
| ELW 변동성 추이(분별) | FHPEW02840300 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/volatility-trend-minute](elw/quotations/volatility-trend-minute.md) |
| ELW 변동성추이(체결) | FHPEW02840100 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/volatility-trend-ccnl](elw/quotations/volatility-trend-ccnl.md) |
| ELW 당일급변종목 | FHPEW02870000 | 모의투자 미지원 | GET | [/uapi/elw/v1/ranking/quick-change](elw/ranking/quick-change.md) |
| ELW 투자지표추이(분별) | FHPEW02740300 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/indicator-trend-minute](elw/quotations/indicator-trend-minute.md) |
| ELW 기초자산 목록조회 | FHKEW154100C0 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/udrl-asset-list](elw/quotations/udrl-asset-list.md) |
| ELW 변동성 추이(일별) | FHPEW02840200 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/volatility-trend-daily](elw/quotations/volatility-trend-daily.md) |
| ELW 거래량순위 | FHPEW02780000 | 모의투자 미지원 | GET | [/uapi/elw/v1/ranking/volume-rank](elw/ranking/volume-rank.md) |
| ELW 지표순위 | FHPEW02790000 | 모의투자 미지원 | GET | [/uapi/elw/v1/ranking/indicator](elw/ranking/indicator.md) |
| ELW 투자지표추이(체결) | FHPEW02740100 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/indicator-trend-ccnl](elw/quotations/indicator-trend-ccnl.md) |
| ELW 상승률순위 | FHPEW02770000 | 모의투자 미지원 | GET | [/uapi/elw/v1/ranking/updown-rate](elw/ranking/updown-rate.md) |
| ELW 민감도 추이(일별) | FHPEW02830200 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/sensitivity-trend-daily](elw/quotations/sensitivity-trend-daily.md) |
| ELW 비교대상종목조회 | FHKEW151701C0 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/compare-stocks](elw/quotations/compare-stocks.md) |
| ELW 만기예정/만기종목 | FHKEW154700C0 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/expiration-stocks](elw/quotations/expiration-stocks.md) |
| ELW LP매매추이 | FHPEW03760000 |  | GET | [/uapi/elw/v1/quotations/lp-trade-trend](elw/quotations/lp-trade-trend.md) |
| ELW 민감도 추이(체결) | FHPEW02830100 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/sensitivity-trend-ccnl](elw/quotations/sensitivity-trend-ccnl.md) |
| ELW 변동성 추이(틱) | FHPEW02840400 | 모의투자 미지원 | GET | [/uapi/elw/v1/quotations/volatility-trend-tick](elw/quotations/volatility-trend-tick.md) |

## [국내주식] 업종/기타

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 국내주식 예상체결지수 추이 | FHPST01840000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/exp-index-trend](domestic-stock/quotations/exp-index-trend.md) |
| 국내주식업종기간별시세(일/주/월/년) | FHKUP03500100 | FHKUP03500100 | GET | [/uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice](domestic-stock/quotations/inquire-daily-indexchartprice.md) |
| 국내업종 시간별지수(분) | FHPUP02110200 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-index-timeprice](domestic-stock/quotations/inquire-index-timeprice.md) |
| 국내업종 구분별전체시세 | FHPUP02140000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-index-category-price](domestic-stock/quotations/inquire-index-category-price.md) |
| 업종 분봉조회 | FHKUP03500200 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-time-indexchartprice](domestic-stock/quotations/inquire-time-indexchartprice.md) |
| 국내휴장일조회 | CTCA0903R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/chk-holiday](domestic-stock/quotations/chk-holiday.md) |
| 국내주식 예상체결 전체지수 | FHKUP11750000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/exp-total-index](domestic-stock/quotations/exp-total-index.md) |
| 국내업종 현재지수 | FHPUP02100000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-index-price](domestic-stock/quotations/inquire-index-price.md) |
| 국내선물 영업일조회 | HHMCM000002C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/market-time](domestic-stock/quotations/market-time.md) |
| 국내업종 시간별지수(초) | FHPUP02110100 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-index-tickprice](domestic-stock/quotations/inquire-index-tickprice.md) |
| 국내업종 일자별지수 | FHPUP02120000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-index-daily-price](domestic-stock/quotations/inquire-index-daily-price.md) |
| 금리 종합(국내채권/금리) | (구) FHPST07020000 (신)HHPST070200C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/comp-interest](domestic-stock/quotations/comp-interest.md) |
| 변동성완화장치(VI) 현황 | FHPST01390000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-vi-status](domestic-stock/quotations/inquire-vi-status.md) |
| 종합 시황/공시(제목) | FHKST01011800 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/news-title](domestic-stock/quotations/news-title.md) |

## [국내주식] 종목정보

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 상품기본조회 | CTPF1604R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/search-info](domestic-stock/quotations/search-info.md) |
| 예탁원정보(상장정보일정) | HHKDB669107C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ksdinfo/list-info](domestic-stock/ksdinfo/list-info.md) |
| 예탁원정보(공모주청약일정) | HHKDB669108C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ksdinfo/pub-offer](domestic-stock/ksdinfo/pub-offer.md) |
| 국내주식 재무비율 | FHKST66430300 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/finance/financial-ratio](domestic-stock/finance/financial-ratio.md) |
| 예탁원정보(자본감소일정) | HHKDB669106C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ksdinfo/cap-dcrs](domestic-stock/ksdinfo/cap-dcrs.md) |
| 예탁원정보(무상증자일정) | HHKDB669101C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ksdinfo/bonus-issue](domestic-stock/ksdinfo/bonus-issue.md) |
| 국내주식 증권사별 투자의견 | FHKST663400C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/invest-opbysec](domestic-stock/quotations/invest-opbysec.md) |
| 국내주식 당사 신용가능종목 | FHPST04770000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/credit-by-company](domestic-stock/quotations/credit-by-company.md) |
| 예탁원정보(주식매수청구일정) | HHKDB669103C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ksdinfo/purreq](domestic-stock/ksdinfo/purreq.md) |
| 예탁원정보(액면교체일정) | HHKDB669105C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ksdinfo/rev-split](domestic-stock/ksdinfo/rev-split.md) |
| 예탁원정보(배당일정) | HHKDB669102C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ksdinfo/dividend](domestic-stock/ksdinfo/dividend.md) |
| 국내주식 종목투자의견 | FHKST663300C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/invest-opinion](domestic-stock/quotations/invest-opinion.md) |
| 국내주식 안정성비율 | FHKST66430600 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/finance/stability-ratio](domestic-stock/finance/stability-ratio.md) |
| 국내주식 수익성비율 | FHKST66430400 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/finance/profit-ratio](domestic-stock/finance/profit-ratio.md) |
| 예탁원정보(실권주일정) | HHKDB669109C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ksdinfo/forfeit](domestic-stock/ksdinfo/forfeit.md) |
| 예탁원정보(의무예치일정) | HHKDB669110C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ksdinfo/mand-deposit](domestic-stock/ksdinfo/mand-deposit.md) |
| 국내주식 손익계산서 | FHKST66430200 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/finance/income-statement](domestic-stock/finance/income-statement.md) |
| 당사 대주가능 종목 | CTSC2702R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/lendable-by-company](domestic-stock/quotations/lendable-by-company.md) |
| 주식기본조회 | CTPF1002R | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/search-stock-info](domestic-stock/quotations/search-stock-info.md) |
| 예탁원정보(유상증자일정) | HHKDB669100C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ksdinfo/paidin-capin](domestic-stock/ksdinfo/paidin-capin.md) |
| 예탁원정보(주주총회일정) | HHKDB669111C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ksdinfo/sharehld-meet](domestic-stock/ksdinfo/sharehld-meet.md) |
| 국내주식 성장성비율 | FHKST66430800 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/finance/growth-ratio](domestic-stock/finance/growth-ratio.md) |
| 국내주식 대차대조표 | FHKST66430100 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/finance/balance-sheet](domestic-stock/finance/balance-sheet.md) |
| 예탁원정보(합병/분할일정) | HHKDB669104C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ksdinfo/merger-split](domestic-stock/ksdinfo/merger-split.md) |
| 국내주식 종목추정실적 | HHKST668300C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/estimate-perform](domestic-stock/quotations/estimate-perform.md) |
| 국내주식 기타주요비율 | FHKST66430500 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/finance/other-major-ratios](domestic-stock/finance/other-major-ratios.md) |

## [국내주식] 시세분석

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 프로그램매매 종합현황(시간) | FHPPG04600101 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/comp-program-trade-today](domestic-stock/quotations/comp-program-trade-today.md) |
| 국내주식 신용잔고 일별추이 | FHPST04760000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/daily-credit-balance](domestic-stock/quotations/daily-credit-balance.md) |
| 시장별 투자자매매동향(일별) | FHPTJ04040000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-investor-daily-by-market](domestic-stock/quotations/inquire-investor-daily-by-market.md) |
| 국내주식 공매도 일별추이 | FHPST04830000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/daily-short-sale](domestic-stock/quotations/daily-short-sale.md) |
| 종목별 투자자매매동향(일별) | FHPTJ04160001 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/investor-trade-by-stock-daily](domestic-stock/quotations/investor-trade-by-stock-daily.md) |
| 종목조건검색 목록조회 | HHKST03900300 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/psearch-title](domestic-stock/quotations/psearch-title.md) |
| 국내주식 상하한가 포착 | FHKST130000C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/capture-uplowprice](domestic-stock/quotations/capture-uplowprice.md) |
| 프로그램매매 종합현황(일별) | FHPPG04600001 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/comp-program-trade-daily](domestic-stock/quotations/comp-program-trade-daily.md) |
| 종목별 일별 대차거래추이 | HHPST074500C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/daily-loan-trans](domestic-stock/quotations/daily-loan-trans.md) |
| 종목조건검색조회 | HHKST03900400 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/psearch-result](domestic-stock/quotations/psearch-result.md) |
| 국내주식 매물대/거래비중 | FHPST01130000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/pbar-tratio](domestic-stock/quotations/pbar-tratio.md) |
| 국내기관_외국인 매매종목가집계 | FHPTJ04400000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/foreign-institution-total](domestic-stock/quotations/foreign-institution-total.md) |
| 관심종목 그룹별 종목조회 | HHKCM113004C6 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/intstock-stocklist-by-group](domestic-stock/quotations/intstock-stocklist-by-group.md) |
| 주식현재가 회원사 종목매매동향 | FHPST04540000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-member-daily](domestic-stock/quotations/inquire-member-daily.md) |
| 종목별 프로그램매매추이(일별) | FHPPG04650201 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/program-trade-by-stock-daily](domestic-stock/quotations/program-trade-by-stock-daily.md) |
| 관심종목 그룹조회 | HHKCM113004C7 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/intstock-grouplist](domestic-stock/quotations/intstock-grouplist.md) |
| 종목별 외인기관 추정가집계 | HHPTJ04160200 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/investor-trend-estimate](domestic-stock/quotations/investor-trend-estimate.md) |
| 종목별일별매수매도체결량 | FHKST03010800 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-daily-trade-volume](domestic-stock/quotations/inquire-daily-trade-volume.md) |
| 국내주식 체결금액별 매매비중 | FHKST111900C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/tradprt-byamt](domestic-stock/quotations/tradprt-byamt.md) |
| 프로그램매매 투자자매매동향(당일) | HHPPG046600C1 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/investor-program-trade-today](domestic-stock/quotations/investor-program-trade-today.md) |
| 국내 증시자금 종합 | FHKST649100C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/mktfunds](domestic-stock/quotations/mktfunds.md) |
| 국내주식 예상체결가 추이 | FHPST01810000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/exp-price-trend](domestic-stock/quotations/exp-price-trend.md) |
| 회원사 실시간 매매동향(틱) | FHPST04320000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/frgnmem-trade-trend](domestic-stock/quotations/frgnmem-trade-trend.md) |
| 시장별 투자자매매동향(시세) | FHPTJ04030000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/inquire-investor-time-by-market](domestic-stock/quotations/inquire-investor-time-by-market.md) |
| 종목별 프로그램매매추이(체결) | FHPPG04650101 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/program-trade-by-stock](domestic-stock/quotations/program-trade-by-stock.md) |
| 외국계 매매종목 가집계 | FHKST644100C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/frgnmem-trade-estimate](domestic-stock/quotations/frgnmem-trade-estimate.md) |
| 국내주식 시간외예상체결등락률 | FHKST11860000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/overtime-exp-trans-fluct](domestic-stock/ranking/overtime-exp-trans-fluct.md) |
| 종목별 외국계 순매수추이 | FHKST644400C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/frgnmem-pchs-trend](domestic-stock/quotations/frgnmem-pchs-trend.md) |
| 관심종목(멀티종목) 시세조회 | FHKST11300006 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/intstock-multprice](domestic-stock/quotations/intstock-multprice.md) |

## [국내주식] 순위분석

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 국내주식 예상체결 상승/하락상위 | FHPST01820000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/exp-trans-updown](domestic-stock/ranking/exp-trans-updown.md) |
| 국내주식 호가잔량 순위 | FHPST01720000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/quote-balance](domestic-stock/ranking/quote-balance.md) |
| 국내주식 신용잔고 상위 | FHKST17010000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/credit-balance](domestic-stock/ranking/credit-balance.md) |
| 국내주식 시간외거래량순위 | FHPST02350000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/overtime-volume](domestic-stock/ranking/overtime-volume.md) |
| 국내주식 배당률 상위 | HHKDB13470100 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/dividend-rate](domestic-stock/ranking/dividend-rate.md) |
| 국내주식 시간외잔량 순위 | FHPST01760000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/after-hour-balance](domestic-stock/ranking/after-hour-balance.md) |
| 국내주식 공매도 상위종목 | FHPST04820000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/short-sale](domestic-stock/ranking/short-sale.md) |
| 국내주식 이격도 순위 | FHPST01780000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/disparity](domestic-stock/ranking/disparity.md) |
| HTS조회상위20종목 | HHMCM000100C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/hts-top-view](domestic-stock/ranking/hts-top-view.md) |
| 거래량순위 | FHPST01710000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/quotations/volume-rank](domestic-stock/quotations/volume-rank.md) |
| 국내주식 수익자산지표 순위 | FHPST01730000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/profit-asset-index](domestic-stock/ranking/profit-asset-index.md) |
| 국내주식 신고/신저근접종목 상위 | FHPST01870000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/near-new-highlow](domestic-stock/ranking/near-new-highlow.md) |
| 국내주식 우선주/괴리율 상위 | FHPST01770000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/prefer-disparate-ratio](domestic-stock/ranking/prefer-disparate-ratio.md) |
| 국내주식 대량체결건수 상위 | FHKST190900C0 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/bulk-trans-num](domestic-stock/ranking/bulk-trans-num.md) |
| 국내주식 재무비율 순위 | FHPST01750000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/finance-ratio](domestic-stock/ranking/finance-ratio.md) |
| 국내주식 시가총액 상위 | FHPST01740000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/market-cap](domestic-stock/ranking/market-cap.md) |
| 국내주식 당사매매종목 상위 | FHPST01860000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/traded-by-company](domestic-stock/ranking/traded-by-company.md) |
| 국내주식 등락률 순위 | FHPST01700000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/fluctuation](domestic-stock/ranking/fluctuation.md) |
| 국내주식 시장가치 순위 | FHPST01790000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/market-value](domestic-stock/ranking/market-value.md) |
| 국내주식 관심종목등록 상위 | FHPST01800000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/top-interest-stock](domestic-stock/ranking/top-interest-stock.md) |
| 국내주식 체결강도 상위 | FHPST01680000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/volume-power](domestic-stock/ranking/volume-power.md) |
| 국내주식 시간외등락율순위 | FHPST02340000 | 모의투자 미지원 | GET | [/uapi/domestic-stock/v1/ranking/overtime-fluctuation](domestic-stock/ranking/overtime-fluctuation.md) |

## [국내주식] 실시간시세

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 국내지수 실시간예상체결 | H0UPANC0 | 모의투자 미지원 | POST | [/tryitout/H0UPANC0](websocket/H0UPANC0.md) |
| 국내주식 장운영정보 (통합) | H0UNMKO0 | 모의투자 미지원 | POST | [/tryitout/H0UNMKO0](websocket/H0UNMKO0.md) |
| 국내주식 실시간회원사 (NXT) | H0NXMBC0 | 모의투자 미지원 | POST | [/tryitout/H0NXMBC0](websocket/H0NXMBC0.md) |
| 국내주식 실시간체결통보 | H0STCNI0 | H0STCNI9 | POST | [/tryitout/H0STCNI0](websocket/H0STCNI0.md) |
| 국내주식 시간외 실시간예상체결 (KRX) | H0STOAC0 | 모의투자 미지원 | POST | [/tryitout/H0STOAC0](websocket/H0STOAC0.md) |
| 국내주식 VI변동성완화장치 | H0STVIC0 |  | POST | [/tryitout/H0STVIC0](websocket/H0STVIC0.md) |
| 국내주식 시간외 실시간호가 (KRX) | H0STOAA0 | 모의투자 미지원 | POST | [/tryitout/H0STOAA0](websocket/H0STOAA0.md) |
| 국내주식 실시간프로그램매매 (통합) | H0UNPGM0 | 모의투자 미지원 | POST | [/tryitout/H0UNPGM0](websocket/H0UNPGM0.md) |
| 국내주식 실시간호가 (통합) | H0UNASP0 | 모의투자 미지원 | POST | [/tryitout/H0UNASP0](websocket/H0UNASP0.md) |
| 국내주식 실시간프로그램매매 (KRX) | H0STPGM0 | 모의투자 미지원 | POST | [/tryitout/H0STPGM0](websocket/H0STPGM0.md) |
| 국내주식 장운영정보 (KRX) | H0STMKO0 | 모의투자 미지원 | POST | [/tryitout/H0STMKO0](websocket/H0STMKO0.md) |
| 국내주식 실시간체결가 (KRX) | H0STCNT0 | H0STCNT0 | POST | [/tryitout/H0STCNT0](websocket/H0STCNT0.md) |
| 국내지수 실시간프로그램매매 | H0UPPGM0 | 모의투자 미지원 | POST | [/tryitout/H0UPPGM0](websocket/H0UPPGM0.md) |
| VI변동성완화 (통합) | H0UNVIC0 |  | POST | [/tryitout/H0UNVIC0](websocket/H0UNVIC0.md) |
| 국내주식 실시간회원사 (통합) | H0UNMBC0 | 모의투자 미지원 | POST | [/tryitout/H0UNMBC0](websocket/H0UNMBC0.md) |
| 국내지수 실시간체결 | H0UPCNT0 | 모의투자 미지원 | POST | [/tryitout/H0UPCNT0](websocket/H0UPCNT0.md) |
| 국내주식 실시간예상체결 (KRX) | H0STANC0 | 모의투자 미지원 | POST | [/tryitout/H0STANC0](websocket/H0STANC0.md) |
| VI변동성완화 (NXT) | H0NXVIC0 |  | POST | [/tryitout/H0NXVIC0](websocket/H0NXVIC0.md) |
| ELW 실시간호가 | H0EWASP0 | 모의투자 미지원 | POST | [/tryitout/H0EWASP0](websocket/H0EWASP0.md) |
| 국내주식 실시간호가 (KRX) | H0STASP0 | H0STASP0 | POST | [/tryitout/H0STASP0](websocket/H0STASP0.md) |
| 국내주식 실시간체결가 (통합) | H0UNCNT0 | 모의투자 미지원 | POST | [/tryitout/H0UNCNT0](websocket/H0UNCNT0.md) |
| 국내주식 실시간호가 (NXT) | H0NXASP0 | 모의투자 미지원 | POST | [/tryitout/H0NXASP0](websocket/H0NXASP0.md) |
| 국내주식 실시간프로그램매매 (NXT) | H0NXPGM0 | 모의투자 미지원 | POST | [/tryitout/H0NXPGM0](websocket/H0NXPGM0.md) |
| 국내주식 실시간체결가 (NXT) | H0NXCNT0 | 모의투자 미지원 | POST | [/tryitout/H0NXCNT0](websocket/H0NXCNT0.md) |
| ELW 실시간체결가 | H0EWCNT0 | 모의투자 미지원 | POST | [/tryitout/H0EWCNT0](websocket/H0EWCNT0.md) |
| ELW 실시간예상체결 | H0EWANC0 | 모의투자 미지원 | POST | [/tryitout/H0EWANC0](websocket/H0EWANC0.md) |
| 국내주식 실시간예상체결 (NXT) | H0NXANC0 | 모의투자 미지원 | POST | [/tryitout/H0NXANC0](websocket/H0NXANC0.md) |
| 국내주식 실시간회원사 (KRX) | H0STMBC0 | 모의투자 미지원 | POST | [/tryitout/H0STMBC0](websocket/H0STMBC0.md) |
| 국내주식 실시간예상체결 (통합) | H0UNANC0 | 모의투자 미지원 | POST | [/tryitout/H0UNANC0](websocket/H0UNANC0.md) |
| 국내주식 장운영정보 (NXT) | H0NXMKO0 | 모의투자 미지원 | POST | [/tryitout/H0NXMKO0](websocket/H0NXMKO0.md) |
| 국내ETF NAV추이 | H0STNAV0 | 모의투자 미지원 | POST | [/tryitout/H0STNAV0](websocket/H0STNAV0.md) |
| 국내주식 시간외 실시간체결가 (KRX) | H0STOUP0 | 모의투자 미지원 | POST | [/tryitout/H0STOUP0](websocket/H0STOUP0.md) |

## [국내선물옵션] 주문/계좌

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| (야간)선물옵션 증거금 상세 | (구) JTCE6003R (신) CTFN7107R | 모의투자 미지원 | GET | [/uapi/domestic-futureoption/v1/trading/ngt-margin-detail](domestic-futureoption/trading/ngt-margin-detail.md) |
| 선물옵션 총자산현황 | CTRP6550R | 모의투자 미지원 | GET | [/uapi/domestic-futureoption/v1/trading/inquire-deposit](domestic-futureoption/trading/inquire-deposit.md) |
| 선물옵션기간약정수수료일별 | CTFO6119R | 모의투자 미지원 | GET | [/uapi/domestic-futureoption/v1/trading/inquire-daily-amount-fee](domestic-futureoption/trading/inquire-daily-amount-fee.md) |
| (야간)선물옵션 잔고현황 | (구) JTCE6001R (신) CTFN6118R | 모의투자 미지원 | GET | [/uapi/domestic-futureoption/v1/trading/inquire-ngt-balance](domestic-futureoption/trading/inquire-ngt-balance.md) |
| 선물옵션 잔고현황 | CTFO6118R | VTFO6118R | GET | [/uapi/domestic-futureoption/v1/trading/inquire-balance](domestic-futureoption/trading/inquire-balance.md) |
| 선물옵션 주문 | (주간 매수/매도) TTTO1101U (야간 매수/매도) (구) JTCE1001U (신) STTN1101U | (주간 매수/매도) VTTO1101U (야간은 모의투자 미제공) | POST | [/uapi/domestic-futureoption/v1/trading/order](domestic-futureoption/trading/order.md) |
| 선물옵션 잔고평가손익내역 | CTFO6159R | 모의투자 미지원 | GET | [/uapi/domestic-futureoption/v1/trading/inquire-balance-valuation-pl](domestic-futureoption/trading/inquire-balance-valuation-pl.md) |
| 선물옵션 증거금률 | TTTO6032R | 미지원 | GET | [/uapi/domestic-futureoption/v1/quotations/margin-rate](domestic-futureoption/quotations/margin-rate.md) |
| 선물옵션 정정취소주문 | (주간 정정/취소) TTTO1103U (야간 정정/취소) (구) JTCE1002U (신) STTN1103U | (주간 정정/취소) VTTO1103U (야간은 모의투자 미제공) | POST | [/uapi/domestic-futureoption/v1/trading/order-rvsecncl](domestic-futureoption/trading/order-rvsecncl.md) |
| 선물옵션 주문체결내역조회 | TTTO5201R | VTTO5201R | GET | [/uapi/domestic-futureoption/v1/trading/inquire-ccnl](domestic-futureoption/trading/inquire-ccnl.md) |
| (야간)선물옵션 주문체결 내역조회 | (구) JTCE5005R (신) STTN5201R | 모의투자 미지원 | GET | [/uapi/domestic-futureoption/v1/trading/inquire-ngt-ccnl](domestic-futureoption/trading/inquire-ngt-ccnl.md) |
| (야간)선물옵션 주문가능 조회 | (구) JTCE1004R (신) STTN5105R | 모의투자 미지원 | GET | [/uapi/domestic-futureoption/v1/trading/inquire-psbl-ngt-order](domestic-futureoption/trading/inquire-psbl-ngt-order.md) |
| 선물옵션 잔고정산손익내역 | CTFO6117R | 모의투자 미지원 | GET | [/uapi/domestic-futureoption/v1/trading/inquire-balance-settlement-pl](domestic-futureoption/trading/inquire-balance-settlement-pl.md) |
| 선물옵션 주문가능 | TTTO5105R | VTTO5105R | GET | [/uapi/domestic-futureoption/v1/trading/inquire-psbl-order](domestic-futureoption/trading/inquire-psbl-order.md) |
| 선물옵션 기준일체결내역 | CTFO5139R | 모의투자 미지원 | GET | [/uapi/domestic-futureoption/v1/trading/inquire-ccnl-bstime](domestic-futureoption/trading/inquire-ccnl-bstime.md) |

## [국내선물옵션] 기본시세

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 선물옵션 시세 | FHMIF10000000 | FHMIF10000000 | GET | [/uapi/domestic-futureoption/v1/quotations/inquire-price](domestic-futureoption/quotations/inquire-price.md) |
| 국내선물 기초자산 시세 | FHPIF05030000 | 모의투자 미지원 | GET | [/uapi/domestic-futureoption/v1/quotations/display-board-top](domestic-futureoption/quotations/display-board-top.md) |
| 선물옵션 일중예상체결추이 | FHPIF05110100 | 모의투자 미지원 | GET | [/uapi/domestic-futureoption/v1/quotations/exp-price-trend](domestic-futureoption/quotations/exp-price-trend.md) |
| 선물옵션기간별시세(일/주/월/년) | FHKIF03020100 | FHKIF03020100 | GET | [/uapi/domestic-futureoption/v1/quotations/inquire-daily-fuopchartprice](domestic-futureoption/quotations/inquire-daily-fuopchartprice.md) |
| 선물옵션 분봉조회 | FHKIF03020200 | 모의투자 미지원 | GET | [/uapi/domestic-futureoption/v1/quotations/inquire-time-fuopchartprice](domestic-futureoption/quotations/inquire-time-fuopchartprice.md) |
| 선물옵션 시세호가 | FHMIF10010000 | FHMIF10010000 | GET | [/uapi/domestic-futureoption/v1/quotations/inquire-asking-price](domestic-futureoption/quotations/inquire-asking-price.md) |

## [국내선물옵션] 실시간시세

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 주식옵션 실시간호가 | H0ZOASP0 | 모의투자 미지원 | POST | [/tryitout/H0ZOASP0](websocket/H0ZOASP0.md) |
| 선물옵션 실시간체결통보 | H0IFCNI0 | H0IFCNI9 | POST | [/tryitout/H0IFCNI0](websocket/H0IFCNI0.md) |
| KRX야간선물 실시간종목체결 | H0MFCNT0 | 모의투자 미지원 | POST | [/tryitout/H0MFCNT0](websocket/H0MFCNT0.md) |
| KRX야간선물 실시간호가 | H0MFASP0 | 모의투자 미지원 | POST | [/tryitout/H0MFASP0](websocket/H0MFASP0.md) |
| KRX야간옵션 실시간체결가 | H0EUCNT0 | 모의투자 미지원 | POST | [/tryitout/H0EUCNT0](websocket/H0EUCNT0.md) |
| KRX야간옵션실시간예상체결 | H0EUANC0 | 모의투자 미지원 | POST | [/tryitout/H0EUANC0](websocket/H0EUANC0.md) |
| 지수선물 실시간체결가 | H0IFCNT0 | 모의투자 미지원 | POST | [/tryitout/H0IFCNT0](websocket/H0IFCNT0.md) |
| 주식선물 실시간예상체결 | H0ZFANC0 | 모의투자 미지원 | POST | [/tryitout/H0ZFANC0](websocket/H0ZFANC0.md) |
| KRX야간옵션실시간체결통보 | H0MFCNI0 | 모의투자 미지원 | POST | [/tryitout/H0EUCNI0](websocket/H0EUCNI0.md) |
| KRX야간선물 실시간체결통보 | H0MFCNI0 | 모의투자 미지원 | POST | [/tryitout/H0MFCNI0](websocket/H0MFCNI0.md) |
| 상품선물 실시간체결가 | H0CFCNT0 | 모의투자 미지원 | POST | [/tryitout/H0CFCNT0](websocket/H0CFCNT0.md) |
| 지수선물 실시간호가 | H0IFASP0 | 모의투자 미지원 | POST | [/tryitout/H0IFASP0](websocket/H0IFASP0.md) |
| 지수옵션  실시간체결가 | H0IOCNT0 | 모의투자 미지원 | POST | [/tryitout/H0IOCNT0](websocket/H0IOCNT0.md) |
| KRX야간옵션 실시간호가 | H0EUASP0 | 모의투자 미지원 | POST | [/tryitout/H0EUASP0](websocket/H0EUASP0.md) |
| 상품선물 실시간호가 | H0CFASP0 | 모의투자 미지원 | POST | [/tryitout/H0CFASP0](websocket/H0CFASP0.md) |
| 주식옵션 실시간예상체결 | H0ZOANC0 | 모의투자 미지원 | POST | [/tryitout/H0ZOANC0](websocket/H0ZOANC0.md) |
| 주식선물 실시간호가 | H0ZFASP0 | 모의투자 미지원 | POST | [/tryitout/H0ZFASP0](websocket/H0ZFASP0.md) |
| 주식옵션 실시간체결가 | H0ZOCNT0 | 모의투자 미지원 | POST | [/tryitout/H0ZOCNT0](websocket/H0ZOCNT0.md) |
| 지수옵션 실시간호가 | H0IOASP0 | 모의투자 미지원 | POST | [/tryitout/H0IOASP0](websocket/H0IOASP0.md) |
| 주식선물 실시간체결가 | H0ZFCNT0 | 모의투자 미지원 | POST | [/tryitout/H0ZFCNT0](websocket/H0ZFCNT0.md) |

## [해외주식] 주문/계좌

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 해외주식 잔고 | TTTS3012R | VTTS3012R | GET | [/uapi/overseas-stock/v1/trading/inquire-balance](overseas-stock/trading/inquire-balance.md) |
| 해외주식 체결기준현재잔고 | CTRP6504R | VTRP6504R | GET | [/uapi/overseas-stock/v1/trading/inquire-present-balance](overseas-stock/trading/inquire-present-balance.md) |
| 해외주식 지정가체결내역조회 | TTTS6059R | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/trading/inquire-algo-ccnl](overseas-stock/trading/inquire-algo-ccnl.md) |
| 해외주식 기간손익 | TTTS3039R | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/trading/inquire-period-profit](overseas-stock/trading/inquire-period-profit.md) |
| 해외주식 매수가능금액조회 | TTTS3007R | VTTS3007R | GET | [/uapi/overseas-stock/v1/trading/inquire-psamount](overseas-stock/trading/inquire-psamount.md) |
| 해외주식 정정취소주문 | (미국 정정·취소) TTTT1004U (아시아 국가 하단 규격서 참고) | (미국 정정·취소) VTTT1004U (아시아 국가 하단 규격서 참고) | POST | [/uapi/overseas-stock/v1/trading/order-rvsecncl](overseas-stock/trading/order-rvsecncl.md) |
| 해외주식 예약주문접수 | (미국예약매수) TTTT3014U  (미국예약매도) TTTT3016U   (중국/홍콩/일본/베트남 예약주문) TTTS3013U | (미국예약매수) VTTT3014U  (미국예약매도) VTTT3016U   (중국/홍콩/일본/베트남 예약주문) VTTS3013U | POST | [/uapi/overseas-stock/v1/trading/order-resv](overseas-stock/trading/order-resv.md) |
| 해외주식 미체결내역 | TTTS3018R | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/trading/inquire-nccs](overseas-stock/trading/inquire-nccs.md) |
| 해외주식 미국주간정정취소 | TTTS6038U | 모의투자 미지원 | POST | [/uapi/overseas-stock/v1/trading/daytime-order-rvsecncl](overseas-stock/trading/daytime-order-rvsecncl.md) |
| 해외주식 주문체결내역 | TTTS3035R | VTTS3035R | GET | [/uapi/overseas-stock/v1/trading/inquire-ccnl](overseas-stock/trading/inquire-ccnl.md) |
| 해외주식 결제기준잔고 | CTRP6010R | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/trading/inquire-paymt-stdr-balance](overseas-stock/trading/inquire-paymt-stdr-balance.md) |
| 해외주식 일별거래내역 | CTOS4001R | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/trading/inquire-period-trans](overseas-stock/trading/inquire-period-trans.md) |
| 해외주식 미국주간주문 | (주간매수) TTTS6036U (주간매도) TTTS6037U | 모의투자 미지원 | POST | [/uapi/overseas-stock/v1/trading/daytime-order](overseas-stock/trading/daytime-order.md) |
| 해외주식 예약주문조회 | (미국) TTTT3039R (일본/중국/홍콩/베트남) TTTS3014R | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/trading/order-resv-list](overseas-stock/trading/order-resv-list.md) |
| 해외주식 주문 | (미국매수) TTTT1002U  (미국매도) TTTT1006U (아시아 국가 하단 규격서 참고) | (미국매수) VTTT1002U  (미국매도) VTTT1001U  (아시아 국가 하단 규격서 참고) | POST | [/uapi/overseas-stock/v1/trading/order](overseas-stock/trading/order.md) |
| 해외주식 예약주문접수취소 | (미국 예약주문 취소접수) TTTT3017U (아시아국가 미제공) | (미국 예약주문 취소접수) VTTT3017U (아시아국가 미제공) | POST | [/uapi/overseas-stock/v1/trading/order-resv-ccnl](overseas-stock/trading/order-resv-ccnl.md) |
| 해외주식 지정가주문번호조회 | TTTS6058R | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/trading/algo-ordno](overseas-stock/trading/algo-ordno.md) |
| 해외증거금 통화별조회 | TTTC2101R | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/trading/foreign-margin](overseas-stock/trading/foreign-margin.md) |

## [해외주식] 기본시세

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 해외주식 체결추이 | HHDFS76200300 | 모의투자 미지원 | GET | [/uapi/overseas-price/v1/quotations/inquire-ccnl](overseas-price/quotations/inquire-ccnl.md) |
| 해외주식 기간별시세 | HHDFS76240000 | HHDFS76240000 | GET | [/uapi/overseas-price/v1/quotations/dailyprice](overseas-price/quotations/dailyprice.md) |
| 해외결제일자조회 | CTOS5011R | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/quotations/countries-holiday](overseas-stock/quotations/countries-holiday.md) |
| 해외주식 현재체결가 | HHDFS00000300 | HHDFS00000300 | GET | [/uapi/overseas-price/v1/quotations/price](overseas-price/quotations/price.md) |
| 해외주식 복수종목 시세조회 | HHDFS76220000 | 미지원 | GET | [/uapi/overseas-price/v1/quotations/multprice](overseas-price/quotations/multprice.md) |
| 해외주식조건검색 | HHDFS76410000 | HHDFS76410000 | GET | [/uapi/overseas-price/v1/quotations/inquire-search](overseas-price/quotations/inquire-search.md) |
| 해외주식 상품기본정보 | CTPF1702R | 모의투자 미지원 | GET | [/uapi/overseas-price/v1/quotations/search-info](overseas-price/quotations/search-info.md) |
| 해외지수분봉조회 | FHKST03030200 | 모의투자 미지원 | GET | [/uapi/overseas-price/v1/quotations/inquire-time-indexchartprice](overseas-price/quotations/inquire-time-indexchartprice.md) |
| 해외주식분봉조회 | HHDFS76950200 | 모의투자 미지원 | GET | [/uapi/overseas-price/v1/quotations/inquire-time-itemchartprice](overseas-price/quotations/inquire-time-itemchartprice.md) |
| 해외주식 현재가상세 | HHDFS76200200 | 모의투자 미지원 | GET | [/uapi/overseas-price/v1/quotations/price-detail](overseas-price/quotations/price-detail.md) |
| 해외주식 업종별코드조회 | HHDFS76370100 | 모의투자 미지원 | GET | [/uapi/overseas-price/v1/quotations/industry-price](overseas-price/quotations/industry-price.md) |
| 해외주식 종목/지수/환율기간별시세(일/주/월/년) | FHKST03030100 | FHKST03030100 | GET | [/uapi/overseas-price/v1/quotations/inquire-daily-chartprice](overseas-price/quotations/inquire-daily-chartprice.md) |
| 해외주식 업종별시세 | HHDFS76370000 | 모의투자 미지원 | GET | [/uapi/overseas-price/v1/quotations/industry-theme](overseas-price/quotations/industry-theme.md) |
| 해외주식 현재가 호가 | HHDFS76200100 | 모의투자 미지원 | GET | [/uapi/overseas-price/v1/quotations/inquire-asking-price](overseas-price/quotations/inquire-asking-price.md) |

## [해외주식] 시세분석

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 해외주식 거래증가율순위 | HHDFS76330000 | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/ranking/trade-growth](overseas-stock/ranking/trade-growth.md) |
| 해외주식 기간별권리조회 | CTRGT011R | 모의투자 미지원 | GET | [/uapi/overseas-price/v1/quotations/period-rights](overseas-price/quotations/period-rights.md) |
| 해외주식 가격급등락 | HHDFS76260000 | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/ranking/price-fluct](overseas-stock/ranking/price-fluct.md) |
| 해외주식 거래대금순위 | HHDFS76320010 | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/ranking/trade-pbmn](overseas-stock/ranking/trade-pbmn.md) |
| 해외주식 거래량급증 | HHDFS76270000 | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/ranking/volume-surge](overseas-stock/ranking/volume-surge.md) |
| 해외주식 신고/신저가 | HHDFS76300000 | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/ranking/new-highlow](overseas-stock/ranking/new-highlow.md) |
| 해외주식 매수체결강도상위 | HHDFS76280000 | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/ranking/volume-power](overseas-stock/ranking/volume-power.md) |
| 해외주식 거래회전율순위 | HHDFS76340000 | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/ranking/trade-turnover](overseas-stock/ranking/trade-turnover.md) |
| 해외뉴스종합(제목) | HHPSTH60100C1 | 모의투자 미지원 | GET | [/uapi/overseas-price/v1/quotations/news-title](overseas-price/quotations/news-title.md) |
| 당사 해외주식담보대출 가능 종목 | CTLN4050R | 모의투자 미지원 | GET | [/uapi/overseas-price/v1/quotations/colable-by-company](overseas-price/quotations/colable-by-company.md) |
| 해외주식 시가총액순위 | HHDFS76350100 | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/ranking/market-cap](overseas-stock/ranking/market-cap.md) |
| 해외속보(제목) | FHKST01011801 | 모의투자 미지원 | GET | [/uapi/overseas-price/v1/quotations/brknews-title](overseas-price/quotations/brknews-title.md) |
| 해외주식 상승율/하락율 | HHDFS76290000 | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/ranking/updown-rate](overseas-stock/ranking/updown-rate.md) |
| 해외주식 권리종합 | HHDFS78330900 | 모의투자 미지원 | GET | [/uapi/overseas-price/v1/quotations/rights-by-ice](overseas-price/quotations/rights-by-ice.md) |
| 해외주식 거래량순위 | HHDFS76310010 | 모의투자 미지원 | GET | [/uapi/overseas-stock/v1/ranking/trade-vol](overseas-stock/ranking/trade-vol.md) |

## [해외주식] 실시간시세

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 해외주식 실시간호가 | HDFSASP0 | 모의투자 미지원 | POST | [/tryitout/HDFSASP0](websocket/HDFSASP0.md) |
| 해외주식 지연호가(아시아) | HDFSASP1 | 모의투자 미지원 | POST | [/tryitout/HDFSASP1](websocket/HDFSASP1.md) |
| 해외주식 실시간지연체결가 | HDFSCNT0 | 모의투자 미지원 | POST | [/tryitout/HDFSCNT0](websocket/HDFSCNT0.md) |
| 해외주식 실시간체결통보 | H0GSCNI0 | H0GSCNI9 | POST | [/tryitout/H0GSCNI0](websocket/H0GSCNI0.md) |

## [해외선물옵션] 주문/계좌

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 해외선물옵션 주문 | OTFM3001U | 모의투자 미지원 | POST | [/uapi/overseas-futureoption/v1/trading/order](overseas-futureoption/trading/order.md) |
| 해외선물옵션 정정취소주문 | (정정) OTFM3002U (취소) OTFM3003U | 모의투자 미지원 | POST | [/uapi/overseas-futureoption/v1/trading/order-rvsecncl](overseas-futureoption/trading/order-rvsecncl.md) |
| 해외선물옵션 당일주문내역조회 | OTFM3116R | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/trading/inquire-ccld](overseas-futureoption/trading/inquire-ccld.md) |
| 해외선물옵션 미결제내역조회(잔고) | OTFM1412R | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/trading/inquire-unpd](overseas-futureoption/trading/inquire-unpd.md) |
| 해외선물옵션 주문가능조회 | OTFM3304R | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/trading/inquire-psamount](overseas-futureoption/trading/inquire-psamount.md) |
| 해외선물옵션 기간계좌손익 일별 | OTFM3118R | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/trading/inquire-period-ccld](overseas-futureoption/trading/inquire-period-ccld.md) |
| 해외선물옵션 일별 체결내역 | OTFM3122R | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/trading/inquire-daily-ccld](overseas-futureoption/trading/inquire-daily-ccld.md) |
| 해외선물옵션 예수금현황 | OTFM1411R | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/trading/inquire-deposit](overseas-futureoption/trading/inquire-deposit.md) |
| 해외선물옵션 일별 주문내역 | OTFM3120R | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/trading/inquire-daily-order](overseas-futureoption/trading/inquire-daily-order.md) |
| 해외선물옵션 기간계좌거래내역 | OTFM3114R | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/trading/inquire-period-trans](overseas-futureoption/trading/inquire-period-trans.md) |
| 해외선물옵션 증거금상세 | OTFM3115R | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/trading/margin-detail](overseas-futureoption/trading/margin-detail.md) |

## [해외선물옵션] 기본시세

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 해외선물종목현재가 | HHDFC55010000 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/inquire-price](overseas-futureoption/quotations/inquire-price.md) |
| 해외선물종목상세 | HHDFC55010100 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/stock-detail](overseas-futureoption/quotations/stock-detail.md) |
| 해외선물 호가 | HHDFC86000000 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/inquire-asking-price](overseas-futureoption/quotations/inquire-asking-price.md) |
| 해외선물 분봉조회 | HHDFC55020400 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/inquire-time-futurechartprice](overseas-futureoption/quotations/inquire-time-futurechartprice.md) |
| 해외선물 체결추이(틱) | HHDFC55020200 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/tick-ccnl](overseas-futureoption/quotations/tick-ccnl.md) |
| 해외선물 체결추이(주간) | HHDFC55020000 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/weekly-ccnl](overseas-futureoption/quotations/weekly-ccnl.md) |
| 해외선물 체결추이(일간) | HHDFC55020100 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/daily-ccnl](overseas-futureoption/quotations/daily-ccnl.md) |
| 해외선물 체결추이(월간) | HHDFC55020300 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/monthly-ccnl](overseas-futureoption/quotations/monthly-ccnl.md) |
| 해외선물 상품기본정보 | HHDFC55200000 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/search-contract-detail](overseas-futureoption/quotations/search-contract-detail.md) |
| 해외선물 미결제추이 | HHDDB95030000 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/investor-unpd-trend](overseas-futureoption/quotations/investor-unpd-trend.md) |
| 해외옵션종목현재가 | HHDFO55010000 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/opt-price](overseas-futureoption/quotations/opt-price.md) |
| 해외옵션종목상세 | HHDFO55010100 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/opt-detail](overseas-futureoption/quotations/opt-detail.md) |
| 해외옵션 호가 | HHDFO86000000 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/opt-asking-price](overseas-futureoption/quotations/opt-asking-price.md) |
| 해외옵션 분봉조회 | HHDFO55020400 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/inquire-time-optchartprice](overseas-futureoption/quotations/inquire-time-optchartprice.md) |
| 해외옵션 체결추이(틱) | HHDFO55020200 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/opt-tick-ccnl](overseas-futureoption/quotations/opt-tick-ccnl.md) |
| 해외옵션 체결추이(일간) | HHDFO55020100 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/opt-daily-ccnl](overseas-futureoption/quotations/opt-daily-ccnl.md) |
| 해외옵션 체결추이(주간) | HHDFO55020000 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/opt-weekly-ccnl](overseas-futureoption/quotations/opt-weekly-ccnl.md) |
| 해외옵션 체결추이(월간) | HHDFO55020300 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/opt-monthly-ccnl](overseas-futureoption/quotations/opt-monthly-ccnl.md) |
| 해외옵션 상품기본정보 | HHDFO55200000 | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/search-opt-detail](overseas-futureoption/quotations/search-opt-detail.md) |
| 해외선물옵션 장운영시간 | OTFM2229R | 모의투자 미지원 | GET | [/uapi/overseas-futureoption/v1/quotations/market-time](overseas-futureoption/quotations/market-time.md) |

## [해외선물옵션]실시간시세

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 해외선물옵션 실시간체결가 | HDFFF020 | 모의투자 미지원 | POST | [/tryitout/HDFFF020](websocket/HDFFF020.md) |
| 해외선물옵션 실시간호가 | HDFFF010 | 모의투자 미지원 | POST | [/tryitout/HDFFF010](websocket/HDFFF010.md) |
| 해외선물옵션 실시간주문내역통보 | HDFFF1C0 | 모의투자 미지원 | POST | [/tryitout/HDFFF1C0](websocket/HDFFF1C0.md) |
| 해외선물옵션 실시간체결내역통보 | HDFFF2C0 | 모의투자 미지원 | POST | [/tryitout/HDFFF2C0](websocket/HDFFF2C0.md) |

## [장내채권] 주문/계좌

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 장내채권 매수주문 | TTTC0952U | 모의투자 미지원 | POST | [/uapi/domestic-bond/v1/trading/buy](domestic-bond/trading/buy.md) |
| 장내채권 매도주문 | TTTC0958U | 모의투자 미지원 | POST | [/uapi/domestic-bond/v1/trading/sell](domestic-bond/trading/sell.md) |
| 장내채권 정정취소주문 | TTTC0953U | 모의투자 미지원 | POST | [/uapi/domestic-bond/v1/trading/order-rvsecncl](domestic-bond/trading/order-rvsecncl.md) |
| 채권정정취소가능주문조회 | CTSC8035R | 모의투자 미지원 | GET | [/uapi/domestic-bond/v1/trading/inquire-psbl-rvsecncl](domestic-bond/trading/inquire-psbl-rvsecncl.md) |
| 장내채권 주문체결내역 | CTSC8013R | 모의투자 미지원 | GET | [/uapi/domestic-bond/v1/trading/inquire-daily-ccld](domestic-bond/trading/inquire-daily-ccld.md) |
| 장내채권 잔고조회 | CTSC8407R | 모의투자 미지원 | GET | [/uapi/domestic-bond/v1/trading/inquire-balance](domestic-bond/trading/inquire-balance.md) |
| 장내채권 매수가능조회 | TTTC8910R | 모의투자 미지원 | GET | [/uapi/domestic-bond/v1/trading/inquire-psbl-order](domestic-bond/trading/inquire-psbl-order.md) |

## [장내채권] 기본시세

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 장내채권현재가(호가) | FHKBJ773401C0 | 모의투자 미지원 | GET | [/uapi/domestic-bond/v1/quotations/inquire-asking-price](domestic-bond/quotations/inquire-asking-price.md) |
| 장내채권현재가(시세) | FHKBJ773400C0 | 모의투자 미지원 | GET | [/uapi/domestic-bond/v1/quotations/inquire-price](domestic-bond/quotations/inquire-price.md) |
| 장내채권현재가(체결) | FHKBJ773403C0 | 모의투자 미지원 | GET | [/uapi/domestic-bond/v1/quotations/inquire-ccnl](domestic-bond/quotations/inquire-ccnl.md) |
| 장내채권현재가(일별) | FHKBJ773404C0 | 모의투자 미지원 | GET | [/uapi/domestic-bond/v1/quotations/inquire-daily-price](domestic-bond/quotations/inquire-daily-price.md) |
| 장내채권 기간별시세(일) | FHKBJ773701C0 | 모의투자 미지원 | GET | [/uapi/domestic-bond/v1/quotations/inquire-daily-itemchartprice](domestic-bond/quotations/inquire-daily-itemchartprice.md) |
| 장내채권 평균단가조회 | CTPF2005R | 모의투자 미지원 | GET | [/uapi/domestic-bond/v1/quotations/avg-unit](domestic-bond/quotations/avg-unit.md) |
| 장내채권 발행정보 | CTPF1101R | 모의투자 미지원 | GET | [/uapi/domestic-bond/v1/quotations/issue-info](domestic-bond/quotations/issue-info.md) |
| 장내채권 기본조회 | CTPF1114R | 모의투자 미지원 | GET | [/uapi/domestic-bond/v1/quotations/search-bond-info](domestic-bond/quotations/search-bond-info.md) |

## [장내채권] 실시간시세

| API 명 | 실전 TR_ID | 모의 TR_ID | Method | URL (→ 문서) |
|---|---|---|---|---|
| 일반채권 실시간체결가 | H0BJCNT0 | 모의투자 미지원 | POST | [/tryitout/H0BJCNT0](websocket/H0BJCNT0.md) |
| 일반채권 실시간호가 | H0BJCNT0 | 모의투자 미지원 | POST | [/tryitout/H0BJASP0](websocket/H0BJASP0.md) |
| 채권지수 실시간체결가 | H0BICNT0 | 모의투자 미지원 | POST | [/tryitout/H0BICNT0](websocket/H0BICNT0.md) |
