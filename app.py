import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="CropCore · Smart Irrigation",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg: #111313;
    --bg-card: #1A1D1D;
    --bg-card2: #202424;
    --accent: #E8611A;
    --green: #4CAF82;
    --yellow: #F5C842;
    --red: #E85555;
    --border: rgba(255,255,255,0.07);
    --text: #F0F0EE;
    --muted: #8A9090;
    --radius: 14px;
    --radius-sm: 8px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text);
}
.stApp { background-color: var(--bg) !important; }
.block-container { padding: 1.5rem 2.5rem 3rem !important; max-width: 1400px !important; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
now = datetime.now()
greeting = "Good Morning" if now.hour < 12 else "Good Afternoon" if now.hour < 17 else "Good Evening"

st.markdown(f"""
<h1 style="font-family:Syne,sans-serif">{greeting}, Sahil 👋</h1>
<p style="color:#8A9090">Smart Irrigation Dashboard</p>
""", unsafe_allow_html=True)

# ---------- FILE UPLOAD ----------
file = st.file_uploader("Upload CSV", type=["csv"])

if file:
    df = pd.read_csv(file, encoding="latin1")
    df.columns = df.columns.str.strip()

else:
    # Demo data
    n = 50
    times = pd.date_range(end=datetime.now(), periods=n, freq="H")
    df = pd.DataFrame({
        "Time": times.strftime("%H:%M"),
        "Soil Moisture": np.random.randint(30, 80, n),
        "Temperature": np.random.randint(20, 40, n),
        "Humidity": np.random.randint(40, 90, n),
        "Pump": np.random.choice(["ON", "OFF"], n)
    })

# ---------- AUTO COLUMN ----------
time_col = df.columns[0]
soil_col = df.columns[1]
temp_col = df.columns[2]
hum_col = df.columns[3]
pump_col = df.columns[4] if len(df.columns) > 4 else None

soil = df[soil_col].iloc[-1]
temp = df[temp_col].iloc[-1]
hum = df[hum_col].iloc[-1]

# ---------- METRICS ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Soil Moisture", f"{soil}")
c2.metric("Temperature", f"{temp}°C")
c3.metric("Humidity", f"{hum}%")
c4.metric("Pump", df[pump_col].iloc[-1] if pump_col else "-")

# ---------- GRAPH ----------
st.subheader("Sensor Trends")
st.line_chart(df.set_index(time_col)[[soil_col, temp_col, hum_col]])

# ---------- TABLE ----------
if pump_col:
    st.subheader("Pump Log")
    st.dataframe(df[[time_col, pump_col]])
