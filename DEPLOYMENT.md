# 🚀 Guida Completa al Deployment

BeeBus Fatture Extractor - Deployment Backend + Frontend

## 📋 Architettura

```
┌─────────────────┐      HTTPS      ┌──────────────────┐
│   Frontend      │  ────────────>  │    Backend       │
│  (Netlify/      │                  │   (Railway)      │
│   Vercel)       │  <────────────  │   FastAPI        │
└─────────────────┘      JSON/CSV    └──────────────────┘
```

---

## 🔧 PARTE 1: Deploy Backend (Railway)

### Step 1: Verifica File

Assicurati di avere questi file nella root:
- ✅ `main.py`
- ✅ `requirements.txt`
- ✅ `railway.json`
- ✅ `extractors/` (cartella)
- ✅ `models/` (cartella)

### Step 2: Push su GitHub

```bash
cd /Users/mirkopapadopoli/Code/fastapi

# Aggiungi tutti i file
git add .

# Commit
git commit -m "Add frontend and complete backend implementation"

# Push
git push origin main
```

### Step 3: Deploy su Railway

1. Vai su https://railway.app/dashboard
2. **New Project** → **Deploy from GitHub repo**
3. Seleziona: `dandele/fastapi`
4. Railway detecterà automaticamente:
   - `railway.json`
   - Python/FastAPI
5. Il deploy inizierà automaticamente (2-3 minuti)

### Step 4: Ottieni URL Backend

Dopo il deploy:
1. Vai su **Settings** → **Networking**
2. Clicca **Generate Domain**
3. Ottieni URL tipo: `https://tuo-app.up.railway.app`
4. **COPIA QUESTO URL** - lo userai per il frontend!

### Step 5: Verifica Backend

```bash
# Health check
curl https://tuo-app.railway.app/health

# Docs
https://tuo-app.railway.app/docs
```

**✅ Backend OK!** Passiamo al frontend.

---

## 🎨 PARTE 2: Deploy Frontend

### Opzione A: Netlify (Consigliata)

#### Metodo 1: Deploy da GitHub (Auto)

1. Vai su https://app.netlify.com
2. **New site** → **Import from Git**
3. Connetti GitHub
4. Repository: `dandele/fastapi`
5. Build settings:
   ```
   Base directory: frontend
   Build command: (lascia vuoto)
   Publish directory: frontend
   ```
6. **Deploy site**

#### Metodo 2: Deploy manuale (Drag & Drop)

1. Vai su https://app.netlify.com
2. Drag & drop la cartella `frontend/` nell'area di upload
3. Attendi deploy (30 secondi)

**Ottieni URL:** `https://tuo-site.netlify.app`

### Opzione B: Vercel

```bash
# Installa Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod

# Segui wizard, alla fine ottieni URL
```

### Opzione C: Railway (anche frontend)

1. **New Project** → **Deploy from GitHub repo**
2. Repository: `dandele/fastapi`
3. **Settings** → **Root Directory**: `frontend`
4. Railway detecterà static HTML
5. Deploy automatico

---

## 🔗 PARTE 3: Collega Frontend a Backend

### Step 1: Aggiorna config.js

Nel file `frontend/config.js`:

```javascript
const CONFIG = {
    // CAMBIA QUESTO con il tuo URL Railway!
    API_BASE_URL: 'https://tuo-app.railway.app',  // ← QUI!
    // ...
};
```

### Step 2: Commit e Push

```bash
git add frontend/config.js
git commit -m "Update frontend API URL"
git push origin main
```

Se hai usato:
- **Netlify/Vercel con GitHub**: Deploy automatico (1 minuto)
- **Deploy manuale**: Ri-fai upload della cartella `frontend/`

### Step 3: Aggiorna CORS (opzionale, per produzione)

Nel `main.py`, sostituisci:

```python
allow_origins=["*"],  # DEVELOPMENT
```

Con:

```python
allow_origins=[
    "https://tuo-site.netlify.app",
    "https://tuo-dominio.com",
    "http://localhost:8080"  # Per test locali
],
```

Poi:
```bash
git add main.py
git commit -m "Update CORS origins"
git push origin main
```

Railway farà re-deploy automatico.

---

## ✅ PARTE 4: Test Completo

### 1. Apri Frontend

Vai su: `https://tuo-site.netlify.app`

### 2. Carica File di Test

Trascina uno dei PDF da `Fatture/`:
- `Fattura IP.pdf`
- `fattura esso.pdf`
- `fattura q8.pdf`

