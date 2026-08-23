"""Product Gap Monitor Italia - dashboard Streamlit.

Avvio:  streamlit run app.py
Prima:  pip install -r requirements.txt && python -m product_gap seed
"""
import json
import os
from datetime import date

import pandas as pd
import streamlit as st
import yaml

import analytics, db
import amazon, google_trends, meta, tiktok
from keywords import suggerisci_keyword
from scoring import load_config, score_snapshot

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")

st.set_page_config(page_title="Product Gap Monitor Italia", page_icon="🇮🇹", layout="wide")

EMOJI = {"ok": "✅", "ko": "🛑", "sconosciuto": "❓"}


@st.cache_resource
def conn():
    c = db.get_conn()
    db.init_db(c)
    return c


def salva_snapshot(pid, d):
    cfg = load_config()
    res = score_snapshot(cfg, d)
    d["verdict"], d["label"] = res["verdict"], res["label"]
    d["rules_json"] = json.dumps(res["rules"], ensure_ascii=False)
    d["score"] = res["score"]
    db.add_snapshot(conn(), pid, d)
    return res


def pagina_regole():
    st.header("⚙️ Regole del motore di scoring")
    st.caption("Soglie configurabili: l'app le rilegge a ogni azione. Salva per renderle attive.")
    cfg = load_config()
    r = cfg["regole"]
    with st.form("regole_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("Google Trends")
            rmin = st.number_input("Rapporto volume Globale/IT - minimo", value=float(r["google_trends"]["rapporto_volume_min"]), step=0.5)
            rmax = st.number_input("Rapporto volume Globale/IT - massimo", value=float(r["google_trends"]["rapporto_volume_max"]), step=0.5)
            rich = st.checkbox("Richiedi curva IT in salita", value=bool(r["google_trends"]["richiedi_trend_it_in_salita"]))
        with c2:
            st.subheader("Meta Ads Library 🇮🇹")
            soc = st.number_input("Max inserzionisti attivi in Italia", value=int(r["meta_ads_italia"]["max_inserzionisti_attivi_it"]), step=1)
            st.subheader("Amazon.it")
            amz = st.number_input("Max venditori con >1000 recensioni", value=int(r["amazon_it"]["max_venditori_oltre_1000_recensioni"]), step=1)
        with c3:
            st.subheader("Verdetto")
            st.write("Regole necessarie per GAP APERTO:")
            st.write("🟢 google_trends, meta_ads_italia, amazon_it")
        if st.form_submit_button("💾 Salva regole"):
            r["google_trends"]["rapporto_volume_min"] = float(rmin)
            r["google_trends"]["rapporto_volume_max"] = float(rmax)
            r["google_trends"]["richiedi_trend_it_in_salita"] = bool(rich)
            r["meta_ads_italia"]["max_inserzionisti_attivi_it"] = int(soc)
            r["amazon_it"]["max_venditori_oltre_1000_recensioni"] = int(amz)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)
            st.success("Regole salvate in config.yaml")


def pagina_nuovo():
    st.header("➕ Nuovo prodotto da monitorare")
    with st.form("nuovo_prodotto"):
        name = st.text_input("Nome prodotto*")
        cat = st.text_input("Categoria", placeholder="es. Wellness, Bellezza, Casa...")
        desc = st.text_input("Descrizione / fonte trend", placeholder="es. link articolo trend o Amazon US")
        kw = st.text_input(
            "Keyword Google Trends (opzionale)",
            placeholder="lascia vuoto = dedotta dal nome (es. testo tra parentesi)",
            help="Se vuota, viene generata automaticamente dal nome. Per il trend globale conviene una keyword in inglese.",
        )
        c1, c2, c3 = st.columns(3)
        tk = c1.selectbox("TikTok Creative Center Italia", ["", "presente", "assente"], format_func=lambda x: {"": "Da verificare manualmente", "presente": "Presente nei Top Products", "assente": "Assente"}.get(x, x))
        meta_n = c2.number_input("Inserzionisti attivi Meta IT (0 = nessuno)", value=0, min_value=0, step=1)
        amz_n = c3.number_input("Venditori Amazon.it >1000 recensioni (lascia vuoto se non verificato)", value=None, min_value=0, step=1)
        if st.form_submit_button("🚀 Aggiungi e valuta"):
            if not name:
                st.error("Il nome è obbligatorio")
            else:
                kw_finale = kw.strip() or suggerisci_keyword(name)
                if not kw.strip():
                    st.info(f"Keyword generata automaticamente dal nome: «{kw_finale}» (modificabile nel dettaglio prodotto).")
                slug = name.lower().replace(" ", "-").replace("/", "-")
                pid = db.add_product(conn(), name, slug, cat, desc, "")
                d = {
                    "keyword": kw_finale,
                    "trend_it_volume": None,
                    "trend_global_volume": None,
                    "tiktok_it": tk,
                    "meta_advertisers_it": int(meta_n),
                    "amazon_sellers_over_1000": amz_n,
                    "note": "Inserito manualmente; avvia 'Scansiona ora' per i dati Google Trends.",
                }
                res = salva_snapshot(pid, d)
                st.success(f"Aggiunto: {res['label']}")


