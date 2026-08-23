# ☁️ Deploy su Streamlit Community Cloud (gratis)

Con questa procedura l'app è **online a un URL pubblico** e la apri dal browser
del telefono (Android/iPhone) e da qualsiasi altro dispositivo, senza installare
nulla. Il monitoraggio richiede però due accortezze, spiegate in fondo — leggi
la sezione "⚠️ Persistenza e limiti" prima di partire.

## Serve (5 minuti totali)

1. Un account **GitHub** (gratis): https://github.com/signup
2. Un account **Streamlit Community Cloud** (gratis): https://share.streamlit.io
   (o https://streamlit.io/cloud — entra con il tuo GitHub)

## Passo 1 — Carica i file su GitHub

1. Su GitHub: **New repository** → nome es. `product-gap-monitor` → **Public** (il
   piano gratuito di Streamlit Cloud richiede repo pubblico) → **Create**.
2. Nella pagina del repo: **"uploading an existing file"**.
3. Trascina dalla cartella `product-gap-monitor` questi file (TUTTI questi):
   - `app.py`
   - `config.yaml`
   - `requirements.txt`
   - `README.md`
   - la cartella `.streamlit/` (contiene `config.toml`)
   - la cartella `product_gap/` (contiene tutti i `.py` dell'app)
4. Clicca **Commit changes**.
   > Non caricare la cartella `data/` (il DB si rigenera da solo, vedi sotto).

## Passo 2 — Collega Streamlit Cloud

1. Vai su https://share.streamlit.io e accedi con GitHub.
2. **New app** → scegli il repository `product-gap-monitor`.
3. Campo **Main file path**: lascia `app.py`.
4. **Deploy!**

Dopo 1-3 minuti l'app è online all'indirizzo:
```
https://<nome-account>.streamlit.app
```
Apri questo URL dal browser del telefono: la dashboard è ottimizzata e si usa
come da PC.

## Passo 3 — Configura il monitoraggio

- **Google Trends**: clicca **"🔁 Scansiona ora"** nella Dashboard: l'app scarica
  i dati live IT vs Globale per tutti i prodotti.
- **Verifica manuale settimanale** (TikTok Creative Center e Meta Ads Library):
  la fai dal browser del telefono, come da app — apri i link indicati nel
  pannello prodotto e inserisci i valori; verranno salvati nello storico.

## ⚠️ Persistenza e limiti (importanti, onestà sui dati)

- **Il DB SQLite su Community Cloud è VOLATILE**: quando l'app va in sleep dopo
  un periodo di inattività, il riavvio ricrea il database; i prodotti tornano ai
  3 esempio (auto-seed) e lo storico si perde. L'app è quindi perfetta per
  **provare e usare in modo interattivo**, ma NON è un archivio duraturo.
- Se vuoi **storico persistente** e monitoraggio programmato vero, le opzioni:
  a) **Render / Railway** con volume disco (piccola spesa mensile);
  b) aggiunta futura di un database esterno tipo **Supabase** (gratis, cloud).
  Dimmi se ti serve una delle due e la integro.
- **Google Trends dal cloud**: pytrends può rispondere con errori 429 se
  chiamato troppo spesso; l'app registra i fallimenti senza inventare dati.
  Con l'uso normale (qualche scan al giorno) funziona.
- Il piano gratuito di Streamlit Cloud **richiede repo GitHub pubblici**:
  non caricare dati sensibili (l'app non ne contiene).

## Aggiornamenti futuri

Modifichi i file localmente → fai **commit e push** su GitHub → Streamlit Cloud
**risincronizza automaticamente** e l'URL resta lo stesso. Nessuna
reinstallazione sul telefono.
