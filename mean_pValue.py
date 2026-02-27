import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import scipy.stats as stats
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nifty Stock Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Background */
    .stApp { background: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background: #161b22; border-right: 1px solid #30363d; }

    /* Header */
    .hero {
        background: linear-gradient(135deg, #1f6feb 0%, #388bfd 50%, #58a6ff 100%);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(31,111,235,0.3);
    }
    .hero h1 { color: #fff; font-size: 2.2rem; margin: 0; font-weight: 700; }
    .hero p  { color: rgba(255,255,255,0.85); margin: 0.4rem 0 0; font-size: 1rem; }

    /* Metric cards */
    .metric-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
    .metric-card {
        flex: 1; min-width: 140px;
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.1rem 1.4rem;
        text-align: center;
    }
    .metric-card .val { font-size: 2rem; font-weight: 700; color: #58a6ff; }
    .metric-card .lbl { font-size: 0.78rem; color: #8b949e; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.5px; }

    /* Badge */
    .badge-strong { background:#1a7f37; color:#fff; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
    .badge-moderate { background:#9e6a03; color:#fff; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }

    /* Progress text */
    .scan-status { color: #8b949e; font-size: 0.88rem; margin-top: 0.3rem; }

    /* Table */
    [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

    /* Sidebar */
    .sidebar-title { font-size: 1.1rem; font-weight: 600; color: #e6edf3; margin-bottom: 1rem; }
    .sidebar-note { background: #21262d; border-left: 3px solid #1f6feb; border-radius: 0 8px 8px 0; padding: 0.7rem 0.9rem; font-size: 0.82rem; color: #8b949e; margin-top: 1rem; }

    /* Scan button */
    .stButton > button {
        background: linear-gradient(135deg,#1f6feb,#388bfd);
        color: #fff; border: none; border-radius: 10px;
        padding: 0.65rem 1.5rem; font-weight: 600; font-size: 1rem;
        width: 100%; cursor: pointer;
        box-shadow: 0 4px 15px rgba(31,111,235,0.4);
        transition: all 0.2s;
    }
    .stButton > button:hover { opacity: 0.88; transform: translateY(-1px); }

    /* Divider */
    hr { border-color: #30363d; }

    /* Info boxes */
    .plan-box {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 12px; padding: 1.2rem 1.6rem; margin-top: 1.2rem;
    }
    .plan-box h4 { color: #58a6ff; margin: 0 0 0.8rem; font-size: 1rem; }
    .plan-row { display: flex; align-items: flex-start; gap: 0.7rem; margin-bottom: 0.5rem; color: #e6edf3; font-size: 0.9rem; }
    .plan-icon { font-size: 1.1rem; flex-shrink: 0; }
</style>
""", unsafe_allow_html=True)

# ── Tickers ────────────────────────────────────────────────────────────────────
ALL_TICKERS = list(set([
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "HINDUNILVR.NS","ITC.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS",
    "LT.NS","AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS",
    "TITAN.NS","BAJFINANCE.NS","ULTRACEMCO.NS","NESTLEIND.NS","WIPRO.NS",
    "TECHM.NS","HCLTECH.NS","POWERGRID.NS","NTPC.NS","ONGC.NS",
    "TATAMOTORS.NS","TATASTEEL.NS","ADANIPORTS.NS","JSWSTEEL.NS","INDUSINDBK.NS",
    "M&M.NS","BAJAJFINSV.NS","DIVISLAB.NS","DRREDDY.NS","CIPLA.NS",
    "GRASIM.NS","COALINDIA.NS","EICHERMOT.NS","HINDALCO.NS","SHREECEM.NS",
    "APOLLOHOSP.NS","BRITANNIA.NS","HEROMOTOCO.NS","UPL.NS","BAJAJ-AUTO.NS",
    "ADANIENT.NS","SBILIFE.NS","HDFCLIFE.NS","PIDILITIND.NS","DABUR.NS",
    "GODREJCP.NS","MARICO.NS","BERGEPAINT.NS","COLPAL.NS","HAVELLS.NS",
    "DLF.NS","GAIL.NS","BPCL.NS","IOC.NS","VEDL.NS",
    "TATACONSUM.NS","SIEMENS.NS","ABB.NS","BOSCHLTD.NS","AMBUJACEM.NS",
    "ACC.NS","BANDHANBNK.NS","BANKBARODA.NS","PNB.NS","CANBK.NS",
    "SAIL.NS","NMDC.NS","RECLTD.NS","PFC.NS","LICHSGFIN.NS",
    "IRCTC.NS","CONCOR.NS","ADANIGREEN.NS","HAL.NS","BEL.NS",
    "BHEL.NS","INDIGO.NS","MUTHOOTFIN.NS","VOLTAS.NS","TORNTPHARM.NS",
    "LUPIN.NS","BIOCON.NS","AUROPHARMA.NS","ZYDUSLIFE.NS","MOTHERSON.NS",
    "BALKRISIND.NS","MRF.NS","APOLLOTYRE.NS","CUMMINSIND.NS","ESCORTS.NS",
    "ASHOKLEY.NS","TVSMOTOR.NS","BAJAJHLDNG.NS","PAGEIND.NS","HINDPETRO.NS",
    "TORNTPOWER.NS","TRENT.NS","DMART.NS","ZOMATO.NS","NYKAA.NS",
    "PAYTM.NS","ADANIPOWER.NS","JINDALSTEL.NS","HINDZINC.NS","CHOLAFIN.NS",
    "SBICARD.NS","TATACHEM.NS","GUJGASLTD.NS","JSWENERGY.NS",
    "NATIONALUM.NS","JUBLFOOD.NS","MCDOWELL-N.NS","IGL.NS","MGL.NS",
    "PETRONET.NS","PIIND.NS","APLAPOLLO.NS","ASTRAL.NS","BATAINDIA.NS",
    "CROMPTON.NS","VBL.NS","TATACOMM.NS","PERSISTENT.NS",
    "COFORGE.NS","LTIM.NS","MPHASIS.NS","OFSS.NS",
    "ICICIGI.NS","ICICIPRULI.NS","SRTRANSFIN.NS","MFSL.NS","M&MFIN.NS",
    "IIFL.NS","GMRINFRA.NS","ADANIWILMAR.NS","ABFRL.NS","AIAENG.NS","ALKEM.NS",
    "AUBANK.NS","BAJAJHLDNG.NS","BALRAMCHIN.NS",
    "BHARATFORG.NS","BSOFT.NS","CAMS.NS","CANFINHOME.NS","CHAMBLFERT.NS",
    "CHOLAHLDNG.NS","COROMANDEL.NS","CUB.NS","CYIENT.NS","DALBHARAT.NS",
    "DEEPAKNTR.NS","DELTACORP.NS","DEVYANI.NS","DIXON.NS","ECLERX.NS",
    "EDELWEISS.NS","ELECON.NS","EMAMILTD.NS","ENDURANCE.NS","EQUITASBNK.NS",
    "EXIDEIND.NS","FEDERALBNK.NS","FINEORG.NS","FLUOROCHEM.NS","FORTIS.NS",
    "GALAXYSURF.NS","GLAND.NS","GLAXO.NS","GLENMARK.NS",
    "GNFC.NS","GODREJPROP.NS","GRANULES.NS","GRINDWELL.NS",
    "HAPPSTMNDS.NS","HDFCAMC.NS","HIKAL.NS","HINDCOPPER.NS",
    "HUDCO.NS","IDFCFIRSTB.NS","IEX.NS","INDIAMART.NS","INDIANB.NS",
    "INDUSTOWER.NS","INTELLECT.NS","IPCALAB.NS","JKCEMENT.NS",
    "KOTAKBANK.NS","LALPATHLAB.NS","LAURUSLABS.NS","LTTS.NS",
    "MANAPPURAM.NS","MCX.NS","METROPOLIS.NS","MINDTREE.NS",
    "NAUKRI.NS","NAVINFLUOR.NS","OBEROIRLTY.NS",
    "POLICYBZR.NS","POLYCAB.NS","PVRINOX.NS","RBLBANK.NS",
    "SHRIRAMFIN.NS","SRF.NS","SUPREMEIND.NS","SYNGENE.NS",
    "TATAELXSI.NS","TATAPOWER.NS","UBL.NS","WHIRLPOOL.NS",
    "YESBANK.NS","ZEEL.NS","AARTIIND.NS","ABBOTINDIA.NS","ABCAPITAL.NS",
    "AEGISCHEM.NS","AJANTPHARM.NS","ANGELONE.NS","APOLLOPIPE.NS",
    "ASAHIINDIA.NS","ASTERDM.NS","ATUL.NS","AVANTIFEED.NS",
    "BAJAJELEC.NS","BASF.NS","BAYERCROP.NS","BIKAJI.NS","BIRLACORPN.NS",
    "BLUEDART.NS","BLUESTARCO.NS","BRIGADE.NS","BSE.NS","CAMPUS.NS",
    "CAPLIPOINT.NS","CARBORUNIV.NS","CARERATING.NS","CASTROLIND.NS",
    "CCL.NS","CDSL.NS","CELLO.NS","CENTRALBK.NS","CERA.NS",
    "CHALET.NS","CLEAN.NS","COCHINSHIP.NS","CREDITACC.NS",
    "DATAPATTNS.NS","ECLERX.NS","ENGINERSIN.NS","EQUITAS.NS",
    "FDC.NS","GABRIEL.NS","GAEL.NS","GARFIBRES.NS","GILLETTE.NS",
    "GMMPFAUDLR.NS","GODFRYPHLP.NS","GODREJAGRO.NS","GODREJIND.NS",
    "GPPL.NS","GRAPHITE.NS","GREAVESCOT.NS","GUJALKALI.NS",
    "HAPPSTMNDS.NS","HATSUN.NS","HBLPOWER.NS","HFCL.NS","HIL.NS",
    "HINDOILEXP.NS","HSCL.NS","IBREALEST.NS","ICRA.NS","IDFC.NS",
    "IFBIND.NS","IIFLWAM.NS","INDHOTEL.NS","INDIACEM.NS","INDIANHUME.NS",
    "INFIBEAM.NS","INGERRAND.NS","INOXWIND.NS","IOB.NS","IRB.NS",
    "IRCON.NS","ISEC.NS","ITI.NS","J&KBANK.NS","JBCHEPHARM.NS",
    "JBMA.NS","JKLAKSHMI.NS","JKPAPER.NS","JMFINANCIL.NS",
    "L&TFH.NS","RAMCOCEM.NS","ADANIENSOL.NS","AMBER.NS","ANANDRATHI.NS",
    "APLLTD.NS","HONAUT.NS","HLEGLAS.NS","IPCALAB.NS",
]))

# ── Core screening function ────────────────────────────────────────────────────
def get_signal(ticker, lookback, end_date):
    try:
        start = end_date - timedelta(days=lookback)
        df = yf.download(ticker, start=start, end=end_date, progress=False)
        if df.empty or len(df) < 250:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] for c in df.columns]

        df["return"] = df["Close"].pct_change() * 100
        df.dropna(inplace=True)
        df["ma_200"] = df["Close"].rolling(200).mean()
        df["ma_50"]  = df["Close"].rolling(50).mean()

        roll_mean = df["return"].rolling(20).mean()
        roll_std  = df["return"].rolling(20).std(ddof=1)
        roll_n    = df["return"].rolling(20).count()
        roll_se   = roll_std / np.sqrt(roll_n)
        roll_t    = roll_mean / roll_se

        latest = df.iloc[-1]
        t_val  = roll_t.iloc[-1]
        n_val  = roll_n.iloc[-1]

        if np.isnan(t_val) or n_val < 2:
            return None

        dfree = int(n_val - 1)
        p_val = stats.t.sf(np.abs(t_val), dfree) * 2

        trend_up    = (roll_mean.iloc[-1] > 0) and (p_val < 0.05)
        above_200   = latest["Close"] > latest["ma_200"]
        dist_200    = (latest["Close"] - latest["ma_200"]) / latest["ma_200"]
        not_stretched = dist_200 <= 0.20

        if trend_up and above_200 and not_stretched:
            return {
                "Ticker":    ticker.replace(".NS", ""),
                "Close ₹":   round(float(latest["Close"]), 2),
                "200 DMA ₹": round(float(latest["ma_200"]), 2),
                "Dist 200DMA %": round(dist_200 * 100, 2),
                "20D Mean Ret %": round(float(roll_mean.iloc[-1]), 3),
                "P-Value":   round(p_val, 4),
                "Strength":  "Strong" if p_val < 0.01 else "Moderate",
            }
        return None
    except Exception:
        return None

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚙️ Screener Settings</div>', unsafe_allow_html=True)
    end_date  = st.date_input("📅 End Date", value=datetime.today().date())
    lookback  = st.slider("📆 Lookback (days)", 300, 600, 400, step=10)
    max_dist  = st.slider("📏 Max Dist from 200 DMA (%)", 5, 40, 20, step=1)
    p_thresh  = st.select_slider("🎯 P-Value Threshold",
                                  options=[0.01, 0.02, 0.05, 0.10],
                                  value=0.05,
                                  format_func=lambda x: f"{x:.2f}")
    strength_filter = st.multiselect("💪 Strength Filter",
                                      ["Strong", "Moderate"],
                                      default=["Strong", "Moderate"])

    st.markdown("---")
    st.markdown(f'<div class="sidebar-note">🔎 Scanning <b>{len(ALL_TICKERS)}</b> stocks from Nifty universe.<br><br>Criteria:<br>• 20-day return mean &gt; 0 &amp; p &lt; {p_thresh}<br>• Close &gt; 200 DMA<br>• Distance from 200 DMA ≤ {max_dist}%</div>',
                unsafe_allow_html=True)

    run_btn = st.button("🚀 Start Scanning", use_container_width=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>📈 Mean P-Value &amp; DMA Screener</h1>
  <p>Statistical momentum screening across Nifty 500 universe · Real-time data via Yahoo Finance</p>
</div>
""", unsafe_allow_html=True)

# ── Placeholder for metrics ────────────────────────────────────────────────────
metrics_placeholder  = st.empty()
progress_placeholder = st.empty()
status_placeholder   = st.empty()
results_placeholder  = st.empty()

if not run_btn:
    st.markdown("""
    <div style="text-align:center; padding:3rem; color:#8b949e;">
      <div style="font-size:4rem;">🔍</div>
      <div style="font-size:1.2rem; margin-top:0.5rem;">Configure settings &amp; click <b style="color:#58a6ff;">Start Scanning</b></div>
      <div style="font-size:0.88rem; margin-top:0.5rem;">Results will appear here</div>
    </div>
    """, unsafe_allow_html=True)

# ── Main scan ─────────────────────────────────────────────────────────────────
if run_btn:
    end_dt   = datetime.combine(end_date, datetime.min.time())
    tickers  = ALL_TICKERS
    total    = len(tickers)
    signals  = []
    scanned  = 0
    found    = 0

    progress_bar = progress_placeholder.progress(0, text="Initialising scan…")

    for ticker in tickers:
        scanned += 1
        pct = scanned / total

        # Dynamic status
        progress_bar.progress(pct,
            text=f"Scanning **{ticker}** ({scanned}/{total}) · Found: **{found}** signals")

        signal = get_signal(ticker, lookback, end_dt)
        time.sleep(0.1)

        # Apply extra filters from sidebar
        if signal:
            if signal["Dist 200DMA %"] > max_dist:
                signal = None
            elif signal["P-Value"] > p_thresh:
                signal = None
            elif signal["Strength"] not in strength_filter:
                signal = None

        if signal:
            signals.append(signal)
            found += 1

    # ── Done ──────────────────────────────────────────────────────────────────
    progress_bar.progress(1.0, text="✅ Scan complete!")
    status_placeholder.empty()

    # Metric cards
    strong_count   = sum(1 for s in signals if s["Strength"] == "Strong")
    moderate_count = found - strong_count
    avg_pval       = round(np.mean([s["P-Value"] for s in signals]), 4) if signals else "—"
    avg_dist       = round(np.mean([s["Dist 200DMA %"] for s in signals]), 2) if signals else "—"

    metrics_placeholder.markdown(f"""
    <div class="metric-row">
      <div class="metric-card">
        <div class="val">{total}</div><div class="lbl">Stocks Scanned</div>
      </div>
      <div class="metric-card">
        <div class="val" style="color:#3fb950">{found}</div><div class="lbl">Signals Found</div>
      </div>
      <div class="metric-card">
        <div class="val" style="color:#58a6ff">{strong_count}</div><div class="lbl">Strong Signals</div>
      </div>
      <div class="metric-card">
        <div class="val" style="color:#d29922">{moderate_count}</div><div class="lbl">Moderate Signals</div>
      </div>
      <div class="metric-card">
        <div class="val" style="font-size:1.4rem">{avg_pval}</div><div class="lbl">Avg P-Value</div>
      </div>
      <div class="metric-card">
        <div class="val" style="font-size:1.4rem">{avg_dist}%</div><div class="lbl">Avg Dist 200DMA</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not signals:
        results_placeholder.warning("⚠️ No signals found for the selected criteria. Try relaxing the filters.")
    else:
        df_out = pd.DataFrame(signals).sort_values("P-Value").reset_index(drop=True)
        df_out.index += 1

        # Color-code Strength
        def color_strength(val):
            if val == "Strong":
                return "background-color:#1a7f37; color:#fff; border-radius:4px"
            return "background-color:#9e6a03; color:#fff; border-radius:4px"

        def color_pval(val):
            if val < 0.01:
                return "color:#3fb950; font-weight:700"
            elif val < 0.05:
                return "color:#d29922; font-weight:700"
            return ""

        styled = (df_out.style
                  .applymap(color_strength, subset=["Strength"])
                  .applymap(color_pval, subset=["P-Value"])
                  .format({"Close ₹": "₹{:.2f}", "200 DMA ₹": "₹{:.2f}",
                            "Dist 200DMA %": "{:.2f}%", "20D Mean Ret %": "{:.3f}%",
                            "P-Value": "{:.4f}"}))

        with results_placeholder.container():
            st.markdown(f"### 🎯 {found} Entry Signals — {end_date.strftime('%d %b %Y')}")
            st.dataframe(styled, use_container_width=True, height=min(60 + found * 38, 620))

            # Download
            csv = df_out.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"scan_{end_date}.csv",
                mime="text/csv",
            )

            # Trading plan
            st.markdown("""
            <div class="plan-box">
              <h4>📋 Trading Plan for Tomorrow</h4>
              <div class="plan-row"><span class="plan-icon">🕘</span><span><b>Entry:</b> Market open or intraday dip</span></div>
              <div class="plan-row"><span class="plan-icon">💰</span><span><b>Position size:</b> ₹10,000 – ₹20,000 per stock</span></div>
              <div class="plan-row"><span class="plan-icon">🎯</span><span><b>Target:</b> 6% profit</span></div>
              <div class="plan-row"><span class="plan-icon">🛑</span><span><b>Exit:</b> Price &lt; 50 DMA <em>and</em> &lt; 200 DMA</span></div>
              <div class="plan-row"><span class="plan-icon">⚠️</span><span><b>Risk:</b> Never risk more than 1–2% of portfolio per trade</span></div>
            </div>

            """, unsafe_allow_html=True)

