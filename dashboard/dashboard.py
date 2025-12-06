import streamlit as st
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
import plotly.graph_objects as go

# Charger les variables .env
load_dotenv()

# Connexion à PostgreSQL
def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
@st.cache_data
def load_prediction(crypto_name):
    try:
        conn = get_connection()
        query = """
            SELECT * FROM predictions
            WHERE crypto = %s
            ORDER BY timestamp DESC
            LIMIT 1;
        """
        df = pd.read_sql_query(query, conn, params=(crypto_name,))
        conn.close()
        if not df.empty:
            return df.iloc[0]
        return None
    except Exception as e:
        st.warning(f"⚠️ Impossible de charger la prédiction : {e}")
        return None


# Récupérer les données d'une crypto
@st.cache_data
def load_crypto_data(crypto_name):
    conn = get_connection()
    query = """
        SELECT timestamp, price, rsi, macd, macd_signal, macd_histogram, 
            sma, upper_band, lower_band, adx, stoch_rsi, 
            fibo_23, fibo_38, fibo_50, fibo_61, fibo_78
        FROM crypto_prices
        WHERE crypto = %s
        ORDER BY timestamp ASC
    """
    df = pd.read_sql_query(query, conn, params=(crypto_name,))
    conn.close()

    # Ajouter MACD Histogramme (MACD - Signal)
    df["macd_histogram"] = df["macd"] - df["macd_signal"]
    return df

# Récupérer le dernier Fear & Greed Index
def get_fear_greed_index():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM fear_greed_index ORDER BY date DESC LIMIT 1",
        conn
    )
    conn.close()
    if not df.empty:
        return df.iloc[0]["value"], df.iloc[0]["classification"]
    return None, None

# UI Streamlit
st.set_page_config(page_title="CryptoBot Dashboard", layout="wide")
st.title("📊 Dashboard CryptoBot")

# Sélection de la crypto
crypto = st.selectbox("Sélectionne une crypto :", ["bitcoin", "ethereum", "binancecoin"])

prediction = load_prediction(crypto)

st.subheader(f" Prédiction du prix pour demain ({crypto.capitalize()})")


if prediction is not None:
    st.metric(label=f"Prix actuel ({crypto.upper()})", value=f"${prediction['last_price']:,.2f}")
    st.metric(label=f"Prédiction pour demain ({crypto.upper()})", value=f"${prediction['predicted_price']:,.2f}")
    st.caption(f"Erreur moyenne du modèle (MAE) : ±${prediction['model_mae']:,.2f}")
    st.caption(f"Date de la prédiction : {prediction['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    # Affichage de la décision (BUY, SELL, HOLD)
    decision = prediction['decision']
    # 🎨 Petit encart coloré avec emoji
    if decision == "BUY":
        st.markdown(
            "<div style='background-color:#d4edda; color:#155724; padding:10px; border-radius:10px;'>"
            "🚀 <b>Decision : BUY</b> - Le modèle recommande d'acheter.</div>",
            unsafe_allow_html=True
        )
    elif decision == "SELL":
        st.markdown(
            "<div style='background-color:#f8d7da; color:#721c24; padding:10px; border-radius:10px;'>"
            "🔻 <b>Decision : SELL</b> - Le modèle recommande de vendre.</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div style='background-color:#fff3cd; color:#856404; padding:10px; border-radius:10px;'>"
            "🤝 <b>Decision : HOLD</b> - Le modèle recommande de conserver.</div>",
            unsafe_allow_html=True
        )
else:
    st.warning("Pas de prédiction disponible.")
    st.info("Lancer le script `python predict_price.py` pour générer une nouvelle prédiction.")



# Récupérer Fear & Greed Index
fng_value, fng_class = get_fear_greed_index()

if fng_value is not None:
    category_colors = {
        "Extreme Fear": "red",
        "Fear": "orange",
        "Greed": "yellow",
        "Extreme Greed": "green"
    }
    category = fng_class
    color = category_colors.get(category, "gray")

    # Graphique Fear & Greed en jauge
    fig_fng = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fng_value,
        title={"text": f"🧠 Fear & Greed ({category})"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "white"},
            "steps": [
                {"range": [0, 25], "color": "red"},
                {"range": [25, 50], "color": "darkorange"},
                {"range": [50, 75], "color": "gold"},
                {"range": [75, 100], "color": "green"}
            ],
        }
    ))
    st.plotly_chart(fig_fng)

