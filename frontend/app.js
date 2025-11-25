/**
 * BeeBus Fatture Extractor - Frontend Application
 * Gestisce upload, estrazione e download CSV
 */

// State
let selectedFiles = [];
let isUploading = false;  // Previene submit multipli

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const filesList = document.getElementById('filesList');
const filesContainer = document.getElementById('filesContainer');
const fileCount = document.getElementById('fileCount');
const actionButtons = document.getElementById('actionButtons');
const progressSection = document.getElementById('progressSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    log('App initialized');
    setupEventListeners();
    checkApiHealth();
});

// Setup Event Listeners
function setupEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);

    // Prevent default drag behavior on document
    document.addEventListener('dragover', (e) => e.preventDefault());
    document.addEventListener('drop', (e) => e.preventDefault());
}

// Check API Health
async function checkApiHealth() {
    try {
        const response = await fetch(getApiUrl(CONFIG.ENDPOINTS.HEALTH));
        const data = await response.json();
        log('API Health:', data);
    } catch (error) {
        log('API Health Check Failed:', error);
        showWarning('Backend non raggiungibile. Verifica che il server sia avviato.');
    }
}

// Handle File Selection
function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    addFiles(files);
}

// Handle Drag Over
function handleDragOver(event) {
    event.preventDefault();
    dropZone.classList.add('drag-over');
}

// Handle Drag Leave
function handleDragLeave(event) {
    event.preventDefault();
    dropZone.classList.remove('drag-over');
}

// Handle Drop
function handleDrop(event) {
    event.preventDefault();
    dropZone.classList.remove('drag-over');

    const files = Array.from(event.dataTransfer.files);
    addFiles(files);
}

// Add Files
function addFiles(files) {
    log('Adding files:', files);

    // Filter PDF files
    const pdfFiles = files.filter(file => {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showWarning(`File "${file.name}" ignorato: solo PDF sono supportati`);
            return false;
        }
        if (file.size > CONFIG.MAX_FILE_SIZE) {
            showWarning(`File "${file.name}" ignorato: dimensione massima 50MB`);
            return false;
        }
        return true;
    });

    // Check max files limit
    if (selectedFiles.length + pdfFiles.length > CONFIG.MAX_FILES) {
        showWarning(`Massimo ${CONFIG.MAX_FILES} file alla volta`);
        return;
    }

    // Add to selected files
    selectedFiles = [...selectedFiles, ...pdfFiles];

    // Update UI
    updateFilesList();
    showActionButtons();
}