def pagina_dashboard():
    st.header("📊 Dashboard prodotti monitorati")
    rows = db.all_with_latest(conn())
    if not rows:
        st.info("Nessun prodotto. Vai su '➕ Nuovo prodotto' oppure esegui: python -m product_gap seed")
        return
    cfg = load_config()
    data = []
    for r in rows:
        s = r["snapshot"] or {}
        data.append(
            {
                "id": r["id"],
                "Prodotto": r["name"],
                "Categoria": r["category"],
                "Verdetto": s.get("label", "⚪ nessun dato"),
                "Score": analytics.score_da_snapshot(cfg, s),
                "Rapporto GL/IT": s.get("trend_ratio"),
                "Direzione IT": s.get("trend_it_direction"),
                "TikTok IT": s.get("tiktok_it"),
                "Ads Meta IT": s.get("meta_advertisers_it"),
                "Venditori >1000 rec": s.get("amazon_sellers_over_1000"),
                "Ultimo rilevamento": s.get("snapshot_date"),
            }
        )
    df = pd.DataFrame(data)
    if "Score" in df.columns:
        df = df.sort_values("Score", ascending=False)
    st.dataframe(df, use_container_width=True, hide_index=True)
    dl1, dl2 = st.columns(2)
    dl1.download_button(
        "⬇️ Prodotti monitorati (ultimo rilevamento)",
        df.to_csv(index=False).encode("utf-8-sig"),
        "prodotti_monitorati.csv",
        "text/csv",
        use_container_width=True,
    )
    storico = db.all_snapshots_with_product(conn())
    if storico:
        df_storico = pd.DataFrame([dict(r) for r in storico])
        dl2.download_button(
            "⬇️ Storico completo (tutti gli snapshot)",
            df_storico.to_csv(index=False).encode("utf-8-sig"),
            "storico_snapshot.csv",
            "text/csv",
            use_container_width=True,
            help="Ogni rilevamento salvato nel tempo per ogni prodotto: utile per Excel e per vedere l'evoluzione del gap.",
        )
    if st.button("🔁 Scansiona ora (Google Trends live)"):
        with st.spinner("Recupero Google Trends IT vs Globale per tutti i prodotti..."):
            cfg = load_config()
            oggi = date.today().isoformat()
            for r in rows:
                s = r["snapshot"] or {}
                kw = s.get("keyword") or r["name"]
                try:
                    d = google_trends.fetch_italia_vs_globale(kw)
                except Exception as e:
                    st.warning(f"{r['name']}: Google Trends non raggiungibile ({e})")
                    continue
                d.update(
                    {
                        "tiktok_it": s.get("tiktok_it"),
                        "meta_advertisers_it": s.get("meta_advertisers_it"),
                        "amazon_sellers_over_1000": s.get("amazon_sellers_over_1000"),
                        "snapshot_date": oggi,
                        "note": "Aggiornato da dashboard (Google Trends live).",
                    }
                )
                res = salva_snapshot(r["id"], d)
                st.write(f"- {r['name']}: ratio {d.get('trend_ratio')}x, {d.get('trend_it_direction')} → {res['label']}")
            st.success("Scansione completata")
            st.rerun()


