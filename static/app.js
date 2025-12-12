// API Base URL
const API_BASE_URL = '';

// DOM Elements
const questionTab = document.getElementById('question-tab');
const settingsTab = document.getElementById('settings-tab');
const tabButtons = document.querySelectorAll('.tab-button');

const questionForm = document.getElementById('question-form');
const questionInput = document.getElementById('question-input');
const nResultsInput = document.getElementById('n-results');
const useAugmentationInput = document.getElementById('use-augmentation');
const askButton = document.getElementById('ask-button');

const loadingDiv = document.getElementById('loading');
const answerSection = document.getElementById('answer-section');
const answerText = document.getElementById('answer-text');
const numChunks = document.getElementById('num-chunks');
const contextChunks = document.getElementById('context-chunks');
const errorMessage = document.getElementById('error-message');

const totalChunksSpan = document.getElementById('total-chunks');
const collectionNameSpan = document.getElementById('collection-name');
const refreshStatsButton = document.getElementById('refresh-stats');

const addPathForm = document.getElementById('add-path-form');
const newPathInput = document.getElementById('new-path-input');
const documentPathsList = document.getElementById('document-paths-list');
const reindexButton = document.getElementById('reindex-button');

const advancedSettingsForm = document.getElementById('advanced-settings-form');
const chunkSizeInput = document.getElementById('chunk-size');
const chunkOverlapInput = document.getElementById('chunk-overlap');
const tokensPerChunkInput = document.getElementById('tokens-per-chunk');

// ============================================================
// Tab Switching
// ============================================================

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.dataset.tab;
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    // Remove active class from all tabs and buttons
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
    });

    // Add active class to selected tab
    if (tabName === 'question') {
        questionTab.classList.add('active');
        tabButtons[0].classList.add('active');
    } else if (tabName === 'settings') {
        settingsTab.classList.add('active');
        tabButtons[1].classList.add('active');
        loadSettings(); // Load settings when switching to settings tab
    }
}

// ============================================================
// Question Form Handler
// ============================================================

questionForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const question = questionInput.value.trim();
    if (!question) return;

    // Show loading, hide previous results
    loadingDiv.classList.remove('hidden');
    answerSection.classList.add('hidden');
    errorMessage.classList.add('hidden');
    askButton.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/api/question`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                n_results: parseInt(nResultsInput.value),
                use_augmentation: useAugmentationInput.checked
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        displayAnswer(data);
        
    } catch (error) {
        console.error('Error:', error);
        showError(`Failed to get answer: ${error.message}`);
    } finally {
        loadingDiv.classList.add('hidden');
        askButton.disabled = false;
    }
});

function displayAnswer(data) {
    answerText.textContent = data.answer;
    numChunks.textContent = data.num_chunks;
    
    // Display context chunks
    contextChunks.innerHTML = '';
    data.relevant_chunks.forEach((chunk, index) => {
        const chunkDiv = document.createElement('div');
        chunkDiv.className = 'chunk';
        chunkDiv.innerHTML = `
            <div class="chunk-header">Context ${index + 1}:</div>
            <div>${escapeHtml(chunk)}</div>
        `;
        contextChunks.appendChild(chunkDiv);
    });

    answerSection.classList.remove('hidden');
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

// ============================================================
// Statistics
// ============================================================

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        if (!response.ok) throw new Error('Failed to load stats');
        
        const stats = await response.json();
        totalChunksSpan.textContent = stats.total_chunks;
        collectionNameSpan.textContent = stats.collection_name;
    } catch (error) {
        console.error('Error loading stats:', error);
        totalChunksSpan.textContent = 'Error';
        collectionNameSpan.textContent = 'Error';
    }
}

refreshStatsButton.addEventListener('click', loadStats);

// ============================================================
// Settings Management
// ============================================================

async function loadSettings() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/settings`);
        if (!response.ok) throw new Error('Failed to load settings');
        
        const settings = await response.json();
        
        // Load document paths
        displayDocumentPaths(settings.document_paths || []);
        
        // Load advanced settings
        chunkSizeInput.value = settings.chunk_size || 1000;
        chunkOverlapInput.value = settings.chunk_overlap || 100;
        tokensPerChunkInput.value = settings.tokens_per_chunk || 256;
        nResultsInput.value = settings.n_results || 5;
        useAugmentationInput.checked = settings.use_augmentation !== false;
        
    } catch (error) {
        console.error('Error loading settings:', error);
        showToast('Failed to load settings', 'error');
    }
}