// Update Files List
function updateFilesList() {
    if (selectedFiles.length === 0) {
        filesList.style.display = 'none';
        actionButtons.style.display = 'none';
        return;
    }

    filesList.style.display = 'block';
    fileCount.textContent = selectedFiles.length;

    filesContainer.innerHTML = '';
    selectedFiles.forEach((file, index) => {
        const fileItem = createFileItem(file, index);
        filesContainer.appendChild(fileItem);
    });

    // Scroll automatico verso la lista file (dopo un breve delay per permettere il rendering)
    setTimeout(() => {
        filesList.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

// Create File Item
function createFileItem(file, index) {
    const div = document.createElement('div');
    div.className = 'file-item';
    div.innerHTML = `
        <div class="file-info-wrapper">
            <div class="file-icon">PDF</div>
            <div class="file-details">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${formatFileSize(file.size)}</div>
            </div>
        </div>
        <button class="file-remove" onclick="removeFile(${index})" title="Rimuovi file">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>
    `;
    return div;
}

// Remove File
function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFilesList();

    if (selectedFiles.length === 0) {
        actionButtons.style.display = 'none';
    }
}

// Clear All Files
function clearFiles() {
    selectedFiles = [];
    updateFilesList();
    fileInput.value = '';
    hideAllSections();
}

// Show Action Buttons
function showActionButtons() {
    actionButtons.style.display = 'flex';
}

// Upload Files
async function uploadFiles() {
    if (selectedFiles.length === 0) {
        showWarning('Seleziona almeno un file PDF');
        return;
    }

    // Previeni submit multipli
    if (isUploading) {
        log('Upload già in corso, richiesta ignorata');
        return;
    }

    isUploading = true;
    log('Uploading files:', selectedFiles);

    // Hide other sections
    hideAllSections();

    // Show progress
    progressSection.style.display = 'block';
    updateProgress(0, 'Preparazione file...');

    try {
        // Create FormData
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        updateProgress(30, 'Caricamento file...');

        // Upload with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.UPLOAD_TIMEOUT);

        const response = await fetch(getApiUrl(CONFIG.ENDPOINTS.DOWNLOAD_CSV), {
            method: 'POST',
            body: formData,
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        updateProgress(70, 'Elaborazione dati...');

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Errore durante l\'estrazione');
        }

        updateProgress(90, 'Generazione CSV...');

        // Get headers for metadata (incluso il totale reale dall'API)
        const totalRecords = response.headers.get('X-Total-Records') || '0';
        const processedFiles = response.headers.get('X-Processed-Files') || '0';
        const totalAmount = response.headers.get('X-Total-Amount') || '0';

        // Get CSV blob
        const blob = await response.blob();
        updateProgress(100, 'Completato!');

        // Extract filename from Content-Disposition header
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'beebus_rifornimenti.csv';
        if (contentDisposition) {
            const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
            if (matches != null && matches[1]) {
                filename = matches[1].replace(/['"]/g, '');
            }
        }

        // Download file
        downloadBlob(blob, filename);

        // Show success
        setTimeout(() => {
            showSuccess();
        }, 500);

    } catch (error) {
        log('Upload error:', error);

        if (error.name === 'AbortError') {
            showError('Timeout: l\'elaborazione sta richiedendo troppo tempo. Riprova con meno file.');
        } else {
            showError(error.message || 'Errore durante l\'elaborazione');
        }
    } finally {
        // Resetta il flag al termine (sia successo che errore)
        isUploading = false;
    }
}

// Update Progress
function updateProgress(percent, message) {
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const progressMessage = document.getElementById('progressMessage');

    progressFill.style.width = percent + '%';
    progressText.textContent = percent + '%';
    progressMessage.textContent = message;
}

// Download Blob
function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    log('File downloaded:', filename);
}

// Show Success
function showSuccess() {
    log('Extraction completed successfully');

    progressSection.style.display = 'none';
    resultsSection.style.display = 'block';
}

// Show Error
function showError(message) {
    progressSection.style.display = 'none';
    errorSection.style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

// Hide All Sections
function hideAllSections() {
    progressSection.style.display = 'none';
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
}

// Format File Size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Show Warning
function showWarning(message) {
    // Simple alert for now - could be improved with toast notifications
    alert('⚠️ ' + message);
}

//Endpoint: ${CONFIG.API_BASE_URL}
//Documentazione API: ${CONFIG.API_BASE_URL}/docs

// Show API Info
function showApiInfo() {
    const info = `
BeeBus Fatture Extractor API

Version: 2.0.0

Fornitori supportati:
• IP Plus
• Esso
• Q8 (Kuwait Petroleum)
• Tamoil

Limiti:
• Max ${CONFIG.MAX_FILES} file per richiesta
• Max ${CONFIG.MAX_FILE_SIZE / 1024 / 1024}MB per file
• Solo file PDF

    `.trim()

    alert(info);
}

// Show Support
function showSupport() {
    const support = `
Supporto BeeBus Fatture Extractor

Per assistenza contattare:
• Email: info@paradygma.tech

Problemi comuni:
1. File non riconosciuto → Verifica che sia PDF
2. Errore upload → Controlla connessione internet
3. CSV vuoto → Verifica formato fattura

    `.trim();

    alert(support);
}

log('App loaded successfully');