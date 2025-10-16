\
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
}

# Exemple d'extractions depuis les URLs d'instruments ProRealTime :
#   /fr/web/xpar-ai/air-liquide  -> exchange = xpar, ticker = ai
#   /en/web/xetr-tgt/11-88-0-solutions-ag -> exchange = xetr, ticker = tgt
PRT_LINK_RE = re.compile(r"/web/([a-z]{4})-([a-z0-9._-]+)/", re.I)

YAHOO_SUFFIX = {
    "xpar": ".PA",   # Paris
    "xams": ".AS",   # Amsterdam
    "xbru": ".BR",   # Brussels
    "xlis": ".LS",   # Lisbon
    "xdub": ".IR",   # Dublin
    "xetr": ".DE",   # Xetra
    "xfra": ".F",    # Frankfurt (floor)
    "xmad": ".MC",   # Madrid
    "xmce": ".MC",
    "xmil": ".MI",   # Milan
    "xsto": ".ST",   # Stockholm
    "xhel": ".HE",   # Helsinki
    "xcse": ".CO",   # Copenhagen
    "xosl": ".OL",   # Oslo
    "xwbo": ".VI",   # Vienna
}

def _fetch_prorealtime_list(url: str, scope_label: str) -> pd.DataFrame:
    resp = requests.get(url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    rows = []
    for a in soup.find_all("a", href=True):
        m = PRT_LINK_RE.search(a["href"])
        if not m:
            continue
        exch, tick = m.group(1).lower(), m.group(2).upper()
        name = a.get_text(strip=True)
        if not name or len(name) < 2:
            continue
        suffix = YAHOO_SUFFIX.get(exch, "")
        yahoo = f"{tick}{suffix}" if suffix else None
        rows.append({
            "ticker": tick,
            "name": name,
            "exchange_code": exch.upper(),
            "yahoo_symbol": yahoo,
            "source": url,
            "scope": scope_label,
            "pea_eligible": True,
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.drop_duplicates(subset=["ticker","exchange_code"])
    return df

def fetch_pea_fr() -> pd.DataFrame:
    """Actions FR éligibles PEA (ProRealTime)."""
    url = "https://www.prorealtime.com/fr/financial-instruments/actions-eligibles-pea"
    return _fetch_prorealtime_list(url, "FR")

def fetch_pea_eee() -> pd.DataFrame:
    """Actions EEE éligibles PEA (ProRealTime)."""
    url = "https://www.prorealtime.com/fr/financial-instruments/actions-eee-eligibles-pea"
    return _fetch_prorealtime_list(url, "EEE")

def fetch_pea_all() -> pd.DataFrame:
    """Union FR + EEE, avec déduplication."""
    fr = fetch_pea_fr()
    eea = fetch_pea_eee()
    if fr.empty and eea.empty:
        return pd.DataFrame(columns=["symbol","ticker","yahoo_symbol","name","exchange_code","scope","pea_eligible","source"])
    all_df = pd.concat([fr, eea], ignore_index=True)
    # Colonne symbol pour compatibilité screener (priorité Yahoo, sinon ticker)
    all_df["symbol"] = all_df["yahoo_symbol"].fillna(all_df["ticker"])
    all_df = all_df.drop_duplicates(subset=["ticker","exchange_code"]).reset_index(drop=True)
    # Ordonne les colonnes importantes
    cols = ["symbol","ticker","yahoo_symbol","name","exchange_code","scope","pea_eligible","source"]
    return all_df[cols]
