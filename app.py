import streamlit as st
import pandas as pd

st.set_page_config(page_title="Smart Irrigation", layout="wide")

# --------- CUSTOM CSS (for app look) ----------
st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    text-align: center;
}
.title {
    font-size: 32px;
    font-weight: bold;
}
.subtitle {
    color: gray;
}
</style>
""", unsafe_allow_html=True)

# --------- HEADER ----------
st.markdown(f"""
<div class="card">
    <div class="title">Good Morning, Sahil 👋</div>
    <div class="subtitle">Smart Irrigation System</div>
</div>
""", unsafe_allow_html=True)

st.write("")

# --------- FILE UPLOAD ----------
file = st.file_uploader("Upload your CSV file", type="csv")

if file:
    df = pd.read_csv(file, encoding='latin1')

    # --------- CARDS (like your image) ----------
    col1, col2, col3 = st.columns(3)

    soil = df["Soil Moisture"].iloc[-1]
    temp = df["Temperature"].iloc[-1]
    hum = df["Humidity"].iloc[-1]

    col1.markdown(f"<div class='card'>🌱 Soil Moisture<br><h2>{soil}</h2></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'>🌡 Temperature<br><h2>{temp}°C</h2></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'>💧 Humidity<br><h2>{hum}%</h2></div>", unsafe_allow_html=True)

    st.write("")

    # --------- GRAPH ----------
    st.markdown("### 📈 Sensor Trends")

    st.line_chart(df.set_index("Time")[["Soil Moisture","Temperature","Humidity"]])

    st.write("")

    # --------- PUMP STATUS ----------
    st.markdown("### 🚰 Pump Status")

    st.dataframe(df[["Time","Pump Action"]], use_container_width=True)

else:
    st.info("Upload your CSV to see dashboard")