# Chargement des données
df = load_crypto_data(crypto)
df["rsi"] = df["rsi"].fillna(0)
df["adx"] = df["adx"].fillna(0)
print(df.isnull().sum())  # Vérifier qu'il n'y a plus de valeurs NaN
print(df.head())  # Vérifier les premières lignes





# Graphique Prix (Plotly)
st.subheader(f"📈 Évolution du prix - {crypto.capitalize()}")
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(x=df["timestamp"], y=df["price"], mode="lines", name="Prix", line=dict(color="blue")))
fig_price.update_layout(xaxis_title="Date", yaxis_title="Prix", template="plotly_dark")
st.plotly_chart(fig_price)

# RSI (Plotly)
st.subheader("🟠 RSI")
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=df["timestamp"], y=df["rsi"], mode="lines", name="RSI", line=dict(color="orange")))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Surachat (70)")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Survente (30)")
fig_rsi.update_layout(xaxis_title="Date", yaxis_title="RSI", template="plotly_dark")
st.plotly_chart(fig_rsi)

# MACD (Plotly)
st.subheader("🔵 MACD")
fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=df["timestamp"], y=df["macd"], mode="lines", name="MACD", line=dict(color="blue")))
fig_macd.add_trace(go.Scatter(x=df["timestamp"], y=df["macd_signal"], mode="lines", name="Signal", line=dict(color="gray")))
fig_macd.add_trace(go.Bar(x=df["timestamp"], y=df["macd_histogram"], name="Histogramme", marker_color="purple"))
fig_macd.update_layout(xaxis_title="Date", yaxis_title="MACD", template="plotly_dark")
st.plotly_chart(fig_macd)

# Bandes de Bollinger (Plotly)
st.subheader("📊 Bandes de Bollinger")
fig_bollinger = go.Figure()
fig_bollinger.add_trace(go.Scatter(x=df["timestamp"], y=df["price"], mode="lines", name="Prix", line=dict(color="blue")))
fig_bollinger.add_trace(go.Scatter(x=df["timestamp"], y=df["upper_band"], mode="lines", name="Bande Supérieure", line=dict(color="red", dash="dash")))
fig_bollinger.add_trace(go.Scatter(x=df["timestamp"], y=df["lower_band"], mode="lines", name="Bande Inférieure", line=dict(color="green", dash="dash")))
fig_bollinger.update_layout(xaxis_title="Date", yaxis_title="Prix", template="plotly_dark")
st.plotly_chart(fig_bollinger)

# ADX (Plotly)
st.subheader("📉 Indicateur ADX")
fig_adx = go.Figure()
fig_adx.add_trace(go.Scatter(x=df["timestamp"], y=df["adx"], mode="lines", name="ADX", line=dict(color="purple")))
fig_adx.add_hline(y=25, line_dash="dash", line_color="gray", annotation_text="Seuil de tendance (25)")
fig_adx.update_layout(xaxis_title="Date", yaxis_title="ADX", template="plotly_dark")
st.plotly_chart(fig_adx)

# Stochastic RSI (Plotly)
st.subheader("🔄 Stochastic RSI")
fig_stoch_rsi = go.Figure()
fig_stoch_rsi.add_trace(go.Scatter(x=df["timestamp"], y=df["stoch_rsi"], mode="lines", name="Stoch RSI", line=dict(color="orange")))
fig_stoch_rsi.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Surachat (80)")
fig_stoch_rsi.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="Survente (20)")
fig_stoch_rsi.update_layout(xaxis_title="Date", yaxis_title="Stoch RSI", template="plotly_dark")
st.plotly_chart(fig_stoch_rsi)
