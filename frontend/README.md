# BeeBus Fatture Extractor - Frontend

Interfaccia web moderna per l'estrazione automatica di dati da fatture carburante (IP, Esso, Q8).

## 🚀 Quick Start

### 1. Configurazione

Modifica `config.js` e imposta l'URL del backend:

```javascript
const CONFIG = {
    API_BASE_URL: 'https://tuo-app.railway.app', // ← MODIFICA QUESTO
    // ...
};
```

### 2. Test Locale

Apri semplicemente `index.html` nel browser oppure usa un server locale:

```bash
# Opzione 1: Python
python -m http.server 8080

# Opzione 2: Node.js (con npx)
npx serve .

# Opzione 3: VS Code Live Server
# Installa estensione "Live Server" e clicca "Go Live"
```

Poi apri: http://localhost:8080

### 3. Deploy Production

#### **Opzione A: Railway (consigliato)**

1. Crea nuovo progetto su Railway
2. Connetti al repository GitHub
3. Railway detecterà automaticamente i file statici
4. Deploy automatico ad ogni push

#### **Opzione B: Netlify**

```bash
# Installa Netlify CLI
npm install -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod
```

#### **Opzione C: Vercel**

```bash
# Installa Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

#### **Opzione D: GitHub Pages**

1. Vai su repository → Settings → Pages
2. Source: Deploy from branch
3. Branch: main
4. Folder: /frontend
5. Save

## 📁 Struttura File

```
frontend/
├── index.html      # Interfaccia principale
├── style.css       # Styling moderno
├── app.js          # Logica applicazione
├── config.js       # Configurazione API
└── README.md       # Questo file
```

## 🔧 Configurazione CORS

Assicurati che il backend abbia CORS configurato correttamente in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tuo-frontend.netlify.app",
        "https://tuo-dominio.com",
        "http://localhost:8080"  # Per development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## ✨ Features

- ✅ Upload multiplo file PDF (drag & drop)
- ✅ Anteprima file caricati
- ✅ Progress bar durante elaborazione
- ✅ Download automatico CSV
- ✅ Support per IP, Esso, Q8
- ✅ Design responsive (mobile-friendly)
- ✅ Gestione errori user-friendly

## 🎨 Personalizzazione

### Colori

Modifica le variabili CSS in `style.css`:

```css
:root {
    --primary: #667eea;        /* Colore primario */
    --secondary: #764ba2;      /* Colore secondario */
    --success: #10b981;        /* Verde successo */
    --error: #ef4444;          /* Rosso errore */
    /* ... */
}
```

### Logo

Sostituisci l'SVG nell'header di `index.html` o aggiungi un'immagine:

```html
<div class="logo">
    <img src="logo.png" alt="BeeBus" width="32">
    <span>BeeBus Fatture Extractor</span>
</div>
```

## 🐛 Troubleshooting

### CORS Error

Se vedi errori CORS nella console:
1. Verifica che `API_BASE_URL` in `config.js` sia corretto
2. Controlla che il backend abbia CORS configurato
3. Verifica che l'origine del frontend sia nella whitelist

### File non si carica

1. Verifica che sia un PDF valido
2. Controlla dimensione (max 50MB)
3. Verifica che il backend sia raggiungibile

### CSV vuoto

1. Verifica che la fattura sia in formato supportato (IP/Esso/Q8)
2. Controlla i log del backend per errori
3. Testa con le fatture di esempio

## 📞 Supporto

- GitHub Issues: https://github.com/dandele/fastapi/issues
- Documentazione API: https://tuo-app.railway.app/docs

## 📄 Licenza

Proprietario: BeeBus SPA