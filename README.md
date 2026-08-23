# 🇮🇹 Product Gap Monitor Italia

App di ricerca prodotto + monitoraggio continuativo del **gap di mercato Italia**
rispetto a USA / Canada / UK / Australia, per trovare prodotti virali all'estero
prima che arrivino sul mercato italiano (store mono-prodotto Shopify).

Implementa esattamente i 4 segnali del tuo metodo:

| Segnale | Sorgente | Automazione |
|---|---|---|
| **Google Trends IT vs Globale** (ratio 5-10x + curva IT in salita) | pytrends (API non ufficiale di Google Trends) | ✅ Automatica |
| **TikTok Creative Center → Top Products → Italia** | Sito TikTok (nessuna API pubblica) | ⚠️ Manuale (2 min) |
| **Meta Ads Library → paese Italia** (0 advertiser = gap reale) | Sito Meta (nessuna API gratuita) | ⚠️ Manuale (3 min) |
| **Amazon.it** (conta venditori con >1000 recensioni, <5-6 = non presidiato) | Ricerca su amazon.it / output del tool ricerca prodotto | ⚠️ Semi-manuale (incolla e conta in automatico) |

> **Onestà sui dati**: Google Trends è l'unico segnale automatizzato in tempo
> reale, tramite la libreria non ufficiale `pytrends` (può andare in errore 429
> se usata troppo: l'app inserisce pause e registra i fallimenti, non inventa
> numeri). TikTok e Meta non espongono API pubbliche: l'app NON simula quei dati,
> ti guida alla verifica manuale e li salva per lo storico. Amazon si alimenta
> con conteggio manuale o incollando l'output dell'elenco risultati.

## Installazione

```bash
# Python 3.10+
cd product-gap-monitor
pip install -r requirements.txt
```

## Quickstart

```bash
# 1. (opzionale) carica i 3 prodotti esempio con snapshot dimostrativi
python -m product_gap seed

# 2. dashboard
streamlit run app.py

# 3. aggiornamento Google Trends live (da CLI o pulsante "Scansiona ora" in dashboard)
python -m product_gap scan
```

### Verifica manuale settimanale (2 valori da inserire nel pannello prodotto)

1. **TikTok**: https://ads.tiktok.com/business/creativecenter/inspiration/popular-products/pc/it — paese Italia, ultimi 30 giorni → `presente`/`assente`.
2. **Meta Ads**: https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=IT&q=<keyword> — conta gli inserzionisti attivi distinti → `0` = nessuno spende = **gap reale**.
3. **Amazon.it**: cerca il prodotto e conta i listing con >1000 recensioni, oppure incolla l'elenco risultati del tool ricerca prodotto dell'assistente (conteggio automatico).

## CLI

```bash
python -m product_gap list                 # tabella verdetti
python -m product_gap scan                 # aggiorna Google Trends live di tutti i prodotti
python -m product_gap trends --keyword "heatless curls"   # confronto IT vs Globale senza salvare
python -m product_gap add --name "..." --category "..."   # nuovo prodotto
python -m product_gap score --id 1         # ricalcola un prodotto con dati live
python -m product_gap export --out storico.csv            # esporta storico per Excel
```

## Verdetto

Il motore combina SOLO le regole necessarie (config.yaml → `verdetto.regole_necessarie`):
tutte **ok** → 🟢 **GAP APERTO**; nessun **ko** ma dati mancanti → 🟡 **gap probabile**;
almeno una **ko** → 🛑 **mercato presidiato** (evita o differenziati).
Soglie modificabili in `config.yaml` o nella pagina ⚙️ Regole.

## Limiti legali e tecnici

- `pytrends` usa l'API non ufficiale di Google Trends: i volumi sono **normalizzati
  per serie geografica** — il rapporto Globale/IT è indicativo, non assoluto.
  Rispetta i limiti di frequenza, oppure usa la pagina "Regole" per i tuoi range.
- TikTok Creative Center e Meta Ads Library: nessuno scraping automatizzato;
  verifica manuale dal browser. Rispetta i Termini di servizio delle piattaforme.
- Amazon.it: non fare scraping aggressivo; usa conteggio manuale o ricerca assistita.
- Il DB (SQLite) salva lo **storico**: la dashboard mostra trend di ratio e volume.

## Monitoraggio continuativo

C'è anche un workflow ricorrente (settimanale) che controlla i segnali web del
gap (nuovi store/seller in Italia, ads attive, presenza TikTok) e pubblica un
report: trovi il card "Enable Workflow" per attivarlo.
