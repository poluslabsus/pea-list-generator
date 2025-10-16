\
import io
import time
import pandas as pd
import streamlit as st
from pea_sources import fetch_pea_fr, fetch_pea_eee, fetch_pea_all

st.set_page_config(page_title="Générateur CSV PEA", page_icon="📈", layout="wide")

st.title("📈 Générateur de CSV — Actions éligibles au PEA")
st.write("Cette application construit un CSV des actions **éligibles PEA** "
         "à partir des listes publiques (France + EEE). "
         "Tu peux ensuite l'importer dans ton screener (la colonne **symbol** est prévue).")

with st.sidebar:
    st.header("Options")
    scope = st.selectbox("Univers", ["France uniquement", "EEE uniquement", "FR + EEE (recommandé)"], index=2)
    only_with_yahoo = st.checkbox("Ne garder que les lignes avec symbole Yahoo reconstitué", value=False)
    filename = st.text_input("Nom du fichier CSV", value=f"actions_pea_{time.strftime('%Y%m%d')}.csv")

@st.cache_data(ttl=24*3600)
def load_data(scope_choice: str) -> pd.DataFrame:
    if scope_choice.startswith("France"):
        return fetch_pea_fr()
    elif scope_choice.startswith("EEE"):
        return fetch_pea_eee()
    else:
        return fetch_pea_all()

def postprocess(df: pd.DataFrame, only_yahoo: bool) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "symbol" not in out.columns:
        out["symbol"] = out.get("yahoo_symbol", pd.Series(index=out.index)).fillna(out["ticker"])
    if only_yahoo:
        out = out[~out["yahoo_symbol"].isna()]
    wanted = ["symbol","ticker","yahoo_symbol","name","exchange_code","scope","pea_eligible","source"]
    keep = [c for c in wanted if c in out.columns]
    out = out[keep].drop_duplicates().sort_values(["exchange_code","ticker"]).reset_index(drop=True)
    return out

df_raw = load_data(scope)
df = postprocess(df_raw, only_with_yahoo)

st.success(f"{len(df):,} lignes prêtes.")
st.dataframe(df, use_container_width=True, height=520)

csv_bytes = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Télécharger le CSV", data=csv_bytes, file_name=filename, mime="text/csv")

st.caption("⚠️ Vérifie toujours l'éligibilité PEA auprès de ton courtier. "
           "Cette liste est fournie à titre indicatif et peut évoluer.")
