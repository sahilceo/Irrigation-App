import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CropCore · Smart Irrigation",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── GLOBAL STYLES ────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Root tokens ── */
:root {
    --bg:        #111313;
    --bg-card:   #1A1D1D;
    --bg-card2:  #202424;
    --accent:    #E8611A;
    --accent2:   #FF8C42;
    --green:     #4CAF82;
    --yellow:    #F5C842;
    --red:       #E85555;
    --border:    rgba(255,255,255,0.07);
    --text:      #F0F0EE;
    --muted:     #8A9090;
    --radius:    14px;
    --radius-sm: 8px;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text);
}
.stApp { background-color: var(--bg) !important; }

/* ── Remove default padding ── */
.block-container { padding: 1.5rem 2.5rem 3rem !important; max-width: 1400px !important; }

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: var(--bg-card2);
    border: 1.5px dashed var(--accent);
    border-radius: var(--radius);
    padding: 1rem;
}
[data-testid="stFileUploader"] label { color: var(--muted) !important; }

/* ── Metric widget override ── */
[data-testid="metric-container"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.5rem;
}
[data-testid="metric-container"] label { color: var(--muted) !important; font-size: 0.8rem; letter-spacing: 0.08em; text-transform: uppercase; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { font-family: 'Syne', sans-serif; font-size: 2rem !important; font-weight: 700 !important; color: var(--text) !important; }
[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 0.75rem; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: var(--radius); overflow: hidden; }
.stDataFrame thead th { background: var(--bg-card2) !important; color: var(--accent) !important; font-family: 'Syne', sans-serif; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; }
.stDataFrame tbody tr:hover td { background: rgba(232,97,26,0.06) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: var(--bg-card2); border-radius: var(--radius-sm); padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { background: transparent; color: var(--muted); border-radius: var(--radius-sm); font-family: 'DM Sans', sans-serif; font-weight: 500; padding: 0.4rem 1.2rem; }
.stTabs [aria-selected="true"] { background: var(--accent) !important; color: white !important; }

/* ── Alerts ── */
.stAlert { border-radius: var(--radius-sm); }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }

/* ── Custom card ── */
.crop-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    height: 100%;
}
.crop-tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
.tag-ok    { background: rgba(76,175,130,0.15); color: #4CAF82; border: 1px solid rgba(76,175,130,0.3); }
.tag-warn  { background: rgba(245,200,66,0.15); color: #F5C842; border: 1px solid rgba(245,200,66,0.3); }
.tag-alert { background: rgba(232,85,85,0.15);  color: #E85555; border: 1px solid rgba(232,85,85,0.3); }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def card(content_html):
    st.markdown(f'<div class="crop-card">{content_html}</div>', unsafe_allow_html=True)

def section_header(title, subtitle=""):
    sub = f'<p style="color:var(--muted);font-size:0.82rem;margin:2px 0 0">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
    <div style="margin: 2rem 0 1rem">
        <span style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;color:var(--text)">{title}</span>
        {sub}
    </div>""", unsafe_allow_html=True)

def status_tag(label, kind="ok"):
    return f'<span class="crop-tag tag-{kind}">{label}</span>'

def make_gauge(value, max_val, title, color="#E8611A"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"color": "#8A9090", "size": 13, "family": "DM Sans"}},
        number={"font": {"color": "#F0F0EE", "size": 28, "family": "Syne, sans-serif"}},
        gauge={
            "axis": {"range": [0, max_val], "tickcolor": "#2A2F2F", "tickfont": {"color": "#8A9090", "size": 10}},
            "bar": {"color": color},
            "bgcolor": "#202424",
            "bordercolor": "#2A2F2F",
            "steps": [{"range": [0, max_val], "color": "#1A1D1D"}],
            "threshold": {"line": {"color": color, "width": 2}, "thickness": 0.75, "value": value},
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=10, l=20, r=20), height=180,
    )
    return fig

def make_line(df, x_col, y_cols, colors):
    fig = go.Figure()
    for col, color in zip(y_cols, colors):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df[x_col], y=df[col], name=col,
                line=dict(color=color, width=2),
                fill="tozeroy", fillcolor=color.replace(")", ",0.07)").replace("rgb", "rgba"),
                mode="lines",
            ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#8A9090", "family": "DM Sans"},
        legend=dict(orientation="h", y=-0.15, font=dict(size=11)),
        xaxis=dict(gridcolor="#1F2424", showline=False, color="#8A9090"),
        yaxis=dict(gridcolor="#1F2424", showline=False, color="#8A9090"),
        margin=dict(t=10, b=10, l=0, r=0),
        height=260,
    )
    return fig


# ─── TOPBAR ───────────────────────────────────────────────────────────────────
now = datetime.now()
col_logo, col_time, col_status = st.columns([3, 2, 2])

with col_logo:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;padding:4px 0">
        <div style="width:38px;height:38px;background:var(--accent);border-radius:10px;
                    display:flex;align-items:center;justify-content:center;font-size:18px">🌿</div>
        <div>
            <div style="font-family:Syne,sans-serif;font-weight:800;font-size:1.15rem;line-height:1">CropCore</div>
            <div style="color:var(--muted);font-size:0.72rem;letter-spacing:0.1em;text-transform:uppercase">Smart Irrigation OS</div>
        </div>
    </div>""", unsafe_allow_html=True)

with col_time:
    st.markdown(f"""
    <div style="text-align:center;padding-top:6px">
        <div style="font-family:Syne,sans-serif;font-size:1.3rem;font-weight:700">{now.strftime("%H:%M")}</div>
        <div style="color:var(--muted);font-size:0.75rem">{now.strftime("%A, %d %B %Y")}</div>
    </div>""", unsafe_allow_html=True)

with col_status:
    st.markdown("""
    <div style="text-align:right;padding-top:8px">
        <span style="background:rgba(76,175,130,0.12);color:#4CAF82;border:1px solid rgba(76,175,130,0.25);
                     padding:4px 14px;border-radius:20px;font-size:0.75rem;font-weight:500">
            ● System Online
        </span>
    </div>""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)


# ─── GREETING ─────────────────────────────────────────────────────────────────
hour = now.hour
greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 17 else "Good Evening"
st.markdown(f"""
<div style="margin-bottom:1.5rem">
    <h1 style="font-family:Syne,sans-serif;font-size:1.9rem;font-weight:800;margin:0;line-height:1.1">
        {greeting}, Sahil 👋
    </h1>
    <p style="color:var(--muted);margin:4px 0 0;font-size:0.9rem">
        Here's what your fields look like today
    </p>
</div>""", unsafe_allow_html=True)


# ─── UPLOAD ───────────────────────────────────────────────────────────────────
section_header("📁 Data Source", "Upload your sensor CSV to begin")
file = st.file_uploader("", type="csv", label_visibility="collapsed")

if not file:
    # ── Demo mode ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:rgba(232,97,26,0.06);border:1px solid rgba(232,97,26,0.2);
                border-radius:var(--radius);padding:1rem 1.4rem;margin:0.5rem 0 1.5rem;
                display:flex;align-items:center;gap:10px">
        <span style="font-size:1.1rem">💡</span>
        <span style="color:var(--muted);font-size:0.85rem">
            No CSV uploaded — showing <strong style="color:var(--accent)">demo data</strong>. 
            Upload your own file above to see live readings.
        </span>
    </div>""", unsafe_allow_html=True)

    # Generate realistic demo data
    n = 48
    times = pd.date_range(end=datetime.now(), periods=n, freq="30min")
    np.random.seed(42)
    df = pd.DataFrame({
        "Timestamp": times.strftime("%H:%M"),
        "Soil Moisture": np.clip(60 + np.cumsum(np.random.randn(n) * 2), 30, 90).round(1),
        "Temperature":   np.clip(24 + np.sin(np.linspace(0, 2*np.pi, n)) * 6 + np.random.randn(n), 15, 40).round(1),
        "Humidity":      np.clip(65 + np.random.randn(n) * 5, 30, 95).round(1),
        "Pump Status":   np.where(np.random.rand(n) > 0.7, "ON", "OFF"),
    })
    time_col, soil_col, temp_col, hum_col, pump_col = df.columns
    demo = True

else:
    # ── Real data ──────────────────────────────────────────────────────────────
    try:
        df = pd.read_csv(file, encoding="latin1")
        df.columns = df.columns.str.strip()
        time_col = df.columns[0]
        soil_col = df.columns[1] if len(df.columns) > 1 else None
        temp_col = df.columns[2] if len(df.columns) > 2 else None
        hum_col  = df.columns[3] if len(df.columns) > 3 else None
        pump_col = df.columns[4] if len(df.columns) > 4 else None
        demo = False
        st.success(f"✅ Loaded **{len(df):,} rows** · {len(df.columns)} columns detected")
    except Exception as e:
        st.error(f"❌ Could not parse file: {e}")
        st.stop()

# Latest values
soil_val = float(df[soil_col].iloc[-1]) if soil_col else 0
temp_val = float(df[temp_col].iloc[-1]) if temp_col else 0
hum_val  = float(df[hum_col].iloc[-1])  if hum_col  else 0
pump_on  = str(df[pump_col].iloc[-1]).strip().upper() == "ON" if pump_col else False


# ─── KPI STRIP ────────────────────────────────────────────────────────────────
section_header("📊 Live Sensor Readings")

k1, k2, k3, k4 = st.columns(4)
k1.metric("🌱 Soil Moisture", f"{soil_val}%",  f"{soil_val - float(df[soil_col].iloc[-2]):.1f}%" if soil_col and len(df) > 1 else None)
k2.metric("🌡 Temperature",   f"{temp_val}°C", f"{temp_val - float(df[temp_col].iloc[-2]):.1f}°C" if temp_col and len(df) > 1 else None)
k3.metric("💧 Humidity",      f"{hum_val}%",   f"{hum_val  - float(df[hum_col].iloc[-2]):.1f}%"  if hum_col  and len(df) > 1 else None)
k4.metric("🚰 Pump Status",   "ON ✅" if pump_on else "OFF ⬜")


# ─── GAUGES + FIELD STATUS ────────────────────────────────────────────────────
section_header("🎛 Field Overview", "Real-time gauge readings + crop health")

g1, g2, g3, g_fields = st.columns([1, 1, 1, 1.4])

with g1:
    st.plotly_chart(make_gauge(soil_val, 100, "Soil Moisture %", "#4CAF82"), use_container_width=True)
with g2:
    st.plotly_chart(make_gauge(temp_val, 50, "Temperature °C", "#E8611A"), use_container_width=True)
with g3:
    st.plotly_chart(make_gauge(hum_val, 100, "Humidity %", "#42A5F5"), use_container_width=True)

with g_fields:
    card(f"""
    <div style="font-family:Syne,sans-serif;font-weight:700;font-size:0.9rem;
                letter-spacing:0.06em;text-transform:uppercase;color:var(--muted);margin-bottom:1rem">
        My Fields
    </div>
    <div style="display:flex;flex-direction:column;gap:0.85rem">
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:0.7rem 0;border-bottom:1px solid var(--border)">
            <div>
                <div style="font-weight:500;font-size:0.9rem">North Fields</div>
                <div style="color:var(--muted);font-size:0.75rem">2.3 Acres · Wheat</div>
            </div>
            {status_tag("Healthy", "ok")}
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:0.7rem 0;border-bottom:1px solid var(--border)">
            <div>
                <div style="font-weight:500;font-size:0.9rem">Groundnuts</div>
                <div style="color:var(--muted);font-size:0.75rem">1.3 Acres · Groundnut</div>
            </div>
            {status_tag("Irrigation Due", "warn")}
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;padding:0.7rem 0">
            <div>
                <div style="font-weight:500;font-size:0.9rem">Cottons</div>
                <div style="color:var(--muted);font-size:0.75rem">1.0 Acres · Cotton</div>
            </div>
            {status_tag("Low Moisture", "alert")}
        </div>
    </div>
    """)


# ─── TREND CHARTS ─────────────────────────────────────────────────────────────
section_header("📈 Sensor Trends", "48-point rolling window")

t1, t2 = st.tabs(["🌊 Moisture & Humidity", "🌡 Temperature"])

cols_to_plot = [c for c in [soil_col, hum_col] if c]
with t1:
    if cols_to_plot:
        st.plotly_chart(
            make_line(df, time_col, cols_to_plot, ["#4CAF82", "#42A5F5"]),
            use_container_width=True
        )

with t2:
    if temp_col:
        st.plotly_chart(
            make_line(df, time_col, [temp_col], ["#E8611A"]),
            use_container_width=True
        )


# ─── PUMP LOG + STATS ─────────────────────────────────────────────────────────
if pump_col:
    section_header("🚰 Pump Activity Log")

    p1, p2 = st.columns([1.8, 1])

    with p1:
        pump_df = df[[time_col, pump_col]].copy()
        pump_df.columns = ["Timestamp", "Pump Status"]
        pump_df["Status"] = pump_df["Pump Status"].apply(
            lambda x: "🟢 ON" if str(x).strip().upper() == "ON" else "⚫ OFF"
        )
        st.dataframe(
            pump_df[["Timestamp", "Status"]].tail(20),
            use_container_width=True, hide_index=True
        )

    with p2:
        on_count  = (df[pump_col].str.upper().str.strip() == "ON").sum()
        off_count = len(df) - on_count
        pct = round(on_count / len(df) * 100, 1) if len(df) else 0

        card(f"""
        <div style="font-family:Syne,sans-serif;font-weight:700;font-size:0.85rem;
                    letter-spacing:0.06em;text-transform:uppercase;color:var(--muted);margin-bottom:1.2rem">
            Pump Summary
        </div>
        <div style="display:flex;flex-direction:column;gap:1rem">
            <div>
                <div style="color:var(--muted);font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em">Active Cycles</div>
                <div style="font-family:Syne,sans-serif;font-size:2rem;font-weight:700;color:#4CAF82">{on_count}</div>
            </div>
            <div>
                <div style="color:var(--muted);font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em">Idle Cycles</div>
                <div style="font-family:Syne,sans-serif;font-size:2rem;font-weight:700;color:var(--muted)">{off_count}</div>
            </div>
            <div>
                <div style="color:var(--muted);font-size:0.75rem;margin-bottom:6px">Uptime</div>
                <div style="background:var(--bg-card2);border-radius:20px;height:8px;overflow:hidden">
                    <div style="background:var(--accent);height:100%;width:{pct}%;border-radius:20px;
                                transition:width 1s ease"></div>
                </div>
                <div style="color:var(--accent);font-size:0.85rem;font-weight:500;margin-top:4px">{pct}%</div>
            </div>
        </div>
        """)


# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;
            color:var(--muted);font-size:0.75rem;padding-bottom:1rem">
    <span>🌿 CropCore · Smart Irrigation OS · v2.1</span>
    <span>Built for Agri-Tech · Powered by Python & Plotly</span>
</div>""", unsafe_allow_html=True)
