# KisanSetu — Complete Backtest Trade Report

Source: `journal\backtest_trades.csv` · 103 trades · 2019-11-22 → 2026-03-13

> Validated config: ride full position on structural trail, S4 uptrend-gated, S1 disabled. Costs (0.15% round-trip + 0.05%/side slippage) already deducted from every P&L below. Current-constituent universe (survivorship bias); live fundamental/delivery/OI confirmation layers are NOT in these numbers.

## 1. Headline

| Metric | Value |
|---|---|
| Net P&L | **₹503,727** on ₹10,00,000 |
| Trades | 103  (40 wins / 63 losses) |
| Win rate | 38.8% |
| Avg win | ₹22,637  ·  Avg loss ₹-6,377 |
| Avg R / trade | 0.58 |
| Profit factor | 2.25  (gross +₹905,489 / ₹-401,762) |
| Best trade | ADANIENT ₹171,987 |
| Worst trade | NATIONALUM ₹-16,061 |
| Avg holding | 19 calendar days |

**The shape of the edge:** a minority of trades win, but winners are far larger than losers — classic positive-expectancy trend-following. The top 5 trades below carry the whole result; the discipline is surviving the many small losses to be holding when a big one runs.

Top 5 trades = ₹474,108 (94% of net P&L).

## 2. By setup type (why each trade was taken)

### S2 — Pullback-to-demand — an established uptrend pulled back into a demand zone (prior breakout/higher-low) on drying volume, then printed a reversal close. The system's positional engine.
- 47 trades · win 28% · avg R 0.88 · net **₹353,478**

### S4 — Post-results momentum (PEAD) — a results-day surge on heavy volume while the stock was already in a confirmed daily uptrend. Drift continuation trade.
- 52 trades · win 50% · avg R 0.38 · net **₹157,851**

### S3 — Failed-breakdown reclaim — price broke a support pivot then closed back above it within 3 sessions (bear trap). Countertrend, taken at half size.
- 4 trades · win 25% · avg R -0.34 · net **₹-7,602**

## 3. By year

| Year | Trades | Win% | Net P&L |
|---|---|---|---|
| 2019 | 1 | 100% | ₹5,259 |
| 2020 | 3 | 33% | ₹-589 |
| 2021 | 17 | 47% | ₹344,533 |
| 2022 | 15 | 40% | ₹-16,589 |
| 2023 | 24 | 42% | ₹39,188 |
| 2024 | 18 | 33% | ₹130,724 |
| 2025 | 12 | 58% | ₹85,759 |
| 2026 | 13 | 8% | ₹-84,558 |

## 4. By regime at entry

| Regime | Trades | Win% | Net P&L |
|---|---|---|---|
| AMBER | 45 | 31% | ₹267,435 |
| GREEN | 36 | 42% | ₹91,501 |
| RED | 22 | 50% | ₹144,791 |

## 5. Every winning trade

