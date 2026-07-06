# Nifty 200 Swing Trading Playbook
### Price Action · Fundamentals · Options Flow · Institutional Footprint

> **Read this first.** This playbook is an educational decision-support framework, not investment
> advice. The author/tool is not SEBI-registered. Markets can and will take money from any system —
> the edge here is *positive expectancy + strict risk control + process discipline*, never a profit
> guarantee. Backtests use current index constituents (survivorship bias) and cannot include
> historical options/flow data; treat results as validation of the engine, not a promise.

**Calibrated for:** ₹5–25 lakh capital · Nifty 200 universe · dual book
(positional 2–6 weeks ≈ 60–70% of risk budget, short swings 3–10 days ≈ 30–40%).

---

## 0. The philosophy in one paragraph

We buy **fundamentally accelerating businesses** (the fuel), in **leading sectors** (the tide),
at **structurally logical prices** (the entry), confirmed by **institutional footprints** —
delivery volumes, options positioning, futures open interest (the smart-money check) — and we
survive by **fixed fractional risk and structural stops** (the insurance). No oscillators, no
curve-fit indicators. Every rule below answers one question: *is real, informed money likely to be
buying this, here, now — and how much do I lose if I'm wrong?*

The funnel:

```
 Nifty 200 (universe)
   │  Layer 1: Fundamental engine            → ~40–60 "Focus List" names, graded A/B/C
   │  Layer 2: Top-down alignment            → only top sectors, weekly agrees, low overhead supply
   │  Layer 3: Market-structure setups       → S1 / S2 / S3 / S4 trigger candidates
   │  Layer 4: Institutional footprint       → delivery %, bulk deals, veto lists
   │  Layer 5: Derivatives flow (F&O names)  → futures OI, PCR, OI walls, IV
   ▼  Layer 6: Trade construction & risk     → instrument, size, stop, targets, management
 1–8 live positions
```

A trade does not need every layer to be perfect — but each layer scores it, and the **grade decides
size and instrument**. Most days the correct output of this funnel is: *no trade*.

---

## 1. Layer 1 — Fundamental engine → the Focus List

Rebuilt **quarterly** (within 3 weeks of results season ending) and patched whenever a Focus List
name reports results. Run: `python run_screener.py --refresh-fundamentals`.

### 1.1 Quantitative screen (automated)

| Metric | Pass | Notes |
|---|---|---|
| Revenue growth (TTM YoY) | > 12% | banks/NBFC: NII growth |
| PAT growth (TTM YoY) | > 15% | adjusted for one-offs where visible |
| **Earnings acceleration** | latest quarter YoY growth > average of last 4 quarters | the single most important line in this table |
| ROE (or ROCE) | > 15% | capital efficiency |
| Debt / Equity | < 1.0 | skip for financials |
| Operating cash flow | positive TTM | profits must be cash |

### 1.2 Quality vetoes (auto-reject)

- Promoter pledge > 20% of holding.
- Promoter holding falling for 2 consecutive quarters (flag; reject if combined with weak structure).
- Auditor resignation / fraud investigation / severe regulatory action in the last year (manual).

### 1.3 The conviction checklist — "future plans & long-term growth" (manual, 10 points)

The part no API can do. Score each Focus List candidate 0–10; do it once per quarter from the
investor presentation, concall transcript, and annual report. One point each:

1. **Order book / revenue visibility** growing YoY (infra, capital goods, defence, EPC).
2. **Capex or capacity expansion** announced and funded (not just intended).
3. **Management guidance raised** or reiterated at the high end in the latest concall.
4. **Sector tailwind** with policy support: PLI, capex cycle, credit growth, premiumization, energy transition, defence indigenisation, China+1.
5. **Market share rising** vs listed peers (compare segment revenue growth).
6. **Margin trajectory** stable or expanding (gross + EBITDA).
7. **New product / segment / geography** that can be >10% of revenue in 3 years.
8. **Institutional ownership** (FII+DII combined) rising over last 2 quarters.
9. **No equity dilution** pending (QIP/warrants) that overhangs the price.
10. **Long-term runway**: can you state, in one sentence, why this company is bigger in 3 years? If you can't write the sentence, score 0.

### 1.4 Grades

| Grade | Definition | What it unlocks |
|---|---|---|
| **A** | passes 1.1 + checklist ≥ 7 | full size, futures allowed, option-selling structures allowed |
| **B** | passes 1.1 + checklist 4–6 | full size, cash + debit spreads only |
| **C** | passes 1.1 + checklist < 4 or unscored | half size, cash only |

