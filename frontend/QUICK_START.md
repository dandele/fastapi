# 🚀 Quick Start - Frontend BeeBus

## 1️⃣ Test Locale (5 minuti)

### Setup

1. **Apri config.js** e verifica l'URL del backend:
   ```javascript
   API_BASE_URL: 'http://localhost:8000'  // Per test locale
   ```

2. **Avvia backend** (in altra finestra terminale):
   ```bash
   cd /Users/mirkopapadopoli/Code/fastapi
   python main.py
   ```

3. **Apri frontend**:
   ```bash
   # Opzione A: Doppio click su index.html
   open index.html

   # Opzione B: Python server
   cd frontend
   python -m http.server 8080
   # Poi apri: http://localhost:8080
   ```

### Test

1. Trascina un PDF (da `../Fatture/`)
2. Clicca "Estrai Dati e Scarica CSV"
3. Verifica download CSV

---

## 2️⃣ Deploy Production (10 minuti)

### Backend (Railway)

```bash
# 1. Push su GitHub
git add .
git commit -m "Frontend complete"
git push origin main

# 2. Railway auto-deploy
# Attendi 2 minuti, poi copia URL: https://xxx.railway.app
```

### Frontend (Netlify)

1. Vai su https://app.netlify.com
2. Drag & drop cartella `frontend/`
3. Attendi 30 secondi
4. Ottieni URL: https://xxx.netlify.app

### Collega

1. **Apri:** `frontend/config.js`
2. **Cambia:**
   ```javascript
   API_BASE_URL: 'https://tuo-app.railway.app'
   ```
3. **Re-upload** su Netlify

---

## 3️⃣ Verifica Funzionamento

✅ Frontend carica: `https://tuo-site.netlify.app`
✅ Backend risponde: `https://tuo-app.railway.app/health`
✅ CORS ok: Nessun errore nella console browser
✅ Upload funziona: CSV scaricato correttamente

---

## 🆘 Help

- **CORS Error?** → Verifica `API_BASE_URL` in `config.js`
- **404?** → Verifica che backend sia online
- **Timeout?** → File troppo grandi o lenti

**Docs completa:** Vedi `DEPLOYMENT.md`