| # | Symbol | Setup | In → Out | Days | Qty | P&L | R | Exit |
|---|---|---|---|---|---|---|---|---|
| 1 | ADANIENT | S2 | 2021-02-02 → 2021-06-14 | 132 | 245 | **₹171,987** | 17.30 | hit the structural stop |
| 2 | CUMMINSIND | S2 | 2024-01-04 → 2024-06-04 | 152 | 100 | **₹119,400** | 8.56 | hit the structural stop |
| 3 | TECHM | S2 | 2021-07-09 → 2021-09-29 | 82 | 264 | **₹84,033** | 20.99 | hit the structural stop |
| 4 | VEDL | S2 | 2025-09-26 → 2026-03-13 | 168 | 252 | **₹55,707** | 7.28 | hit the structural stop |
| 5 | NHPC | S4 | 2024-01-24 → 2024-02-15 | 22 | 2882 | **₹42,981** | 4.13 | hit the max-holding-period time stop |
| 6 | BANKINDIA | S2 | 2023-08-09 → 2023-10-20 | 72 | 2781 | **₹39,505** | 3.04 | hit the structural stop |
| 7 | GMRAIRPORT | S4 | 2021-09-23 → 2021-10-14 | 21 | 5702 | **₹35,447** | 3.64 | hit the max-holding-period time stop |
| 8 | VEDL | S2 | 2021-04-16 → 2021-06-16 | 61 | 1664 | **₹31,788** | 5.63 | hit the structural stop |
| 9 | BEL | S4 | 2025-05-15 → 2025-06-05 | 21 | 680 | **₹31,126** | 2.77 | hit the max-holding-period time stop |
| 10 | PNB | S4 | 2023-12-06 → 2023-12-28 | 22 | 2392 | **₹22,455** | 4.53 | hit the max-holding-period time stop |
| 11 | NHPC | S4 | 2021-10-01 → 2021-10-25 | 24 | 10151 | **₹21,686** | 2.93 | hit the max-holding-period time stop |
| 12 | HINDPETRO | S4 | 2021-09-30 → 2021-10-22 | 22 | 1212 | **₹19,910** | 2.07 | hit the max-holding-period time stop |
| 13 | GODREJPROP | S4 | 2024-01-08 → 2024-01-31 | 23 | 127 | **₹18,592** | 1.79 | hit the max-holding-period time stop |
| 14 | INDUSTOWER | S2 | 2026-01-23 → 2026-02-04 | 12 | 720 | **₹17,870** | 2.55 | closed below the last confirmed higher-low (trend broke) |
| 15 | ABCAPITAL | S4 | 2022-11-29 → 2022-12-20 | 21 | 1021 | **₹16,475** | 3.33 | hit the max-holding-period time stop |
| 16 | NAUKRI | S4 | 2021-08-30 → 2021-09-21 | 22 | 95 | **₹15,207** | 3.22 | hit the max-holding-period time stop |
| 17 | BOSCHLTD | S4 | 2025-07-14 → 2025-08-04 | 21 | 3 | **₹14,177** | 2.89 | hit the max-holding-period time stop |
| 18 | PNB | S4 | 2023-07-06 → 2023-07-27 | 21 | 3764 | **₹14,096** | 1.42 | hit the max-holding-period time stop |
| 19 | EICHERMOT | S2 | 2022-08-01 → 2022-08-29 | 28 | 65 | **₹12,033** | 0.91 | hit the structural stop |
| 20 | GAIL | S4 | 2023-12-27 → 2024-01-17 | 21 | 1388 | **₹10,943** | 1.09 | hit the max-holding-period time stop |
| 21 | LTF | S4 | 2025-10-01 → 2025-10-24 | 23 | 647 | **₹10,479** | 1.82 | hit the max-holding-period time stop |
| 22 | LT | S4 | 2023-07-25 → 2023-08-16 | 22 | 105 | **₹10,006** | 1.62 | hit the max-holding-period time stop |
| 23 | DIXON | S2 | 2024-03-18 → 2024-04-16 | 29 | 15 | **₹8,557** | 1.14 | hit the structural stop |
| 24 | NHPC | S4 | 2023-12-06 → 2023-12-28 | 22 | 1637 | **₹8,520** | 1.72 | hit the max-holding-period time stop |
| 25 | CUMMINSIND | S2 | 2022-11-24 → 2022-12-23 | 29 | 202 | **₹8,056** | 0.76 | hit the structural stop |
| 26 | POWERGRID | S4 | 2023-12-07 → 2023-12-29 | 22 | 683 | **₹7,306** | 1.47 | hit the max-holding-period time stop |
| 27 | TIINDIA | S4 | 2022-09-07 → 2022-09-28 | 21 | 50 | **₹6,660** | 1.34 | hit the max-holding-period time stop |
| 28 | NATIONALUM | S4 | 2025-10-06 → 2025-10-28 | 22 | 478 | **₹6,542** | 1.13 | hit the max-holding-period time stop |
| 29 | PRESTIGE | S2 | 2023-12-26 → 2024-02-13 | 49 | 239 | **₹5,957** | 0.46 | ≤1R after 6 weeks — capital recycled |
| 30 | FEDERALBNK | S4 | 2025-10-28 → 2025-11-19 | 22 | 517 | **₹5,904** | 1.01 | hit the max-holding-period time stop |
| 31 | APLAPOLLO | S4 | 2020-08-18 → 2020-09-08 | 21 | 366 | **₹5,721** | 1.52 | hit the max-holding-period time stop |
| 32 | FORTIS | S2 | 2024-09-11 → 2024-10-04 | 23 | 277 | **₹5,710** | 0.76 | hit the structural stop |
| 33 | MOTILALOFS | S4 | 2019-11-22 → 2019-12-13 | 21 | 277 | **₹5,259** | 0.78 | hit the max-holding-period time stop |
| 34 | GLENMARK | S3 | 2023-06-27 → 2023-06-28 | 1 | 191 | **₹5,131** | 1.04 | closed below the last confirmed higher-low (trend broke) |
| 35 | CGPOWER | S4 | 2024-05-14 → 2024-06-04 | 21 | 175 | **₹3,939** | 0.67 | hit the structural stop |
| 36 | M&M | S4 | 2022-08-03 → 2022-08-26 | 23 | 215 | **₹2,416** | 0.26 | hit the max-holding-period time stop |
| 37 | BEL | S4 | 2021-01-05 → 2021-01-27 | 22 | 2103 | **₹1,524** | 0.40 | hit the max-holding-period time stop |
| 38 | RECLTD | S4 | 2022-11-29 → 2022-12-20 | 21 | 1346 | **₹1,313** | 0.27 | hit the max-holding-period time stop |
| 39 | ADANIPORTS | S2 | 2025-05-27 → 2025-06-13 | 17 | 72 | **₹811** | 0.11 | hit the structural stop |
| 40 | BAJAJ-AUTO | S4 | 2023-07-07 → 2023-07-28 | 21 | 57 | **₹260** | 0.04 | hit the max-holding-period time stop |