---

## 2. Layer 2 — Top-down alignment

Checked daily by the screener; nothing below this line matters if the top-down is against you.

### 2.1 Sector rotation gate
- Rank NSE sectoral indices (Bank, Financial Services, IT, Pharma, Auto, FMCG, Metal, Energy, Realty, Infra, PSU Bank, Media) by **blended 1M + 3M relative strength vs Nifty 50**.
- New longs only in stocks belonging to the **top 4 sectors**, *plus* any sector showing a fresh weekly structure reversal (first weekly higher-high after a downtrend) — the "turnaround exception", at half size.

### 2.2 Multi-timeframe agreement
- The **weekly chart must agree**: weekly higher-highs/higher-lows, or a weekly base within 10% of 52-week highs.
- A daily setup against a broken weekly structure is an automatic reject. No exceptions.

### 2.3 Overhead supply score
- Distance from 52-week high: **< 5%** = best (breaking into clean air), 5–15% = acceptable, 15–25% = only S2/S3 with A-grade fundamentals, **> 25% below = reject** (too many trapped sellers above).
- All-time-high breakouts from multi-month bases are the highest-quality longs in this system.

### 2.4 Market regime gate (structure-based, no indicators)

| Regime | Definition | Permission |
|---|---|---|
| **GREEN** | Nifty 50 daily structure = HH/HL **and** breadth (% of Focus List in daily uptrend structure) > 50% **and** India VIX < 24 | all setups, full size |
| **AMBER** | exactly one of the above broken, or FII net-short index futures while DIIs absorb | S2 + S4 only, half size, no new F&O longs |
| **RED** | Nifty daily structure broken (lower-low confirmed) or VIX ≥ 28 | **no new longs**. Manage exits. Optional short module (§7) |

Regime also reads **FII/DII cash flows** (5-day cumulative) and **FII index-futures net positioning**
(participant-wise OI): sustained FII selling + net-short futures pushes GREEN→AMBER even if price
structure holds.

---

## 3. Layer 3 — Market-structure setups (pure price action)

All structure is computed from raw OHLCV swing pivots (a pivot high = a bar high greater than the
N bars either side; default N=3 daily, N=2 weekly). Trend state = sequence of pivots:
HH+HL = uptrend, LH+LL = downtrend, mixed = range.

### S1 — Breakout–retest *(short swing, 3–10 days)*

The bread-and-butter momentum trade.

- **Base**: ≥ 15 sessions of consolidation, range ≤ 12% high-to-low, within 15% of 52w high. Tighter is better (≤ 8% = "tight base" bonus).
- **Breakout day**: close above base high on **≥ 1.5× 20-day average volume**, close in **top third** of the day's range.
- **Entry**:
  - *Tight base (≤8%)*: enter on the breakout close itself; or
  - otherwise: wait for the **retest** — price returns to within 2% of the breakout level within 5 sessions and holds (does not close below it) → enter on the first close back above the prior day's high.
- **Gap rule**: if the breakout day opens **> 2% gap-up, never chase** — only the retest entry is allowed.
- **Stop**: below base high (the breakout level) minus buffer, or breakout-day low — whichever is **nearer**; max 5% from entry, else skip.
- **Target/exit**: 50% off at +1.5R or first call-OI wall; stop to breakeven; trail rest; hard time exit end of day 10.

### S2 — Pullback to demand *(positional, 2–6 weeks)*

The core compounder trade — buying leaders at wholesale prices.

- **Context**: established daily uptrend (≥ 2 completed HH/HL sequences), weekly agrees.
- **Demand zone** (any of): origin of the prior impulsive leg (the consolidation the last rally launched from) · prior breakout level · most recent confirmed higher-low area. Zone = that consolidation's high-low range.
- **Quality sign**: pullback volume **dries up** — average volume over the pullback < 0.8× the average volume of the preceding rally leg. Heavy-volume pullbacks are distribution; skip.
- **Trigger**: at/inside the zone, a **reversal close** — close above the prior day's high (engulfing-type strength), ideally with volume re-expanding.
- **Stop**: below the zone low; max 8% from entry, else skip.
- **Target/exit**: 50% at +2R or prior swing high / call-OI wall; trail rest **below each new confirmed higher-low**; full exit on daily structure break (confirmed lower-low) or close below the zone.

### S3 — Failed-breakdown reclaim *(reversal, half size)*

The bear-trap trade — when sellers fail, the snap-back is violent.