function displayDocumentPaths(paths) {
    documentPathsList.innerHTML = '';
    
    if (paths.length === 0) {
        documentPathsList.innerHTML = '<li class="path-item"><span class="help-text">No document paths configured</span></li>';
        return;
    }
    
    paths.forEach(path => {
        const li = document.createElement('li');
        li.className = 'path-item';
        li.innerHTML = `
            <span class="path-text">${escapeHtml(path)}</span>
            <div class="path-actions">
                <button class="btn btn-danger btn-sm remove-path-btn" data-path="${escapeHtml(path)}">
                    <span class="btn-icon">🗑️</span>
                    Remove
                </button>
            </div>
        `;
        documentPathsList.appendChild(li);
    });
    
    // Add event listeners to remove buttons
    document.querySelectorAll('.remove-path-btn').forEach(btn => {
        btn.addEventListener('click', () => removeDocumentPath(btn.dataset.path));
    });
}

// Add Document Path
addPathForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const path = newPathInput.value.trim();
    if (!path) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/document-path/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path })
        });

        if (!response.ok) throw new Error('Failed to add path');
        
        const data = await response.json();
        showToast(data.message, 'success');
        newPathInput.value = '';
        loadSettings(); // Reload settings to update the list
        
    } catch (error) {
        console.error('Error adding path:', error);
        showToast('Failed to add document path', 'error');
    }
});

// Remove Document Path
async function removeDocumentPath(path) {
    if (!confirm(`Remove path: ${path}?`)) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/document-path/remove`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path })
        });

        if (!response.ok) throw new Error('Failed to remove path');
        
        const data = await response.json();
        showToast(data.message, 'success');
        loadSettings(); // Reload settings to update the list
        
    } catch (error) {
        console.error('Error removing path:', error);
        showToast('Failed to remove document path', 'error');
    }
}

// Reindex Documents
reindexButton.addEventListener('click', async () => {
    if (!confirm('Reindex all documents? This will clear existing data and reload from configured paths.')) {
        return;
    }

    reindexButton.disabled = true;
    reindexButton.innerHTML = '<span class="btn-icon">⏳</span> Reindexing...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/reindex`, {
            method: 'POST'
        });

        if (!response.ok) throw new Error('Failed to reindex');
        
        const data = await response.json();
        showToast(data.message, 'success');
        loadStats(); // Refresh stats after reindexing
        
    } catch (error) {
        console.error('Error reindexing:', error);
        showToast('Failed to reindex documents', 'error');
    } finally {
        reindexButton.disabled = false;
        reindexButton.innerHTML = '<span class="btn-icon">🔄</span> Reindex All Documents';
    }
});

// Advanced Settings Form
advancedSettingsForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    try {
        const response = await fetch(`${API_BASE_URL}/api/settings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                chunk_size: parseInt(chunkSizeInput.value),
                chunk_overlap: parseInt(chunkOverlapInput.value),
                tokens_per_chunk: parseInt(tokensPerChunkInput.value),
                n_results: parseInt(nResultsInput.value),
                use_augmentation: useAugmentationInput.checked
            })
        });

        if (!response.ok) throw new Error('Failed to save settings');
        
        const data = await response.json();
        showToast('Settings saved successfully!', 'success');
        
    } catch (error) {
        console.error('Error saving settings:', error);
        showToast('Failed to save settings', 'error');
    }
});

// ============================================================
// Toast Notifications
// ============================================================

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ============================================================
// Utility Functions
// ============================================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================
// Initialize on Page Load
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadSettings();
    showToast('Welcome! Ask a question or configure settings.', 'info');
});