## 6. Every losing trade

| # | Symbol | Setup | In → Out | Days | Qty | P&L | R | Exit |
|---|---|---|---|---|---|---|---|---|
| 1 | NATIONALUM | S4 | 2026-01-08 → 2026-01-09 | 1 | 908 | ₹-16,061 | -2.96 | hit the structural stop |
| 2 | INDUSTOWER | S2 | 2026-01-16 → 2026-01-21 | 5 | 536 | ₹-15,791 | -1.02 | hit the structural stop |
| 3 | HINDALCO | S4 | 2025-10-28 → 2025-11-06 | 9 | 291 | ₹-15,141 | -2.59 | hit the structural stop |
| 4 | WIPRO | S4 | 2024-07-19 → 2024-07-22 | 3 | 447 | ₹-12,628 | -2.20 | hit the structural stop |
| 5 | PNB | S4 | 2026-01-19 → 2026-01-20 | 1 | 2042 | ₹-11,974 | -1.03 | hit the structural stop |
| 6 | ASIANPAINT | S2 | 2023-07-12 → 2023-08-10 | 29 | 79 | ₹-10,713 | -0.82 | hit the structural stop |
| 7 | YESBANK | S4 | 2022-07-25 → 2022-07-26 | 1 | 11973 | ₹-10,310 | -1.02 | hit the structural stop |
| 8 | AMBUJACEM | S4 | 2022-09-16 → 2022-09-26 | 10 | 425 | ₹-10,241 | -1.03 | hit the structural stop |
| 9 | KEI | S4 | 2022-08-08 → 2022-08-10 | 2 | 162 | ₹-10,130 | -1.03 | hit the structural stop |
| 10 | SHRIRAMFIN | S2 | 2023-08-08 → 2023-08-14 | 6 | 663 | ₹-9,781 | -0.75 | hit the structural stop |
| 11 | BANKINDIA | S4 | 2023-07-24 → 2023-07-28 | 4 | 3437 | ₹-9,447 | -1.04 | hit the structural stop |
| 12 | ONGC | S4 | 2026-01-30 → 2026-02-02 | 3 | 408 | ₹-9,147 | -1.55 | hit the structural stop |
| 13 | ASHOKLEY | S4 | 2023-06-20 → 2023-06-23 | 3 | 3431 | ₹-9,074 | -1.04 | hit the structural stop |
| 14 | BRITANNIA | S2 | 2022-07-29 → 2022-08-02 | 4 | 71 | ₹-8,863 | -0.74 | hit the structural stop |
| 15 | ABB | S2 | 2023-07-12 → 2023-07-20 | 8 | 44 | ₹-8,403 | -0.63 | hit the structural stop |
| 16 | PNB | S2 | 2026-01-29 → 2026-02-02 | 4 | 2014 | ₹-8,272 | -1.07 | hit the structural stop |
| 17 | COROMANDEL | S2 | 2022-08-25 → 2022-09-14 | 20 | 261 | ₹-8,103 | -0.81 | hit the structural stop |
| 18 | EXIDEIND | S2 | 2024-05-15 → 2024-06-04 | 20 | 276 | ₹-8,102 | -1.02 | hit the structural stop |
| 19 | ADANIPORTS | S2 | 2025-12-08 → 2025-12-09 | 1 | 176 | ₹-8,100 | -1.04 | hit the structural stop |
| 20 | DLF | S2 | 2023-06-13 → 2023-06-23 | 10 | 537 | ₹-7,925 | -0.60 | hit the structural stop |
| 21 | MARICO | S2 | 2024-10-09 → 2024-10-14 | 5 | 376 | ₹-7,860 | -1.04 | hit the structural stop |
| 22 | CGPOWER | S2 | 2022-12-13 → 2022-12-19 | 6 | 828 | ₹-7,072 | -1.04 | hit the structural stop |
| 23 | GMRAIRPORT | S2 | 2023-05-23 → 2023-05-29 | 6 | 5112 | ₹-6,821 | -0.51 | hit the structural stop |
| 24 | COALINDIA | S2 | 2026-01-23 → 2026-02-02 | 10 | 721 | ₹-6,689 | -1.06 | hit the structural stop |
| 25 | KOTAKBANK | S2 | 2026-01-01 → 2026-01-07 | 6 | 377 | ₹-6,576 | -0.84 | hit the structural stop |
| 26 | GODREJPROP | S2 | 2021-01-21 → 2021-01-22 | 1 | 141 | ₹-6,509 | -1.65 | hit the structural stop |
| 27 | ITC | S4 | 2024-07-29 → 2024-08-05 | 7 | 265 | ₹-6,275 | -1.10 | hit the structural stop |
| 28 | AUROPHARMA | S2 | 2024-09-26 → 2024-09-27 | 1 | 199 | ₹-6,243 | -1.06 | hit the structural stop |
| 29 | CONCOR | S4 | 2024-05-24 → 2024-05-31 | 7 | 116 | ₹-6,215 | -1.02 | hit the structural stop |
| 30 | INDUSTOWER | S4 | 2026-01-05 → 2026-01-06 | 1 | 625 | ₹-6,211 | -1.06 | hit the structural stop |
| 31 | FEDERALBNK | S2 | 2025-06-19 → 2025-06-20 | 1 | 1483 | ₹-6,079 | -1.07 | hit the structural stop |
| 32 | IOC | S2 | 2021-06-16 → 2021-06-29 | 13 | 1601 | ₹-6,050 | -1.02 | hit the structural stop |
| 33 | COALINDIA | S4 | 2026-01-08 → 2026-01-20 | 12 | 348 | ₹-5,996 | -1.03 | hit the structural stop |
| 34 | TECHM | S4 | 2026-01-20 → 2026-02-04 | 15 | 75 | ₹-5,913 | -1.03 | hit the structural stop |
| 35 | PAYTM | S3 | 2026-01-16 → 2026-01-21 | 5 | 86 | ₹-5,891 | -1.02 | hit the structural stop |
| 36 | 360ONE | S4 | 2025-06-17 → 2025-06-19 | 2 | 82 | ₹-5,811 | -1.02 | hit the structural stop |
| 37 | GRASIM | S2 | 2021-04-09 → 2021-04-15 | 6 | 57 | ₹-5,808 | -1.02 | hit the structural stop |
| 38 | BAJAJFINSV | S4 | 2023-10-16 → 2023-10-26 | 10 | 100 | ₹-5,798 | -1.16 | hit the structural stop |
| 39 | BAJFINANCE | S3 | 2023-07-31 → 2023-08-02 | 2 | 343 | ₹-5,196 | -1.06 | hit the structural stop |
| 40 | TCS | S2 | 2024-09-11 → 2024-09-12 | 1 | 71 | ₹-5,151 | -1.08 | hit the structural stop |
| 41 | CONCOR | S4 | 2023-12-13 → 2023-12-21 | 8 | 140 | ₹-5,127 | -1.03 | hit the structural stop |
| 42 | HINDPETRO | S2 | 2024-03-04 → 2024-03-11 | 7 | 392 | ₹-4,587 | -0.61 | hit the structural stop |
| 43 | JINDALSTEL | S2 | 2024-05-14 → 2024-06-04 | 21 | 122 | ₹-4,586 | -0.58 | hit the structural stop |
| 44 | NATIONALUM | S4 | 2021-03-04 → 2021-03-05 | 1 | 2183 | ₹-4,201 | -1.03 | hit the structural stop |
| 45 | LTM | S2 | 2026-01-02 → 2026-01-06 | 4 | 23 | ₹-3,907 | -0.52 | hit the structural stop |
| 46 | MUTHOOTFIN | S2 | 2025-12-08 → 2025-12-30 | 22 | 37 | ₹-3,856 | -0.50 | hit the structural stop |
| 47 | LTM | S4 | 2020-09-16 → 2020-09-22 | 6 | 41 | ₹-3,851 | -1.03 | hit the structural stop |
| 48 | PHOENIXLTD | S2 | 2022-07-19 → 2022-07-26 | 7 | 141 | ₹-3,769 | -0.56 | hit the structural stop |
| 49 | GLENMARK | S2 | 2021-07-05 → 2021-07-26 | 21 | 150 | ₹-3,648 | -0.62 | hit the structural stop |
| 50 | LUPIN | S2 | 2024-03-22 → 2024-04-04 | 13 | 128 | ₹-3,514 | -0.46 | closed below the last confirmed higher-low (trend broke) |
| 51 | SUNPHARMA | S4 | 2021-05-11 → 2021-05-28 | 17 | 140 | ₹-3,141 | -0.69 | hit the structural stop |
| 52 | ADANIPORTS | S2 | 2024-02-26 → 2024-03-13 | 16 | 80 | ₹-2,907 | -0.39 | hit the structural stop |
| 53 | ADANIENSOL | S4 | 2021-06-01 → 2021-06-15 | 14 | 56 | ₹-2,642 | -0.58 | hit the structural stop |
| 54 | COROMANDEL | S2 | 2022-06-15 → 2022-06-23 | 8 | 96 | ₹-2,612 | -0.39 | closed below the last confirmed higher-low (trend broke) |
| 55 | JUBLFOOD | S2 | 2021-07-05 → 2021-07-06 | 1 | 375 | ₹-2,605 | -1.13 | hit the structural stop |
| 56 | INFY | S2 | 2020-08-07 → 2020-08-25 | 18 | 84 | ₹-2,459 | -0.49 | hit the structural stop |
| 57 | TRENT | S4 | 2023-06-15 → 2023-07-07 | 22 | 139 | ₹-2,454 | -0.25 | hit the max-holding-period time stop |
| 58 | GODREJPROP | S2 | 2021-01-20 → 2021-01-21 | 1 | 142 | ₹-2,445 | -1.11 | hit the structural stop |
| 59 | APLAPOLLO | S4 | 2022-09-05 → 2022-09-26 | 21 | 185 | ₹-2,442 | -0.25 | hit the max-holding-period time stop |
| 60 | DLF | S2 | 2023-06-28 → 2023-07-25 | 27 | 552 | ₹-2,130 | -0.70 | hit the structural stop |
| 61 | BIOCON | S3 | 2023-07-28 → 2023-08-02 | 5 | 356 | ₹-1,646 | -0.33 | closed below the last confirmed higher-low (trend broke) |
| 62 | KEI | S4 | 2023-06-16 → 2023-07-10 | 24 | 77 | ₹-476 | -0.05 | hit the max-holding-period time stop |
| 63 | HINDPETRO | S4 | 2024-07-30 → 2024-08-13 | 14 | 447 | ₹-387 | -0.07 | hit the structural stop |

---
*Losses are capped by structural stops near −1R; the right tail is left uncapped by the trailing exit. That asymmetry — small bounded losses, large open-ended wins — is the entire engine.*