def pagina_dettaglio():
    st.header("🔎 Dettaglio prodotto")
    rows = db.all_with_latest(conn())
    if not rows:
        st.info("Nessun prodotto in archivio")
        return
    opts = {f"{r['name']} (id {r['id']})": r for r in rows}
    scelta = st.selectbox("Prodotto", list(opts.keys()))
    r = opts[scelta]
    pid = r["id"]
    s = r["snapshot"] or {}
    st.subheader(r["name"])
    if r["category"]:
        st.caption(f"{r['category']} — {r['description'] or ''}")
    if r["source_url"]:
        st.markdown(f"[Fonte trend]({r['source_url']})")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Rapporto Globale/IT", f"{s.get('trend_ratio')}x" if s.get("trend_ratio") else "—",
              help="Volume globale normalizzato / volume Italia normalizzato (pytrends, 12 mesi)")
    c2.metric("Direzione curva IT", s.get("trend_it_direction") or "—")
    c3.metric("Ads Meta attivi IT", s.get("meta_advertisers_it") if s.get("meta_advertisers_it") is not None else "—")
    c4.metric("Venditori AMZ >1000 rec", s.get("amazon_sellers_over_1000") if s.get("amazon_sellers_over_1000") is not None else "—")
    sc = s.get("score") if s.get("score") is not None else analytics.score_da_snapshot(load_config(), s)
    c5.metric("Score gap (0-100)", f"{sc}" if sc is not None else "—",
              help="Media pesata dei segnali: 100 = gap completamente aperto, 0 = mercato presidiato")

    if s.get("label"):
        st.markdown(f"### Verdetto attuale: {s['label']}")
    hist0 = db.history(conn(), pid)
    if len(hist0) >= 2:
        for a in analytics.delta_alert(load_config(), dict(hist0[-2]), dict(hist0[-1])):
            st.warning(a)
    if s.get("note"):
        st.caption(f"Nota: {s['note']}")

    with st.expander("🧩 Breakdown regole dell'ultimo rilevamento"):
        try:
            rules = json.loads(s.get("rules_json") or "{}")
            for k, v in rules.items():
                st.markdown(f"{EMOJI.get(v['stato'], '❓')} **{k}** — {v['dettaglio']}")
        except Exception:
            st.write("Nessun dettaglio salvato.")

    st.markdown("---")
    st.subheader("✏️ Aggiorna segnali manuali")
    st.caption("TikTok Creative Center e Meta Ads Library non hanno API pubbliche: i valori qui sono la tua verifica manuale. Amazon può essere incollato.")
    with st.form(f"update_{pid}"):
        col1, col2 = st.columns(2)
        tk = col1.selectbox("TikTok Creative Center Italia", ["", "presente", "assente"], index=["", "presente", "assente"].index(s.get("tiktok_it") or ""))
        meta_n = col1.number_input("Inserzionisti attivi Meta IT", value=int(s.get("meta_advertisers_it") or 0), min_value=0, step=1)
        amz_n = col2.number_input("Venditori Amazon.it >1000 recensioni", value=int(s.get("amazon_sellers_over_1000") or 0), min_value=0, step=1)
        incolla = col2.text_area("Oppure incolla l'output ricerca Amazon (conta automatico)", height=90)
        note = st.text_input("Nota del rilevamento", value="Verifica manuale settimanale.")
        if st.form_submit_button("💾 Salva e ricalcola"):
            amz_finale = amazon.conta_da_incolla(incolla) if incolla.strip() else int(amz_n)
            d = {
                "keyword": s.get("keyword") or r["name"],
                "trend_it_volume": s.get("trend_it_volume"),
                "trend_global_volume": s.get("trend_global_volume"),
                "trend_ratio": s.get("trend_ratio"),
                "trend_it_direction": s.get("trend_it_direction"),
                "tiktok_it": tk,
                "meta_advertisers_it": int(meta_n),
                "amazon_sellers_over_1000": amz_finale,
                "snapshot_date": date.today().isoformat(),
                "note": note,
            }
            res = salva_snapshot(pid, d)
            st.success(f"Aggiornato: {res['label']}")
            st.rerun()

    st.markdown("---")
    hist = db.history(conn(), pid)
    if len(hist) > 1:
        st.subheader("📈 Storico dei rilevamenti")
        dfh = pd.DataFrame(hist)[["snapshot_date", "trend_ratio", "trend_it_volume", "verdict"]]
        dfh["snapshot_date"] = pd.to_datetime(dfh["snapshot_date"])
        dfh = dfh.set_index("snapshot_date")
        st.line_chart(dfh[["trend_ratio"]])
        st.line_chart(dfh[["trend_it_volume"]])
        st.dataframe(dfh, use_container_width=True)


def main():
    try:
        if not db.list_products(conn()):
            import seed_example
            seed_example.esegui()
            st.sidebar.info("🟢 DB vuoto: ricaricati i 3 prodotti esempio.")
    except Exception as e:
        st.sidebar.warning(f"Auto-seed non riuscito: {e}")

    st.sidebar.title("🇮🇹 Product Gap Monitor")
    st.sidebar.caption("Ricerca prodotto + monitoraggio continuativo del gap Italia (USA/CA/UK/AU vs IT)")
    pagina = st.sidebar.radio(
        "Navigazione",
        ["📊 Dashboard", "🔎 Dettaglio prodotto", "➕ Nuovo prodotto", "⚙️ Regole"],
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "**Come funziona:**\n"
        "1. **Google Trends**: automatizzato (pytrends), ratio Globale/IT 5-10x + curva IT in salita\n"
        "2. **TikTok Creative Center IT**: verifica manuale (nessuna API pubblica)\n"
        "3. **Meta Ads Library IT**: verifica manuale — 0 advertiser = gap reale\n"
        "4. **Amazon.it**: conteggio manuale o incolla-output — <5-6 venditori forti = non presidiato"
    )
    st.sidebar.info("Monitoraggio settimanale: il workflow ricorrente controlla i segnali o ti ricorda di lanciare `python -m product_gap scan`.")

    if pagina.startswith("📊"):
        pagina_dashboard()
    elif pagina.startswith("🔎"):
        pagina_dettaglio()
    elif pagina.startswith("➕"):
        pagina_nuovo()
    else:
        pagina_regole()


if __name__ == "__main__":
    main()