### 3. Clicca "Estrai Dati e Scarica CSV"

Dovresti:
1. Vedere progress bar
2. Download automatico del CSV
3. Vedere statistiche (file processati, record, importo)

### 4. Verifica CSV

Apri il CSV scaricato:
- Deve avere header: `Targa;Data_Rifornimento;...`
- Deve contenere tutti i record estratti
- Valori corretti

---

## 🔍 Troubleshooting

### ❌ CORS Error

**Problema:** Console mostra errore CORS

**Soluzione:**
1. Verifica che `API_BASE_URL` in `config.js` sia corretto
2. Verifica che il backend sia raggiungibile: `curl https://tuo-backend.railway.app/health`
3. Verifica CORS nel `main.py`

### ❌ 404 Not Found

**Problema:** Frontend non carica

**Soluzione Netlify:**
- Verifica **Publish directory**: deve essere `frontend` o `.` (se sei dentro la cartella)

**Soluzione Vercel:**
- Aggiungi `vercel.json`:
```json
{
  "version": 2,
  "routes": [
    { "src": "/(.*)", "dest": "/" }
  ]
}
```

### ❌ Backend Timeout

**Problema:** Upload si blocca al 70%

**Soluzione:**
1. Riduci numero di file (max 10)
2. Verifica dimensione file (max 50MB)
3. Controlla log Railway: **View Logs**

### ❌ CSV Vuoto

**Problema:** CSV scaricato ma senza dati

**Soluzione:**
1. Verifica che le fatture siano IP/Esso/Q8
2. Controlla log backend: Railway → **View Logs**
3. Testa con fatture di esempio

---

## 📊 Monitoring & Logs

### Backend Logs (Railway)

1. Vai su Railway Dashboard
2. Seleziona progetto
3. **View Logs**
4. Filtra errori: cerca `ERROR` o `500`

### Frontend Logs (Netlify)

1. Netlify Dashboard → Site → **Functions**
2. **Deploy log** per errori di build
3. Browser Console (F12) per errori JavaScript

---

## 🔒 Produzione: Best Practices

### 1. Environment Variables (Railway)

Nel dashboard Railway:
- **Variables** → Add Variable:
  ```
  CORS_ORIGINS=https://tuo-site.netlify.app
  DEBUG=false
  MAX_FILE_SIZE_MB=50
  ```

### 2. Custom Domain

**Backend (Railway):**
1. Settings → Networking → **Custom Domain**
2. Aggiungi: `api.tuodominio.com`
3. Configura DNS: `CNAME → [railway-domain]`

**Frontend (Netlify):**
1. Domain settings → **Add custom domain**
2. Aggiungi: `app.tuodominio.com`
3. Netlify configura automaticamente HTTPS

### 3. Rate Limiting

Aggiungi al `main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/download-csv")
@limiter.limit("10/minute")  # Max 10 richieste al minuto
async def download_csv_file(...):
    ...
```

### 4. Autenticazione API Key

```python
from fastapi import Header, HTTPException

API_KEY = "tua-chiave-segreta"  # Metti in env variable!

async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(401, "Unauthorized")

@app.post("/download-csv", dependencies=[Depends(verify_api_key)])
async def download_csv_file(...):
    ...
```

Nel frontend `config.js`:
```javascript
const CONFIG = {
    API_KEY: 'tua-chiave-segreta',
    // ...
};
```

In `app.js`, aggiungi header:
```javascript
const response = await fetch(getApiUrl(CONFIG.ENDPOINTS.DOWNLOAD_CSV), {
    method: 'POST',
    headers: {
        'X-API-Key': CONFIG.API_KEY
    },
    body: formData
});
```

---

## 📱 URL Finali

Dopo il deployment completo, dovresti avere:

- 🔗 **Frontend:** https://beebus-fatture.netlify.app
- 🔗 **Backend API:** https://beebus-api.railway.app
- 🔗 **Docs:** https://beebus-api.railway.app/docs
- 🔗 **GitHub:** https://github.com/dandele/fastapi

---

## ✨ Next Steps

1. [ ] Test con clienti pilota
2. [ ] Monitoraggio errori (Sentry)
3. [ ] Analytics (Google Analytics)
4. [ ] Email notifiche per errori
5. [ ] Backup automatico dati estratti
6. [ ] Dashboard admin per statistiche

---

Buon deployment! 🚀