- Price closes below a well-tested support / higher-low pivot, **then closes back above it within 3 sessions**.
- Trigger: the reclaim close. Stop: below the trap low (the lowest point of the failed breakdown). Max 6%.
- **Half normal risk** (it's countertrend until proven). Manage like S1.

### S4 — Post-results momentum (PEAD) *(3–15 days)*

Post-earnings-announcement drift is one of the most persistent edges in Indian markets: a genuinely
great result is rarely fully priced in one day.

- **Results day**: gap/surge ≥ 3% on **≥ 2.5× average volume** with **delivery % above the stock's 20-day average** (institutions taking delivery, not traders churning) — and the result itself must show the acceleration of §1.1.
- **Entry**: first pullback/retest of the results-day range (typically the gap top or the day's VWAP-area, practically: the upper third of the results candle) within 5 sessions, on a reversal close. If no pullback comes and price consolidates ≥ 3 days sideways instead, enter the range break.
- **Stop**: below the results-day midpoint; max 6%.
- **This is the only setup allowed within 5 sessions of a results date.** All other setups auto-veto around earnings (binary risk).

### Relative strength requirement (all setups)
Over the setup's own leg (base length for S1, pullback length for S2…), the stock must have
outperformed the Nifty 50. We are only ever long the strongest horses.

---

## 4. Layer 4 — Institutional footprint (India-specific edge)

### 4.1 Delivery percentage — the truth serum
NSE publishes per-stock delivery volumes daily. Interpretation:

- Breakout/results day with **delivery % > stock's 20-day average** → genuine accumulation → grade up.
- Breakout on **< 25% delivery** → intraday churn dressed as a breakout → grade down (S1 demands the retest entry in this case; never the breakout-day entry).
- During S2 pullbacks: falling delivery on down days = holders not selling = bullish confirmation.

### 4.2 Bulk & block deals
- Fresh institutional/marquee-fund bulk buys in a Focus List name within the last month → grade up.
- Repeated same-party buy-sell churn (operator pattern) → flag, halve size.

### 4.3 Auto-veto list (screener rejects these daily, no discretion)
- Stock under **ASM / GSM surveillance** (any stage).
- Stock in **F&O ban** (MWPL > 95%) — crowded, no fresh derivative positions allowed anyway.
- **Results within 5 sessions** (unless setup = S4).
- Known corporate event in window: open offer, delisting vote, large IPO lock-in expiry.

---

## 5. Layer 5 — Derivatives flow read (F&O names, live)

### 5.1 Futures open interest

| Price | OI | Reading | Action |
|---|---|---|---|
| ↑ | ↑ | **Long buildup** | confirms longs; futures permitted (A-grade) |
| ↑ | ↓ | Short covering | weaker fuel; half size, cash/spread only |
| ↓ | ↑ | **Short buildup** | veto longs in this name today |
| ↓ | ↓ | Long unwinding | stand aside |

Near expiry: **rollover % vs the name's 3-month average** — high rollover into a long buildup =
position carriers have conviction; weak rollover after a rally = exit fuel.

### 5.2 Options positioning
- **Stock PCR (OI)** rising or > 0.9 → put writers (usually the better-informed side in stocks) are defending lower levels → bullish.
- **Heaviest put-OI strike below your demand zone** → the market's own stop-defence line; your structural stop and this strike agreeing = strong setup.
- **Nearest heavy call-OI strike above** → the first supply shelf → use as the 50% scale-out target.
- **Max pain** noted near expiry: expect pin-drift toward it in the final 2–3 sessions; don't initiate fresh F&O positions Wed–Thu of expiry week unless the setup is A-grade.

### 5.3 IV decides the instrument
- **Low/normal IV** → buy the move: futures (A-grade) or debit spread.
- **Elevated IV** (post-event, pre-news) → sell the insurance instead: put credit spread at the demand zone / put-wall strike.

---

## 6. Layer 6 — Trade construction, risk & management

### 6.1 Position sizing — the non-negotiable core

```
Risk per trade  = 1.0% of capital (S2 positional) | 0.75% (S1/S4 swing) | half that for S3 / C-grade / AMBER regime
Quantity        = floor( risk_amount / (entry − structural_stop) )
```

- Structural stop only (zone low / breakout invalidation / trap low) — never a round % number.
- If the structural stop is farther than the cap (8% positional / 5–6% swing) → **skip the trade**. The setup is telling you it's too loose.

**Portfolio caps** (screener enforces):
max **8** open positions · max **2 per sector** · total open risk ("heat") ≤ **4%** of capital ·
single position notional ≤ **20%** (futures counted at full contract notional ≤ 25%).

### 6.2 Instrument selection (₹5–25L calibrated)

| Instrument | When | Rules |
|---|---|---|
| **Cash equity** | default for everything | — |
| **Stock futures** | A-grade S2 **with** long-buildup confirmation | one lot's risk (lot × stop distance) must fit ≤ 1.25% of capital; notional ≤ 25%; max 2 futures positions; roll T-4 before expiry if thesis intact |
| **Debit call spread** | S1/S4 on F&O names, IV normal | buy ~0.60-delta call, sell the call at the call-OI-wall/target strike, **next-month expiry** (≥ 2× expected hold); max premium = the trade's risk budget; exit at 60–70% of max spread value or on structure stop |
| **Put credit spread / cash-secured put** | A-grade S2 at a demand zone, **elevated IV, GREEN regime only** | short strike at the heavy put-OI support below the zone, hedge leg 2 strikes lower; max 1 such position; assignment must be acceptable |
| **Nifty put hedge** | regime drops GREEN→AMBER/RED with open book | buy next-month ~0.35-delta Nifty put sized to cover ~50% of net long notional |

**Forbidden, permanently**: naked stock-option selling · weekly index-option lottery buying ·
averaging down · moving a stop away from price.

### 6.3 Managing the trade

> **Backtest-validated (see §11):** *riding the full position on a structural trailing
> stop beat scaling 50% out at a fixed target* — across two independent windows it roughly
> doubled the system's profit factor and lifted expectancy 4–9×. A low-win, positive-R
> trend system makes its money on the few trades that run for many R; taking half off at
> +2R amputates exactly that tail. So the default below is **trail, don't scale**. (Scaling
> half remains available for traders who need the psychological win-rate — set
> `exits.scale_fraction: 0.5` — but expect lower expectancy.)

1. **Entry day**: GTT/bracket order — entry, structural stop (SL-L with sensible trigger-limit gap), no target order.
2. **Trailing is the exit**: after each **new confirmed higher-low**, raise the stop to just below it (0.5% buffer). Never trail tighter than structure. Let the winner run as far as structure allows.
3. **Move to breakeven** once price is ≥ +1.5R, so the worst case becomes a scratch.
4. **Pyramiding** (S2 winners, optional): add 0.5R at each new confirmed higher-low, max 2 adds, every add raises the whole position's stop. Never add to a loser. *(Backtest-neutral on this universe — discretionary.)*
5. **Hard exits**: structure break (close below the last confirmed higher-low) = full exit, same day · S1/S4 hard time-stop day 10–15 · S2 review at 6 weeks — if < 1R progress, recycle the capital.
6. **Events**: holding through results is allowed **only** if position is ≥ +2R with stop ≥ breakeven, or hedged via the spread structure. Otherwise flatten/reduce the day before.

> **On S1 breakouts:** the backtest shows S1 *loses* money on price structure alone — it is
> only viable **with** the live delivery-% + futures-OI + grade confirmation of Layers 4–5.
> It is therefore **disabled by default** (`entries.disabled_setups: ["S1"]`). Re-enable it
> only once you are consistently applying that confirmation by hand. S2 (pullback-to-demand)
> is the validated engine of this system; S4 (post-results, uptrend-gated) is the secondary.

### 6.4 Costs & taxes (₹ matter)
- Assume ~0.25–0.3% round-trip all-in on delivery equity (STT 0.1% each side dominates), less on F&O but with wider effective spreads. The backtest charges 0.15% round-trip + 0.05% slippage per side.
- Swing gains are **STCG (20%)**; build it into expectations — a 20% gross year is ~16% net.
- Keep a single trading account/ledger separate from investments; it makes the journal and taxes honest.

---

## 7. RED-regime short module (optional, advanced)

Mirror image, used sparingly — shorts move fast and squeeze faster:
- Universe: Focus-List **rejects** with the *worst* RS, broken weekly structure, sector in bottom 3.
- Setups: S1/S2 mirrored (breakdown–retest of support, rally-to-supply in a downtrend) confirmed by **short buildup** (price↓ OI↑) and PCR < 0.7 (call writers in control).
- Instrument: stock futures (half risk) or **bear put spreads** only. Never short cash without intraday cover. Half risk budget, max 3 concurrent shorts, total heat ≤ 2%.

---

## 8. The routine

**Evening, every trading day (15–20 min)**
1. `python run_screener.py` → regime, veto list, today's setup candidates with full scorecards.
2. For each candidate: open the chart, verify the structure with your own eyes (the screener proposes, the trader disposes), check the layers-passed scorecard.
3. Place GTT orders for tomorrow; update stops on open positions to any new higher-lows.
4. Journal: yesterday's fills and exits get their outcome logged (screener appends automatically; you add one line of *why*).

**Weekend (45–60 min)**
1. Regime review: Nifty weekly structure, sector RS ranks, FII/DII weekly flows, VIX.
2. Walk the full Focus List weekly charts (60 charts ≈ 20 minutes) — mark fresh bases and zones.
3. Journal review: every closed trade vs its setup grade. Three questions: *Did I follow the rules? Was the loss a good loss (rules followed, market disagreed)? What is the one repeating mistake?*
4. Results calendar for the coming week → veto-window list.

**Quarterly (half a day, results season)**
1. `--refresh-fundamentals` → rebuild Focus List.
2. Re-score the conviction checklist for every A/B name from fresh concalls/presentations.
3. System review: expectancy, win rate, avg R by setup type from the journal — if a setup type has negative expectancy over 30+ trades, suspend it and investigate.

---

## 9. Trade journal (auto-generated, `journal/trades.csv`)

Every screener pick that becomes a trade carries:
`date · symbol · setup(S1–S4) · grade · layers_passed · regime · instrument · entry · stop · qty · risk_₹ · scale_out · exit · exit_reason · R_result · rule_violations · note`

The single most predictive column over time is `rule_violations`. Keep it at zero.

---

## 10. What makes this profitable (and what will break it)

**The edges being harvested**: momentum & post-earnings drift (well-documented, persistent) ·
fundamental acceleration (institutions take weeks to build positions — you ride their footprints) ·
sector rotation (trend persistence at the sector level) · structural entries (asymmetric R:R —
small structural stops against multi-R trends) · the delivery/OI confirmation layer (filters the
fake moves that kill most breakout traders in India).

**What breaks it**: overriding stops · trading AMBER/RED regimes at GREEN size · skipping the
journal · revenge trades after a loss · size creep after a winning streak · "just this once"
holding through results. The system's math survives a 45% win rate at avg 1.8R. It does not
survive one un-stopped position.

Expect: long flat/down stretches in AMBER/RED regimes (2022-style chop), drawdowns of 8–12% even
when executed perfectly, and most profits arriving in clusters during GREEN regimes. That is what
trend-following expectancy looks like from the inside.

---

## 11. How the rules were validated (and what changed)

The structural core was backtested on current Nifty 200 constituents, then tuned by testing
**principled** changes (theory-first, not data-mined) and keeping only those that improved
profit factor *and* expectancy *and* held up across **two independent start windows**
(2019-06 and 2021-06). Confirmation across windows is the guard against curve-fitting.

| Change tested | Verdict | Why |
|---|---|---|
| **Ride full position on structural trail** (no 50% scale-out) | **ADOPTED** | Doubled S2 profit; PF 1.28→1.9; expectancy up 4×. A positive-R / low-win system lives on its right tail. |
| **S4 only when stock already in uptrend** | **ADOPTED** | Cut 95→48 trades, win 46→56%, drawdown −11%→−8%. Pure quality gain. |
| **Disable S1 in the backtest default** | **ADOPTED** | S1 lost money on price structure in *every* variant; it needs live delivery/OI confirmation absent from the test. Kept available, off by default. |
| Exit on real structure break instead of trend-state flip | rejected | Helped 2019, hurt 2021 — not robust. |
| S1 retest-only entries | rejected | Made S1 worse, not better. |
| Pyramiding into winners | rejected (kept optional) | Neutral-to-slightly-negative on this universe. |

**Result of the adopted set (vs baseline), both windows:** profit factor 1.28→**2.25** (2019)
and 1.09→**1.74** (2021); expectancy roughly **5–9× higher**; maximum drawdown **reduced**;
Sharpe nearly doubled. Lower win rate (~38–40%) is the deliberate trade-off of letting
winners run.

**The honest ceiling.** Even optimised, the backtested CAGR (~6%) trails a buy-and-hold
Nifty (~9.7%) over this particular bull-market window — but at **lower drawdown**, sitting in
cash through RED regimes, and *before* the live fundamental/delivery/OI confirmation layers
(which exist precisely to raise hit-rate) are applied. This is a **risk-controlled,
positive-expectancy process**, not an index-beating machine. Anyone who promises you the
latter is selling something. Reproduce all of this yourself: `python experiments/sweep.py`
and `python experiments/sweep2.py`.
