/**
 * Pydantic AI Agent Framework - Main JavaScript
 * Handles UI interactions and API calls
 */

// Global variables
let currentTheme = 'light';
let alertTimeout = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Load theme preference
    loadTheme();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Set up event listeners
    setupEventListeners();
    
    console.log('🤖 Pydantic AI Framework initialized');
}

function loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        currentTheme = savedTheme;
        document.body.setAttribute('data-theme', currentTheme);
    }
}

function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function setupEventListeners() {
    // Global error handler
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        showAlert('An unexpected error occurred. Please try again.', 'danger');
    });
    
    // Handle unhandled promise rejections
    window.addEventListener('unhandledrejection', function(e) {
        console.error('Unhandled promise rejection:', e.reason);
        showAlert('An unexpected error occurred. Please try again.', 'danger');
    });
}

// Alert system
function showAlert(message, type = 'info', duration = 5000) {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;
    
    // Clear existing timeout
    if (alertTimeout) {
        clearTimeout(alertTimeout);
    }
    
    // Create alert element
    const alertId = 'alert-' + Date.now();
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert" id="${alertId}">
            <i class="bi bi-${getAlertIcon(type)}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.innerHTML = alertHtml;
    
    // Auto-dismiss after duration
    if (duration > 0) {
        alertTimeout = setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, duration);
    }
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle',
        'primary': 'info-circle',
        'secondary': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// API Helper functions
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Configuration modal functions
function showConfigModal() {
    loadConfiguration();
    const modal = new bootstrap.Modal(document.getElementById('configModal'));
    modal.show();
}

async function loadConfiguration() {
    try {
        const response = await apiRequest('/api/models');
        if (response.success) {
            displayModelProviders(response.models);
        }
    } catch (error) {
        console.error('Error loading configuration:', error);
        showAlert('Error loading configuration', 'danger');
    }
}

function displayModelProviders(models) {
    const container = document.getElementById('modelProviders');
    if (!container) return;
    
    let html = '';
    for (const [provider, modelList] of Object.entries(models)) {
        const isConfigured = modelList.length > 0;
        const statusClass = isConfigured ? 'text-success' : 'text-warning';
        const statusIcon = isConfigured ? 'check-circle' : 'exclamation-triangle';
        
        html += `
            <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center">
                    <strong>${provider.charAt(0).toUpperCase() + provider.slice(1)}</strong>
                    <i class="bi bi-${statusIcon} ${statusClass}"></i>
                </div>
                <small class="text-muted">
                    ${isConfigured ? `${modelList.length} models available` : 'Not configured'}
                </small>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function saveConfiguration() {
    showAlert('Configuration saved successfully!', 'success');
    bootstrap.Modal.getInstance(document.getElementById('configModal')).hide();
}

// System logs modal functions
function showLogsModal() {
    loadSystemLogs();
    const modal = new bootstrap.Modal(document.getElementById('logsModal'));
    modal.show();
}

async function loadSystemLogs() {
    const container = document.getElementById('systemLogs');
    if (!container) return;
    
    container.innerHTML = `
        <div class="text-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    // Simulate loading logs (replace with actual API call)
    setTimeout(() => {
        const logs = [
            { level: 'INFO', message: 'Application started successfully', timestamp: new Date().toISOString() },
            { level: 'INFO', message: 'Database initialized', timestamp: new Date().toISOString() },
            { level: 'INFO', message: 'Agent templates loaded', timestamp: new Date().toISOString() }
        ];
        
        displaySystemLogs(logs);
    }, 1000);
}

function displaySystemLogs(logs) {
    const container = document.getElementById('systemLogs');
    if (!container) return;
    
    let html = '';
    logs.forEach(log => {
        const levelClass = getLevelClass(log.level);
        const time = new Date(log.timestamp).toLocaleString();
        
        html += `
            <div class="d-flex justify-content-between align-items-start mb-2 p-2 border-bottom">
                <div>
                    <span class="badge bg-${levelClass}">${log.level}</span>
                    <span class="ms-2">${log.message}</span>
                </div>
                <small class="text-muted">${time}</small>
            </div>
        `;
    });
    
    container.innerHTML = html || '<p class="text-muted">No logs available</p>';
}

function getLevelClass(level) {
    const classes = {
        'ERROR': 'danger',
        'WARNING': 'warning',
        'INFO': 'info',
        'DEBUG': 'secondary'
    };
    return classes[level] || 'secondary';
}

function refreshLogs() {
    loadSystemLogs();
}

// About modal function
function showAboutModal() {
    const modal = new bootstrap.Modal(document.getElementById('aboutModal'));
    modal.show();
}

// Theme toggle function
function toggleTheme() {
    currentTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.body.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
}

// Utility functions
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Copy to clipboard function
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('Copied to clipboard!', 'success', 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
            showAlert('Failed to copy to clipboard', 'danger');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showAlert('Copied to clipboard!', 'success', 2000);
        } catch (err) {
            console.error('Failed to copy: ', err);
            showAlert('Failed to copy to clipboard', 'danger');
        } finally {
            textArea.remove();
        }
    }
}

// Download function
function downloadFile(content, filename, contentType = 'application/json') {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateRequired(value) {
    return value && value.trim().length > 0;
}

function validateMinLength(value, minLength) {
    return value && value.length >= minLength;
}

function validateMaxLength(value, maxLength) {
    return !value || value.length <= maxLength;
}

// Loading state management
function showLoading(element, text = 'Loading...') {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    
    if (element) {
        element.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">${text}</span>
                </div>
                <div class="mt-2">${text}</div>
            </div>
        `;
    }
}

function hideLoading(element, content = '') {
    if (typeof element === 'string') {
        element = document.getElementById(element);
    }
    
    if (element) {
        element.innerHTML = content;
    }
}

// Animation helpers
function fadeIn(element, duration = 300) {
    element.style.opacity = 0;
    element.style.display = 'block';
    
    const start = performance.now();
    
    function animate(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        
        element.style.opacity = progress;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}

function fadeOut(element, duration = 300) {
    const start = performance.now();
    const startOpacity = parseFloat(getComputedStyle(element).opacity);
    
    function animate(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);
        
        element.style.opacity = startOpacity * (1 - progress);
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            element.style.display = 'none';
        }
    }
    
    requestAnimationFrame(animate);
}

// Export functions for global use
window.PydanticAI = {
    showAlert,
    apiRequest,
    showConfigModal,
    showLogsModal,
    showAboutModal,
    toggleTheme,
    copyToClipboard,
    downloadFile,
    formatBytes,
    formatDate,
    debounce,
    throttle,
    validateEmail,
    validateRequired,
    validateMinLength,
    validateMaxLength,
    showLoading,
    hideLoading,
    fadeIn,
    fadeOut
};

console.log('🚀 Pydantic AI Framework JavaScript loaded');
