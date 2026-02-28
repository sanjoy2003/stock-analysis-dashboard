import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

st.set_page_config(page_title="AI Stock Intelligence", layout="wide", page_icon="⚡")

st.markdown("""
<style>
/* ─── BASE ─────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
section.main > div {
    background-color: #0a0e17 !important;
    color: #e2e8f0;
    font-family: 'Segoe UI', sans-serif;
}
[data-testid="stSidebar"]         { background-color: #0d1117 !important; }
[data-testid="stHeader"]          { background-color: #0a0e17 !important; }
.block-container                  { padding-top: 1.5rem !important; }

/* ─── HERO TITLE ──────────────────────────────────── */
.hero-wrap { padding: 10px 0 6px 0; }
.hero-title {
    font-size: 44px; font-weight: 900; letter-spacing: -1px;
    background: linear-gradient(90deg, #00F5A0 0%, #00D9F5 55%, #a78bfa 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1.1; margin: 0;
}
.hero-sub {
    font-size: 13px; color: #4b5563; letter-spacing: 3px;
    margin-top: 4px; text-transform: uppercase;
}

/* ─── INPUTS ──────────────────────────────────────── */
label { color: black !important; font-weight: 600; font-size: 13px !important; }

.stNumberInput div[data-baseweb="input"],
.stTextInput  div[data-baseweb="input"] {
    background: #111827 !important;
    border: 1px solid #1f2937 !important;
    border-radius: 10px !important;
}
.stNumberInput input, .stTextInput input {
    color: #00F5A0 !important; font-weight: 700 !important;
    font-size: 16px !important; background: transparent !important;
}
.stNumberInput button {
    background: transparent !important; color: #00F5A0 !important; border: none !important;
}
.stNumberInput div[data-baseweb="input"]:focus-within,
.stTextInput  div[data-baseweb="input"]:focus-within {
    border-color: #00F5A0 !important; box-shadow: 0 0 0 2px rgba(0,245,160,0.15) !important;
}

/* ─── GENERATE BUTTON ─────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #00F5A0, #00D9F5) !important;
    color: #000 !important; font-weight: 800 !important; font-size: 15px !important;
    border-radius: 12px !important; height: 54px !important;
    width: 100% !important; border: none !important;
    box-shadow: 0 0 28px rgba(0,245,160,0.3) !important;
    letter-spacing: 1.5px !important; transition: 0.2s !important;
}
.stButton > button:hover { transform: scale(1.02) !important; }

/* ─── DIVIDER ─────────────────────────────────────── */
hr { border-color: #1f2937 !important; margin: 18px 0 !important; }

/* ─── METRIC CARD ─────────────────────────────────── */
.mc {
    background: #111827;
    border-radius: 14px; padding: 16px 12px; text-align: center;
    border: 1px solid #1f2937; transition: 0.2s ease; height: 100%;
    position: relative; overflow: hidden;
}
.mc::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 2px; border-radius: 14px 14px 0 0;
}
.mc:hover { transform: translateY(-3px); }
.mc-label { font-size: 10px; color: #6b7280; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 8px; }
.mc-val   { font-size: 28px; font-weight: 800; line-height: 1; }
.mc-hint  { font-size: 10px; color: #4b5563; margin-top: 5px; }

/* color variants */
.mc-g  { border-color: rgba(0,245,160,0.3);  box-shadow: 0 0 18px rgba(0,245,160,0.08); }
.mc-g  .mc-val { color: #00F5A0; }
.mc-g::before  { background: #00F5A0; }

.mc-y  { border-color: rgba(250,204,21,0.3); box-shadow: 0 0 18px rgba(250,204,21,0.08); }
.mc-y  .mc-val { color: #FACC15; }
.mc-y::before  { background: #FACC15; }

.mc-b  { border-color: rgba(0,217,245,0.3);  box-shadow: 0 0 18px rgba(0,217,245,0.08); }
.mc-b  .mc-val { color: #00D9F5; }
.mc-b::before  { background: #00D9F5; }

.mc-p  { border-color: rgba(167,139,250,0.3);box-shadow: 0 0 18px rgba(167,139,250,0.08); }
.mc-p  .mc-val { color: #a78bfa; }
.mc-p::before  { background: #a78bfa; }

.mc-r  { border-color: rgba(239,68,68,0.3);  box-shadow: 0 0 18px rgba(239,68,68,0.08); }
.mc-r  .mc-val { color: #ef4444; }
.mc-r::before  { background: #ef4444; }

.mc-o  { border-color: rgba(249,115,22,0.3); box-shadow: 0 0 18px rgba(249,115,22,0.08); }
.mc-o  .mc-val { color: #f97316; }
.mc-o::before  { background: #f97316; }

/* ─── VERDICT BANNER ──────────────────────────────── */
.verdict-banner {
    border-radius: 18px; padding: 28px 30px; text-align: center;
    border: 1.5px solid; position: relative; overflow: hidden;
}
.vb-buy  { background: radial-gradient(ellipse at top,#052e16 0%,#0a0e17 70%); border-color:#10b981; box-shadow:0 0 40px rgba(16,185,129,0.2); }
.vb-hold { background: radial-gradient(ellipse at top,#1c1200 0%,#0a0e17 70%); border-color:#f59e0b; box-shadow:0 0 40px rgba(245,158,11,0.2); }
.vb-sell { background: radial-gradient(ellipse at top,#1f0000 0%,#0a0e17 70%); border-color:#ef4444; box-shadow:0 0 40px rgba(239,68,68,0.2); }

.vb-tag   { font-size: 11px; letter-spacing: 3px; color: #6b7280; margin-bottom: 6px; }
.vb-main  { font-size: 38px; font-weight: 900; margin: 4px 0 12px 0; line-height:1; }
.vb-buy  .vb-main  { color: #10b981; }
.vb-hold .vb-main  { color: #f59e0b; }
.vb-sell .vb-main  { color: #ef4444; }
.vb-reason{ font-size: 14px; color: #9ca3af; line-height: 1.7; max-width:600px; margin:0 auto; }
.vb-hold-line { font-size: 13px; font-weight: 700; margin-top: 10px; }
.vb-buy  .vb-hold-line { color: #34d399; }
.vb-hold .vb-hold-line { color: #fbbf24; }
.vb-sell .vb-hold-line { color: #f87171; }

/* ─── STRATEGY CARDS ──────────────────────────────── */
.sc {
    border-radius: 14px; padding: 22px 16px; text-align: center;
    border: 1px solid #1f2937; background: #111827;
    transition: 0.2s ease; height: 100%;
}
.sc:hover { transform: translateY(-3px); }
.sc-label { font-size: 11px; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px; }
.sc-val   { font-size: 28px; font-weight: 900; margin: 4px 0; }
.sc-hint  { font-size: 11px; margin-top: 4px; opacity: 0.7; }

.sc-sell { border-left: 3px solid #ef4444; }
.sc-sell .sc-label { color: #f87171; }
.sc-sell .sc-val   { color: #ef4444; }

.sc-buy  { border-left: 3px solid #10b981; }
.sc-buy  .sc-label { color: #34d399; }
.sc-buy  .sc-val   { color: #10b981; }

.sc-sig  { border-left: 3px solid #3b82f6; }
.sc-sig  .sc-label { color: #60a5fa; }
.sc-sig  .sc-val   { color: #3b82f6; font-size: 20px; }

/* ─── PROFIT TABLE ROW ────────────────────────────── */
.pt-row {
    display:flex; justify-content:space-between; align-items:center;
    background:#111827; border-radius:10px; padding:14px 20px;
    margin:5px 0; border:1px solid #1f2937;
}
.pt-period { font-size:13px; color:#6b7280; min-width:80px; }
.pt-price  { font-size:16px; font-weight:800; }
.pt-pct    { font-size:13px; font-weight:700; min-width:70px; text-align:right; }
.pt-inv    { font-size:12px; color:#4b5563; min-width:120px; text-align:right; }

/* ─── INDICATOR ROW ───────────────────────────────── */
.ir {
    display:flex; justify-content:space-between; align-items:center;
    background:#111827; border-radius:10px; padding:11px 16px;
    margin:4px 0; border-left: 3px solid;
}
.ir-name   { font-size:12px; color:#6b7280; flex:1; }
.ir-val    { font-size:12px; font-weight:700; color:#e2e8f0; flex:1; text-align:center; }
.ir-status { font-size:12px; font-weight:600; flex:1; text-align:right; }

/* ─── AI NOTE ─────────────────────────────────────── */
.ai-note {
    background: linear-gradient(135deg,#0f172a,#1e1b4b);
    border:1px solid #312e81; border-radius:14px; padding:20px 24px; margin:12px 0;
}
.ai-note-hd { font-size:11px; color:#818cf8; letter-spacing:2px; margin-bottom:10px; text-transform:uppercase; }
.ai-note-bd { font-size:14px; color:#cbd5e1; line-height:1.75; }

/* ─── DOWNLOAD BUTTON ─────────────────────────────── */
.stDownloadButton > button {
    background: linear-gradient(135deg,#f59e0b,#FACC15) !important;
    color:#000 !important; font-weight:800 !important; font-size:14px !important;
    border-radius:12px !important; width:100% !important;
    height:50px !important; border:none !important;
    box-shadow:0 0 20px rgba(245,158,11,0.3) !important;
}
h2,h3 { color:#FACC15 !important; text-shadow:0 0 12px rgba(250,204,21,0.3); }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-wrap">
  <div class="hero-title">⚡ AI Stock Intelligence</div>
  <div class="hero-title">Institutional-Grade Technical &amp; Fundamental Research Engine</div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# ═══════════════════════════════════════════════════════════════
#  INPUTS
# ═══════════════════════════════════════════════════════════════
ci1, ci2, ci3, ci4 = st.columns([2, 1.5, 1, 1])
with ci1: symbol = st.text_input("📌 Stock Symbol", "TATAPOWER.NS", help="Add .NS for NSE India")
with ci2: investment_amount = st.number_input("💰 Investment (₹)", min_value=1000, value=50000, step=1000)
with ci3: years = st.number_input("📅 Period (Years)", min_value=1, max_value=10, value=2, step=1)
with ci4:
    st.markdown("<div style='height:27px'></div>", unsafe_allow_html=True)
    run = st.button("🚀 GENERATE AI REPORT")

if run:
    with st.spinner("⏳ Fetching live data & computing signals..."):
        stock = yf.Ticker(symbol)
        data  = stock.history(period=f"{years}y")
        info  = stock.info

    if data.empty:
        st.error("❌ Invalid symbol. Try RELIANCE.NS / TCS.NS / HDFCBANK.NS")
        st.stop()

    close  = data['Close']
    volume = data['Volume']
    high_s = data['High']
    low_s  = data['Low']
    open_s = data['Open']

    # ── RSI ─────────────────────────────────────────────────────────────
    delta    = close.diff()
    gain     = delta.clip(lower=0).rolling(14).mean()
    loss     = (-delta.clip(upper=0)).rolling(14).mean()
    rsi      = 100 - (100 / (1 + gain / loss))
    cur_rsi  = round(float(rsi.iloc[-1]), 2)

    # ── MACD ────────────────────────────────────────────────────────────
    ema12       = close.ewm(span=12).mean()
    ema26       = close.ewm(span=26).mean()
    macd_line   = ema12 - ema26
    signal_line = macd_line.ewm(span=9).mean()
    macd_hist   = macd_line - signal_line
    cur_macd    = round(float(macd_line.iloc[-1]), 2)
    cur_sig     = round(float(signal_line.iloc[-1]), 2)
    cur_hist    = round(float(macd_hist.iloc[-1]), 2)
    macd_signal = "BUY" if cur_macd > cur_sig else "SELL"

    # ── Bollinger Bands ──────────────────────────────────────────────────
    sma20  = close.rolling(20).mean()
    std20  = close.rolling(20).std()
    bb_up  = sma20 + 2 * std20
    bb_dn  = sma20 - 2 * std20
    bb_rng = float(bb_up.iloc[-1]) - float(bb_dn.iloc[-1])
    bb_pct = round(((float(close.iloc[-1]) - float(bb_dn.iloc[-1])) / bb_rng) * 100, 1) if bb_rng != 0 else 50

    # ── SMA ──────────────────────────────────────────────────────────────
    sma50  = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()

    # ── ATR ──────────────────────────────────────────────────────────────
    tr    = pd.concat([(high_s - low_s),
                       (high_s - close.shift()).abs(),
                       (low_s  - close.shift()).abs()], axis=1).max(axis=1)
    atr14 = round(float(tr.rolling(14).mean().iloc[-1]), 2)

    # ── Volume ───────────────────────────────────────────────────────────
    avg_vol    = float(volume.rolling(20).mean().iloc[-1])
    cur_vol    = float(volume.iloc[-1])
    vol_signal = "HIGH" if cur_vol > avg_vol * 1.2 else ("LOW" if cur_vol < avg_vol * 0.8 else "NORMAL")

    # ── Core numbers ─────────────────────────────────────────────────────
    cur_price  = round(float(close.iloc[-1]), 2)
    w52_high   = round(float(close.rolling(252).max().iloc[-1]), 2)
    w52_low    = round(float(close.rolling(252).min().iloc[-1]), 2)
    volatility = round(float(close.pct_change().std() * 100), 2)
    shares     = int(investment_amount // cur_price)
    upside     = round(((w52_high - cur_price) / cur_price) * 100, 2)
    downside   = round(((cur_price - w52_low)  / cur_price) * 100, 2)
    rr         = round(upside / downside, 2) if downside != 0 else 0

    sma50_val  = round(float(sma50.iloc[-1]),  2)
    sma200_val = round(float(sma200.iloc[-1]), 2) if len(data) >= 200 else None

    # ── CES ──────────────────────────────────────────────────────────────
    tf = 1.0
    if cur_price > sma50_val: tf += 0.3
    if cur_rsi   > 55:        tf += 0.2
    raw_ces   = (upside / volatility) * tf if volatility else 0
    ces_score = round(min(max(raw_ces * 20, 0), 100), 1)

    if   ces_score > 80: ces_lbl = "High Conviction"; ces_col = "#10b981"
    elif ces_score > 60: ces_lbl = "Strong Setup";    ces_col = "#22c55e"
    elif ces_score > 40: ces_lbl = "Moderate";        ces_col = "#f59e0b"
    else:                ces_lbl = "High Risk";       ces_col = "#ef4444"

    # ── Technical Score (0–100) ───────────────────────────────────────────
    pts = 0
    if   cur_rsi < 30:  pts += 25
    elif cur_rsi < 50:  pts += 20
    elif cur_rsi < 60:  pts += 12
    else:               pts +=  5
    if macd_signal == "BUY" and cur_hist > 0: pts += 22
    elif macd_signal == "BUY":               pts += 14
    else:                                    pts +=  5
    if   bb_pct < 20:   pts += 22
    elif bb_pct < 40:   pts += 14
    else:               pts +=  5
    if   rr > 2.0:      pts += 20
    elif rr > 1.2:      pts += 13
    else:               pts +=  5
    if cur_price > sma50_val: pts += 6
    if sma200_val and cur_price > sma200_val: pts += 5
    tech_score = min(pts, 100)

    # ── Fundamentals ─────────────────────────────────────────────────────
    def fv(k, mult=1, suf=""):
        v = info.get(k)
        if v is None or v == "N/A": return "N/A"
        try: return f"{round(float(v)*mult,2)}{suf}"
        except: return str(v)

    pe_val   = fv('trailingPE')
    pb_val   = fv('priceToBook')
    roe_val  = fv('returnOnEquity', 100, '%')
    de_val   = fv('debtToEquity')
    mcap     = info.get('marketCap', 0) or 0
    mcap_cr  = f"₹{round(mcap/1e7):,} Cr" if mcap else "N/A"
    div_yld  = fv('dividendYield', 100, '%')

    # ── Verdict ───────────────────────────────────────────────────────────
    if tech_score >= 65 and rr >= 1.2:
        verdict    = "✅ STRONG BUY"
        v_css      = "vb-buy"
        v_color    = "#10b981"
        hold_days  = 90
        sci_reason = (
            f"The stock scores {tech_score}/100 on our composite technical model. "
            f"RSI at {cur_rsi} indicates {'an oversold reversal opportunity' if cur_rsi < 45 else 'healthy momentum without being overbought'}. "
            f"MACD is {'bullish — histogram positive, showing rising momentum' if macd_signal=='BUY' and cur_hist>0 else 'approaching a bullish crossover'}. "
            f"Bollinger Band %B at {bb_pct}% {'shows price near the lower band — statistically high probability of bounce' if bb_pct<30 else 'shows price in the middle zone'}. "
            f"Risk-reward of {rr} means for every ₹1 at risk, there is ₹{rr} potential upside. "
            f"With ₹{investment_amount:,} you can buy {shares} shares. "
            f"Suggested hold: {hold_days} days."
        )
        why_buy  = f"Strong entry signal: RSI={cur_rsi}, MACD={macd_signal}, R:R={rr}, Tech Score={tech_score}/100."
        why_sell = f"Exit target: ₹{round(w52_high*0.98,2)} (near 52-week high). Set stop-loss at ₹{round(cur_price*0.92,2)} (-8%)."
        why_hold = f"Hold for {hold_days} days. Review if RSI crosses 70 or MACD turns negative."

    elif tech_score >= 45 or rr >= 1.0:
        verdict    = "🟡 ACCUMULATE / HOLD"
        v_css      = "vb-hold"
        v_color    = "#f59e0b"
        hold_days  = 180
        sci_reason = (
            f"Mixed signals — technical score {tech_score}/100. "
            f"RSI at {cur_rsi} is {'neutral, awaiting direction' if 40 < cur_rsi < 60 else 'elevated — avoid chasing at this level'}. "
            f"MACD is {macd_signal} but conviction is moderate. "
            f"Bollinger %B at {bb_pct}% places price in the {'middle zone — no clear edge' if 25 < bb_pct < 75 else 'extreme zone'}. "
            f"R:R of {rr} is marginal. Wait for RSI to dip below 45 or MACD crossover for a stronger entry. "
            f"Accumulate in small tranches if fundamentals are sound."
        )
        why_buy  = f"Partial entry only. Wait for RSI < 45 or MACD bullish cross before full position."
        why_sell = f"Do not buy at current price if RSI > 65. Sell if RSI > 72 and MACD turns negative."
        why_hold = f"SIP-style accumulation recommended. Review every 30 days."

    else:
        verdict    = "🔴 AVOID / WATCH"
        v_css      = "vb-sell"
        v_color    = "#ef4444"
        hold_days  = 0
        sci_reason = (
            f"Weak technical setup — score {tech_score}/100. "
            f"RSI at {cur_rsi} {'is overbought — high risk of correction' if cur_rsi > 65 else 'shows weak momentum'}. "
            f"MACD is bearish ({macd_signal}). "
            f"R:R of {rr} does not justify entry — downside risk ({downside}%) outweighs upside ({upside}%). "
            f"Bollinger %B at {bb_pct}% {'near upper band — selling pressure likely' if bb_pct > 70 else 'weak structure'}. "
            f"Avoid new positions. Set a watchlist alert for RSI < 40."
        )
        why_buy  = f"Do NOT buy currently. Wait for RSI < 40 and MACD bullish crossover."
        why_sell = f"If already holding, consider partial exit above ₹{round(cur_price*1.05,2)} (+5%)."
        why_hold = f"Watchlist only. Re-evaluate when Tech Score > 55."

    # ── Profit projection ────────────────────────────────────────────────
    monthly_ret = float(close.pct_change(21).mean())
    monthly_ret = max(min(monthly_ret, 0.07), -0.04)
    projections = []
    for days, lbl in [(30,"1 Month"),(90,"3 Months"),(180,"6 Months"),(365,"1 Year"),(730,"2 Years")]:
        m = days / 30
        pp  = round(cur_price * ((1 + monthly_ret) ** m), 2)
        pct = round(((pp - cur_price) / cur_price) * 100, 2)
        inv = int(investment_amount * (1 + pct/100))
        projections.append((lbl, pp, pct, inv))

    # ── AI note ──────────────────────────────────────────────────────────
    ai_note_text = (
        f"<b>RSI ({cur_rsi}):</b> {'🟢 Oversold — strong reversal candidate.' if cur_rsi<35 else '🟡 Neutral zone — awaiting directional confirmation.' if cur_rsi<60 else '🔴 Overbought — avoid chasing, wait for pullback.'}<br>"
        f"<b>MACD ({macd_signal}):</b> {'🟢 Bullish crossover — momentum accelerating.' if macd_signal=='BUY' and cur_hist>0 else '🟡 Nearing bullish cross — monitor daily.' if macd_signal=='BUY' else '🔴 Bearish — selling pressure dominant.'}<br>"
        f"<b>Bollinger %B ({bb_pct}%):</b> {'🟢 Near lower band — statistically likely to bounce.' if bb_pct<25 else '🔴 Near upper band — caution, possible reversal.' if bb_pct>75 else '🟡 Mid-band — no edge, wait for breakout.'}<br>"
        f"<b>Volume:</b> {'🟢 Above average — smart money accumulating.' if vol_signal=='HIGH' else '🔴 Below average — no institutional interest.' if vol_signal=='LOW' else '🟡 Normal volume — inconclusive.'}<br>"
        f"<b>Risk-Reward ({rr}):</b> {'🟢 Excellent — favorable entry.' if rr>1.5 else '🟡 Marginal — wait for better entry.' if rr>1.0 else '🔴 Poor — downside risk too high.'}"
    )

    # ═══════════════════════════════════════════════════════════════
    #  DISPLAY
    # ═══════════════════════════════════════════════════════════════

    # ── Row 1: 6 metric cards ─────────────────────────────────────────────
    st.markdown("### 📊 Live Market Overview")
    r1c = st.columns(6)
    cards_r1 = [
        ("💰 Price",     f"₹{cur_price}",  "mc-g", f"ATR ₹{atr14}"),
        ("📊 RSI (14)",  cur_rsi,           "mc-y" if 40<cur_rsi<60 else "mc-g" if cur_rsi<=40 else "mc-r", "OB>70 | OS<30"),
        ("📈 MACD",      macd_signal,        "mc-g" if macd_signal=="BUY" else "mc-r", f"Hist {cur_hist:+.2f}"),
        ("🎯 Tech Score",f"{tech_score}/100","mc-g" if tech_score>=65 else "mc-y" if tech_score>=45 else "mc-r", "Buy≥65 | Watch<45"),
        ("⚡ CES",        f"{ces_score}/100", f"mc-{'g' if ces_score>60 else 'y' if ces_score>40 else 'r'}", ces_lbl),
        ("📦 Shares",    f"{shares}",        "mc-p", f"@ ₹{cur_price}"),
    ]
    for col, (lbl, val, cls, hint) in zip(r1c, cards_r1):
        col.markdown(f"""<div class="mc {cls}">
            <div class="mc-label">{lbl}</div>
            <div class="mc-val">{val}</div>
            <div class="mc-hint">{hint}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Row 2: 6 metric cards ─────────────────────────────────────────────
    r2c = st.columns(6)
    cards_r2 = [
        ("🏔️ 52W High",  f"₹{w52_high}",  "mc-r",  f"{round(((cur_price-w52_high)/w52_high)*100,1)}% from high"),
        ("🏖️ 52W Low",   f"₹{w52_low}",   "mc-g",  f"+{round(((cur_price-w52_low)/w52_low)*100,1)}% from low"),
        ("⚖️ R:R Ratio", f"{rr}",          "mc-g" if rr>1.2 else "mc-r", f"Up {upside}% / Dn {downside}%"),
        ("📉 Volatility",f"{volatility}%", "mc-o",  "Daily std dev"),
        ("🎸 BB %B",     f"{bb_pct}%",     "mc-g" if bb_pct<25 else "mc-r" if bb_pct>75 else "mc-b", "OS<25 | OB>75"),
        ("🔊 Volume",    vol_signal,        "mc-g" if vol_signal=="HIGH" else "mc-y" if vol_signal=="NORMAL" else "mc-r", "vs 20D avg"),
    ]
    for col, (lbl, val, cls, hint) in zip(r2c, cards_r2):
        col.markdown(f"""<div class="mc {cls}">
            <div class="mc-label">{lbl}</div>
            <div class="mc-val">{val}</div>
            <div class="mc-hint">{hint}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── VERDICT + FUNDAMENTALS ────────────────────────────────────────────
    vc, fc = st.columns([3, 1])

    with vc:
        st.markdown(f"""
        <div class="verdict-banner {v_css}">
            <div class="vb-tag">🤖 AI VERDICT — {symbol.upper()}</div>
            <div class="vb-main">{verdict}</div>
            <div class="vb-reason">{sci_reason}</div>
            {"<div class='vb-hold-line'>⏱ Suggested Hold Period: " + str(hold_days) + " Days</div>" if hold_days else ""}
        </div>""", unsafe_allow_html=True)

    with fc:
        st.markdown(f"""
        <div class="mc mc-b" style="padding:18px;text-align:left">
            <div class="mc-label" style="text-align:center;margin-bottom:14px">🏢 FUNDAMENTALS</div>
            <div class="ir" style="border-left-color:#00D9F5"><span class="ir-name">P/E Ratio</span><span class="ir-val" style="color:#00D9F5">{pe_val}</span></div>
            <div class="ir" style="border-left-color:#a78bfa"><span class="ir-name">P/B Ratio</span><span class="ir-val" style="color:#a78bfa">{pb_val}</span></div>
            <div class="ir" style="border-left-color:#00F5A0"><span class="ir-name">ROE</span><span class="ir-val" style="color:#00F5A0">{roe_val}</span></div>
            <div class="ir" style="border-left-color:#f97316"><span class="ir-name">Debt/Equity</span><span class="ir-val" style="color:#f97316">{de_val}</span></div>
            <div class="ir" style="border-left-color:#FACC15"><span class="ir-name">Market Cap</span><span class="ir-val" style="color:#FACC15">{mcap_cr}</span></div>
            <div class="ir" style="border-left-color:#34d399"><span class="ir-name">Div. Yield</span><span class="ir-val" style="color:#34d399">{div_yld}</span></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── AI NOTE ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="ai-note">
        <div class="ai-note-hd">🤖 AI Analyst Note — Signal Breakdown</div>
        <div class="ai-note-bd">{ai_note_text}</div>
    </div>""", unsafe_allow_html=True)

    # ── WHY BUY / SELL / HOLD ─────────────────────────────────────────────
    wb, ws, wh = st.columns(3)
    wb.markdown(f"""<div class="sc sc-buy">
        <div class="sc-label">Why Buy?</div>
        <div class="sc-val">📈</div>
        <div class="sc-hint" style="font-size:12px;color:#d1d5db;line-height:1.6">{why_buy}</div>
    </div>""", unsafe_allow_html=True)
    ws.markdown(f"""<div class="sc sc-sell">
        <div class="sc-label">When to Sell?</div>
        <div class="sc-val">💰</div>
        <div class="sc-hint" style="font-size:12px;color:#d1d5db;line-height:1.6">{why_sell}</div>
    </div>""", unsafe_allow_html=True)
    wh.markdown(f"""<div class="sc sc-sig">
        <div class="sc-label">Hold Strategy</div>
        <div class="sc-val">⏱</div>
        <div class="sc-hint" style="font-size:12px;color:#d1d5db;line-height:1.6">{why_hold}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── PRICE ACTION ──────────────────────────────────────────────────────
    st.markdown("### 🎯 Price Action Strategy")
    target_px   = round(w52_high * 0.98, 2)
    buy_zone_px = round(w52_low  * 1.05, 2)
    stoploss_px = round(cur_price * 0.92, 2)

    sig_val = "SELL — Near Target" if cur_price >= target_px else \
              "BUY — Support Zone" if cur_price <= buy_zone_px else "HOLD / ACCUMULATE"

    pa1, pa2, pa3, pa4 = st.columns(4)
    for col, cls, lbl, val, hint in [
        (pa1,"sc-sell","🎯 Target (Sell)",  f"₹{target_px}",   "98% of 52W high"),
        (pa2,"sc-buy", "🛒 Buy Zone",       f"₹{buy_zone_px}", "5% above 52W low"),
        (pa3,"sc-sell","🛑 Stop-Loss",      f"₹{stoploss_px}", "-8% from current"),
        (pa4,"sc-sig", "📡 Live Signal",    sig_val,            f"Price: ₹{cur_price}"),
    ]:
        col.markdown(f"""<div class="sc {cls}">
            <div class="sc-label">{lbl}</div>
            <div class="sc-val">{val}</div>
            <div class="sc-hint">{hint}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── FULL CHART ────────────────────────────────────────────────────────
    st.markdown("### 📈 Live Technical Chart")
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        row_heights=[0.50, 0.18, 0.18, 0.14],
        vertical_spacing=0.025,
        subplot_titles=(f"{symbol} — Candlestick + BB + SMA", "RSI (14)", "MACD", "Volume")
    )

    fig.add_trace(go.Candlestick(
        x=data.index, open=open_s, high=high_s, low=low_s, close=close,
        increasing_line_color='#00F5A0', decreasing_line_color='#ef4444',
        name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=sma50,  line=dict(color='#FACC15',width=1.5,dash='dot'), name="SMA 50"),  row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=sma200, line=dict(color='#a78bfa',width=1.5,dash='dot'), name="SMA 200"), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=bb_up,  line=dict(color='rgba(0,217,245,0.5)',width=1),  name="BB Up",   showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=bb_dn,  line=dict(color='rgba(0,217,245,0.5)',width=1),  name="BB Low",
        fill='tonexty', fillcolor='rgba(0,217,245,0.04)', showlegend=False), row=1, col=1)

    fig.add_trace(go.Scatter(x=data.index, y=rsi, line=dict(color='#FACC15',width=2), name="RSI"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="#ef4444", line_width=1, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="#10b981", line_width=1, row=2, col=1)

    h_colors = ['#00F5A0' if v >= 0 else '#ef4444' for v in macd_hist]
    fig.add_trace(go.Bar(x=data.index, y=macd_hist, marker_color=h_colors, name="Histogram", showlegend=False), row=3, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=macd_line,   line=dict(color='#00D9F5',width=1.5), name="MACD"),   row=3, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=signal_line, line=dict(color='#f97316', width=1.5), name="Signal"), row=3, col=1)

    v_colors = ['#00F5A0' if float(close.iloc[i]) >= float(close.iloc[i-1]) else '#ef4444' for i in range(len(close))]
    fig.add_trace(go.Bar(x=data.index, y=volume, marker_color=v_colors, name="Volume", showlegend=False), row=4, col=1)

    fig.update_layout(
        height=780, template="plotly_dark",
        paper_bgcolor='#0a0e17', plot_bgcolor='#0a0e17',
        font=dict(color='#6b7280', size=11),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right",
                    bgcolor='rgba(0,0,0,0)', font=dict(size=11)),
        margin=dict(l=10,r=10,t=35,b=10)
    )
    for i in range(1, 5):
        fig.update_xaxes(gridcolor='#1f2937', row=i, col=1)
        fig.update_yaxes(gridcolor='#1f2937', row=i, col=1)
    fig.update_yaxes(range=[0,100], row=2, col=1)

    st.plotly_chart(fig, use_container_width=True, key="full_chart")
    st.markdown("---")

    # ── PROFIT PROJECTION ────────────────────────────────────────────────
    st.markdown(f"### 💹 Profit Projection  *(Avg monthly return: {round(monthly_ret*100,2)}%)*")
    pr_cols = st.columns(5)
    for idx, (lbl, pp, pct, inv) in enumerate(projections):
        color = "mc-g" if pct >= 0 else "mc-r"
        arrow = "▲" if pct >= 0 else "▼"
        pr_cols[idx].markdown(f"""<div class="mc {color}">
            <div class="mc-label">{lbl}</div>
            <div class="mc-val">₹{pp}</div>
            <div class="mc-hint">{arrow} {abs(pct)}%</div>
            <div style="font-size:11px;color:#4b5563;margin-top:4px">Inv → ₹{inv:,}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── INDICATOR TABLE ───────────────────────────────────────────────────
    st.markdown("### 🔬 Full Indicator Summary")
    ind_rows = [
        ("RSI (14)",        cur_rsi,                 "#10b981" if cur_rsi<40 else "#f59e0b" if cur_rsi<60 else "#ef4444",
         "🟢 Oversold" if cur_rsi<35 else "🟡 Neutral" if cur_rsi<60 else "🔴 Overbought"),
        ("MACD Signal",     macd_signal,              "#10b981" if macd_signal=="BUY" else "#ef4444",
         "🟢 Bullish" if macd_signal=="BUY" else "🔴 Bearish"),
        ("MACD Histogram",  f"{cur_hist:+.2f}",       "#10b981" if cur_hist>=0 else "#ef4444",
         "🟢 Rising" if cur_hist>=0 else "🔴 Falling"),
        ("Bollinger %B",    f"{bb_pct}%",             "#10b981" if bb_pct<25 else "#ef4444" if bb_pct>75 else "#f59e0b",
         "🟢 Oversold Zone" if bb_pct<25 else "🔴 Overbought Zone" if bb_pct>75 else "🟡 Neutral"),
        ("SMA 50 vs Price", f"₹{sma50_val}",          "#10b981" if cur_price>sma50_val else "#ef4444",
         "🟢 Price Above" if cur_price>sma50_val else "🔴 Price Below"),
        ("SMA 200 vs Price",f"₹{sma200_val}" if sma200_val else "N/A", "#10b981" if sma200_val and cur_price>sma200_val else "#ef4444",
         "🟢 Price Above" if sma200_val and cur_price>sma200_val else "🔴 Price Below" if sma200_val else "⚪ Need Data"),
        ("Volume Trend",    vol_signal,               "#10b981" if vol_signal=="HIGH" else "#f59e0b" if vol_signal=="NORMAL" else "#ef4444",
         "🟢 Strong" if vol_signal=="HIGH" else "🟡 Normal" if vol_signal=="NORMAL" else "🔴 Weak"),
        ("Risk-Reward",     f"{rr}",                  "#10b981" if rr>1.5 else "#f59e0b" if rr>1.0 else "#ef4444",
         "🟢 Excellent" if rr>1.5 else "🟡 Moderate" if rr>1.0 else "🔴 Poor"),
        ("ATR (14)",        f"₹{atr14}",              "#a78bfa", "📊 Daily Range"),
        ("Tech Score",      f"{tech_score}/100",      "#10b981" if tech_score>=65 else "#f59e0b" if tech_score>=45 else "#ef4444",
         "🟢 Strong" if tech_score>=65 else "🟡 Moderate" if tech_score>=45 else "🔴 Weak"),
        ("CES Score",       f"{ces_score}/100",       ces_col,   f"⚡ {ces_lbl}"),
    ]

    half = len(ind_rows) // 2 + 1
    tc1, tc2 = st.columns(2)
    for col, chunk in [(tc1, ind_rows[:half]), (tc2, ind_rows[half:])]:
        with col:
            for name, val, bcolor, status in chunk:
                st.markdown(f"""<div class="ir" style="border-left-color:{bcolor}">
                    <span class="ir-name">{name}</span>
                    <span class="ir-val">{val}</span>
                    <span class="ir-status" style="color:{bcolor}">{status}</span>
                </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ═══════════════════════════════════════════════════════════════
    #  PDF REPORT
    # ═══════════════════════════════════════════════════════════════
    pdf_fn = f"{symbol.replace('.','_')}_Report.pdf"
    doc    = SimpleDocTemplate(pdf_fn, rightMargin=45, leftMargin=45,
                               topMargin=40, bottomMargin=40)
    S      = getSampleStyleSheet()

    title_s  = ParagraphStyle('T', parent=S['Title'],  fontSize=20, spaceAfter=6,  textColor=colors.HexColor('#000000'))
    h1_s     = ParagraphStyle('H1',parent=S['Heading1'],fontSize=14, spaceAfter=4,  textColor=colors.HexColor('#1a3c6e'))
    h2_s     = ParagraphStyle('H2',parent=S['Heading2'],fontSize=12, spaceAfter=3,  textColor=colors.HexColor('#2e5e9e'))
    body_s   = ParagraphStyle('B', parent=S['Normal'], fontSize=10, spaceAfter=3,  leading=15)
    verdict_s= ParagraphStyle('V', parent=S['Normal'], fontSize=13, spaceAfter=6,  fontName='Helvetica-Bold',
                               textColor=colors.HexColor('#0a4d2e' if 'BUY' in verdict else '#7a3e00' if 'HOLD' in verdict else '#5e0000'))
    small_s  = ParagraphStyle('S', parent=S['Normal'], fontSize=9,  spaceAfter=2,  textColor=colors.HexColor('#555555'))

    elems = []
    elems.append(Paragraph(f"AI Stock Intelligence Report", title_s))
    elems.append(Paragraph(f"{symbol.upper()}  |  {pd.Timestamp.now().strftime('%d %b %Y, %H:%M')}", body_s))
    elems.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1a3c6e')))
    elems.append(Spacer(1, 0.15*inch))

    # ── Verdict block ──
    elems.append(Paragraph("AI VERDICT", h1_s))
    clean_v = verdict.replace("✅","[BUY]").replace("🟡","[HOLD]").replace("🔴","[SELL]")
    elems.append(Paragraph(clean_v, verdict_s))
    elems.append(Paragraph(sci_reason, body_s))
    elems.append(Spacer(1, 0.1*inch))

    # ── Why Buy / Sell / Hold ──
    elems.append(Paragraph("INVESTMENT GUIDANCE", h2_s))
    elems.append(Paragraph(f"<b>Why Buy:</b> {why_buy}", body_s))
    elems.append(Paragraph(f"<b>When to Sell:</b> {why_sell}", body_s))
    elems.append(Paragraph(f"<b>Hold Strategy:</b> {why_hold}", body_s))
    elems.append(Spacer(1, 0.1*inch))

    # ── Key numbers ──
    elems.append(Paragraph("KEY NUMBERS", h2_s))
    for line in [
        f"Current Price: Rs.{cur_price}  |  Shares: {shares}  |  Investment: Rs.{investment_amount:,}",
        f"52W High: Rs.{w52_high}  |  52W Low: Rs.{w52_low}",
        f"Target Price: Rs.{target_px}  |  Buy Zone: Rs.{buy_zone_px}  |  Stop-Loss: Rs.{stoploss_px}",
        f"RSI: {cur_rsi}  |  MACD: {macd_signal}  |  BB%B: {bb_pct}%",
        f"Tech Score: {tech_score}/100  |  CES: {ces_score}/100  |  R:R: {rr}",
        f"Volatility: {volatility}%  |  ATR: Rs.{atr14}  |  Volume: {vol_signal}",
    ]:
        elems.append(Paragraph(f"• {line}", body_s))
    elems.append(Spacer(1, 0.1*inch))

    # ── Fundamentals ──
    elems.append(Paragraph("FUNDAMENTALS", h2_s))
    for line in [f"P/E: {pe_val}", f"P/B: {pb_val}", f"ROE: {roe_val}",
                 f"Debt/Equity: {de_val}", f"Market Cap: {mcap_cr}", f"Dividend Yield: {div_yld}"]:
        elems.append(Paragraph(f"• {line}", body_s))
    elems.append(Spacer(1, 0.1*inch))

    # ── Indicators ──
    elems.append(Paragraph("INDICATOR SUMMARY", h2_s))
    for name, val, _, status in ind_rows:
        clean_s = status.replace("🟢","[OK]").replace("🔴","[WARN]").replace("🟡","[NEUTRAL]").replace("⚡","").replace("📊","").replace("⚪","[N/A]")
        elems.append(Paragraph(f"• {name}: {val}  —  {clean_s}", body_s))
    elems.append(Spacer(1, 0.1*inch))

    # ── Profit projection ──
    elems.append(Paragraph("PROFIT PROJECTION", h2_s))
    elems.append(Paragraph(f"Based on historical avg monthly return of {round(monthly_ret*100,2)}%", small_s))
    for lbl, pp, pct, inv in projections:
        sign = "+" if pct >= 0 else ""
        elems.append(Paragraph(f"• {lbl}: Rs.{pp}  ({sign}{pct}%)  →  Portfolio value: Rs.{inv:,}", body_s))
    elems.append(Spacer(1, 0.15*inch))

    elems.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elems.append(Paragraph(
        "DISCLAIMER: This report is generated by an AI model for educational and research purposes only. "
        "It does not constitute financial advice. Past performance is not indicative of future results. "
        "Please consult a SEBI-registered investment advisor before making any investment decisions.",
        small_s))

    doc.build(elems)

    with open(pdf_fn, "rb") as f:
        st.download_button(
            f"📥 Download Full AI Report — {symbol}",
            f, file_name=pdf_fn, mime="application/pdf")

    os.remove(pdf_fn)

    st.markdown("""
    <div style="text-align:center;color:#374151;font-size:11px;margin-top:16px;padding:12px;
    border:1px solid #1f2937;border-radius:10px;background:#0d1117">
    ⚠️ Disclaimer: For educational &amp; research purposes only. Not financial advice.
    Always consult a SEBI-registered advisor before investing.
    </div>""", unsafe_allow_html=True)