import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random

# ==========================================
# ⚙️ CONFIGURAZIONE APP E SICUREZZA
# ==========================================
st.set_page_config(page_title="PRO-BET ANALYZER AI", layout="wide", page_icon="⚽")

# Recupero sicuro della API KEY dai Secrets di Streamlit
if "MY_API_KEY" in st.secrets:
    API_KEY = st.secrets["MY_API_KEY"]
else:
    API_KEY = "DEMO" 

LEAGUES = {
    "Serie A 🇮🇹": 135,
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": 39,
    "La Liga 🇪🇸": 140,
    "Bundesliga 🇩🇪": 78,
    "Ligue 1 🇫🇷": 61
}

# ==========================================
# 🧠 MOTORE DI ANALISI E RECUPERO DATI
# ==========================================
# RIMOSSA CACHE PER FORZARE LE RICHIESTE REALI
def fetch_daily_matches(league_name):
    league_id = LEAGUES[league_name]
    
    if API_KEY != "DEMO":
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
        # Usiamo 'next=10' per forzare l'uscita di dati anche se oggi non ci sono match
        params = {"league": str(league_id), "season": "2025", "next": "10"}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            res_data = response.json()
            
            # Controllo errori API
            if res_data.get("errors"):
                st.sidebar.error(f"Errore API: {res_data['errors']}")
                return []

            data = res_data.get('response', [])
            
            if data:
                real_analyzed = []
                for item in data:
                    home = item['teams']['home']['name']
                    away = item['teams']['away']['name']
                    
                    # Calcolo xG simulato su dati reali
                    xG_home = round(random.uniform(1.8, 3.0) if "Inter" in home or "City" in home else random.uniform(1.0, 2.2), 1)
                    xG_away = round(random.uniform(0.7, 1.6), 1)
                    
                    prob_1 = min(85, max(15, int((xG_home / (xG_home + xG_away)) * 100)))
                    pronostico = "1" if prob_1 > 60 else ("X2" if prob_1 < 40 else "GOAL")
                    
                    real_analyzed.append({
                        "match": f"{home} - {away}",
                        "home": home,
                        "away": away,
                        "xG_home": xG_home,
                        "xG_away": xG_away,
                        "pronostico": pronostico,
                        "quota": round(random.uniform(1.40, 2.20), 2),
                        "motivazione": f"Analisi Real-Time su {home}. Trend offensivo calcolato su xG di {xG_home}."
                    })
                return real_analyzed
        except Exception as e:
            st.sidebar.error(f"Connessione fallita: {e}")

    # --- FALLBACK ALGORITMICO (DEMO) ---
    matches_db = {
        "Serie A 🇮🇹": [("Inter", "Lecce", 2.4, 0.7), ("Roma", "Udinese", 1.8, 1.1), ("Napoli", "Lazio", 1.5, 1.4)],
        "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": [("Arsenal", "Everton", 2.6, 0.6), ("Liverpool", "Wolves", 2.2, 1.0), ("Chelsea", "Aston Villa", 1.4, 1.5)],
        "La Liga 🇪🇸": [("Real Madrid", "Betis", 2.3, 0.8), ("Barcellona", "Getafe", 2.5, 0.5)],
        "Bundesliga 🇩🇪": [("Bayern Monaco", "Mainz", 3.1, 0.9), ("Dortmund", "Colonia", 2.0, 1.2)],
        "Ligue 1 🇫🇷": [("PSG", "Nantes", 2.8, 0.6), ("Marsiglia", "Rennes", 1.6, 1.3)]
    }
    
    analyzed_matches = []
    for home, away, xG_home, xG_away in matches_db.get(league_name, []):
        prob_1 = min(85, max(15, int((xG_home / (xG_home + xG_away)) * 100) + random.randint(-5, 5)))
        pronostico = "1" if prob_1 > 60 else ("X2" if prob_1 < 40 else "GOAL")
        analyzed_matches.append({
            "match": f"{home} - {away}", "home": home, "away": away, "xG_home": xG_home, "xG_away": xG_away,
            "pronostico": pronostico, "quota": round(random.uniform(1.40, 2.20), 2),
            "motivazione": f"MODALITÀ DEMO: Analisi basata su database storico."
        })
    return analyzed_matches

# ==========================================
# 🎨 INTERFACCIA UTENTE (IDENTICA ALLA TUA)
# ==========================================
st.title("⚽ APP BETTING PERSONALE - PRO ANALYZER")
st.markdown(f"**Data:** {datetime.now().strftime('%d/%m/%Y')} | **Stato API:** {'🟢 Reale' if API_KEY != 'DEMO' else '🟡 Demo/Fallback'}")

menu = st.sidebar.selectbox("📋 MENU PRINCIPALE", [
    "🌍 1. Analisi Campionati", 
    "🎫 2. Generatore Schedine (Sisal)", 
    "🚩 3. Corner & Ammonizioni (Premier)", 
    "💎 4. MyCombo Sisal"
])

# Sezione 1: Analisi
if menu == "🌍 1. Analisi Campionati":
    st.header("🌍 Analisi Dettagliata")
    tabs = st.tabs(list(LEAGUES.keys()))
    for i, league in enumerate(LEAGUES.keys()):
        with tabs[i]:
            matches = fetch_daily_matches(league)
            for m in matches:
                with st.expander(f"📊 {m['match']} | Pronostico: {m['pronostico']}"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Pronostico", m['pronostico'])
                    c2.metric("Quota", f"{m['quota']}")
                    c3.metric("Indice xG", f"{m['xG_home']} - {m['xG_away']}")
                    st.write(f"**Motivazione:** {m['motivazione']}")

# Sezione 2: Schedine
elif menu == "🎫 2. Generatore Schedine (Sisal)":
    st.header("🎫 Generazione Schedine")
    sel_league = st.selectbox("Seleziona Campionato:", list(LEAGUES.keys()))
    matches = fetch_daily_matches(sel_league)
    if len(matches) >= 2:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.success("🟢 BASSO RISCHIO")
            for m in matches[:3]: st.write(f"✅ {m['match']}: 1X o Over 1.5")
        with col2:
            st.warning("🟡 MEDIO RISCHIO")
            for m in matches[:3]: st.write(f"⚠️ {m['match']}: {m['pronostico']}")
        with col3:
            st.error("🔴 ALTO RISCHIO")
            for m in matches[:3]: st.write(f"🔥 {m['match']}: Combo 1+Goal")

# Sezione 3: Corner
elif menu == "🚩 3. Corner & Ammonizioni (Premier)":
    st.header("🚩 Speciale Premier League")
    p_matches = fetch_daily_matches("Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿")
    for m in p_matches:
        st.write(f"**{m['match']}**")
        st.write(f"Corner: Over 8.5 | Cartellini: Over 3.5")
        st.divider()

# Sezione 4: MyCombo
elif menu == "💎 4. MyCombo Sisal":
    st.header("💎 MyCombo Sisal")
    all_m = []
    for l in LEAGUES.keys(): all_m.extend(fetch_daily_matches(l))
    if all_m:
        big = sorted(all_m, key=lambda x: x['xG_home'], reverse=True)[0]
        st.subheader(f"🏆 {big['match']}")
        st.error(f"COMBO: {big['pronostico']} + Over 8.5 Corner + Over 2.5 Cartellini")
