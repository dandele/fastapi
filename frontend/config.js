/**
 * Configurazione API
 *
 * IMPORTANTE: Modifica API_BASE_URL con l'URL del tuo backend Railway
 *
 * Esempi:
 * - Development locale: 'http://localhost:8000'
 * - Railway production: 'https://tuo-app.railway.app'
 * - Custom domain: 'https://api.tuodominio.com'
 */

const CONFIG = {
    // URL base dell'API (MODIFICA QUESTO!)
    //API_BASE_URL: 'http://localhost:8000',
    API_BASE_URL: 'https://fastapi-production-2a3a.up.railway.app',

    // Endpoint specifici
    ENDPOINTS: {
        DOWNLOAD_CSV: '/download-csv',
        HEALTH: '/health',
        SUPPORTED_PROVIDERS: '/supported-providers'
    },

    // Limiti file
    MAX_FILE_SIZE: 50 * 1024 * 1024, // 50MB
    MAX_FILES: 10,
    ALLOWED_EXTENSIONS: ['.pdf'],

    // Timeout upload (in ms)
    UPLOAD_TIMEOUT: 120000, // 2 minuti

    // Debug mode (mostra log nella console)
    DEBUG: true
};

// Funzione helper per logging
function log(...args) {
    if (CONFIG.DEBUG) {
        console.log('[BeeBus]', ...args);
    }
}

// Funzione per ottenere URL completo
function getApiUrl(endpoint) {
    return CONFIG.API_BASE_URL + endpoint;
}