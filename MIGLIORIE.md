# Migliorie applicate

## 1. App resa funzionante (era rotta)
Lo zip originale aveva tutti i file appiattiti nella cartella radice, ma il codice
è scritto come pacchetto Python. Ripristinata la struttura corretta:

```
product-gap-monitor/
├── app.py                 # dashboard Streamlit (root)
├── config.yaml            # soglie
├── requirements.txt
├── test_scoring.py
├── test_amazon.py         # nuovo
└── product_gap/           # pacchetto
    ├── __init__.py
    ├── __main__.py
    ├── cli.py
    ├── scoring.py
    ├── analytics.py
    ├── db.py
    ├── seed_example.py
    └── adapters/          # sotto-pacchetto
        ├── __init__.py
        ├── google_trends.py
        ├── amazon.py
        ├── meta.py
        └── tiktok.py
```

## 2. Bug corretto: conteggio recensioni Amazon
Il parser leggeva male i numeri in formato USA (`1,234 reviews` risultava 1,2 e
veniva scartato) e ignorava "ratings / valutazioni / voti". Ora normalizza sia il
formato italiano (`1.234`) sia quello USA (`1,234`) e riconosce più diciture.
Nuova funzione `estrai_conteggi()` e soglia parametrica.

## 3. Efficienza: query DB N+1 eliminata
`all_with_latest()` faceva 1 query + 1 per ogni prodotto. Ora sono 2 query fisse
(window function `ROW_NUMBER`), a parità di risultato: la dashboard resta veloce
anche con molti prodotti.

## 4. Efficienza: config in cache
`load_config()` rileggeva `config.yaml` da disco a ogni chiamata (decine per render
in Streamlit). Ora è in cache con invalidazione su modifica del file: veloce ma
sempre reattivo ai cambi salvati dalla pagina Regole.

## 5. Robustezza Google Trends (pytrends)
- Retry automatico con backoff crescente sugli errori 429/timeout.
- Cache in memoria per-processo: la stessa keyword non viene interrogata due volte
  nello stesso scan.
- Messaggi d'errore chiari quando Google limita le richieste.

## 6. Bug prevenuto: SQLite + Streamlit
Connessione aperta con `check_same_thread=False` + `journal_mode=WAL`: evita
l'errore "SQLite objects created in a thread can only be used in that same thread"
tipico di Streamlit.

## 7. Aggiunti test e .gitignore
`test_amazon.py` blocca la correzione del parser. Totale test: 13, tutti verdi
(`python -m unittest test_scoring test_amazon`).

## 8. Auto-generazione keyword dal nome prodotto
Nuovo modulo `keywords.py`. Nel form "Nuovo prodotto" la keyword è ora
**opzionale**: se la lasci vuota viene dedotta dal nome. Se il nome contiene un
termine tra parentesi (es. "Bigodini senza calore (heatless curls)") usa quello
— di solito è il termine virale in inglese, ideale per il trend globale. La stessa
logica è usata come fallback anche da `python -m product_gap scan`.

## 9. Export storico completo dalla dashboard
In Dashboard, accanto al download dei prodotti (ultimo rilevamento), c'è un nuovo
pulsante **"Storico completo (tutti gli snapshot)"**: scarica in CSV ogni
rilevamento salvato nel tempo per ogni prodotto, pronto per Excel. Query dedicata
`all_snapshots_with_product()` (una sola query).
