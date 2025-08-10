// Main JavaScript for Restorative Justice Case Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeTooltips();
    initializeAlerts();
    initializeFormValidation();
    initializeSearch();
    initializeDatePickers();
    initializeConfirmDialogs();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Auto-dismiss alerts
function initializeAlerts() {
    // Auto-dismiss success alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-success');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Form validation enhancements
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Phone number formatting
    const phoneInputs = document.querySelectorAll('input[type="tel"], input[name*="phone"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 10) {
                value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
            }
            e.target.value = value;
        });
    });

    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(function(input) {
        input.addEventListener('blur', function(e) {
            const email = e.target.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                e.target.classList.add('is-invalid');
                showFieldError(e.target, 'Please enter a valid email address');
            } else {
                e.target.classList.remove('is-invalid');
                hideFieldError(e.target);
            }
        });
    });
}

// Enhanced search functionality
function initializeSearch() {
    const searchInputs = document.querySelectorAll('input[name="search"]');
    
    searchInputs.forEach(function(input) {
        let timeout = null;
        
        input.addEventListener('input', function(e) {
            clearTimeout(timeout);
            
            // Debounce search for better UX
            timeout = setTimeout(function() {
                if (e.target.value.length >= 2 || e.target.value.length === 0) {
                    // Could trigger auto-search here if desired
                    console.log('Search:', e.target.value);
                }
            }, 500);
        });

        // Clear search button functionality
        const clearButton = input.parentElement.querySelector('.btn[type="button"]');
        if (clearButton) {
            clearButton.addEventListener('click', function() {
                input.value = '';
                input.focus();
            });
        }
    });
}

// Date picker enhancements
function initializeDatePickers() {
    const dateInputs = document.querySelectorAll('input[type="date"]');
    
    dateInputs.forEach(function(input) {
        // Set max date to today for birth dates
        if (input.name.includes('birth')) {
            const today = new Date().toISOString().split('T')[0];
            input.setAttribute('max', today);
        }
        
        // Validate date ranges
        input.addEventListener('change', function(e) {
            const selectedDate = new Date(e.target.value);
            const today = new Date();
            
            if (input.name.includes('birth') && selectedDate > today) {
                showFieldError(e.target, 'Birth date cannot be in the future');
                e.target.classList.add('is-invalid');
            } else {
                hideFieldError(e.target);
                e.target.classList.remove('is-invalid');
            }
        });
    });
}

// Confirmation dialogs for destructive actions
function initializeConfirmDialogs() {
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = button.getAttribute('data-confirm') || 'Are you sure?';
            
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

// Utility functions
function showFieldError(field, message) {
    hideFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    errorDiv.setAttribute('data-custom-error', 'true');
    
    field.parentNode.appendChild(errorDiv);
    field.classList.add('is-invalid');
}

function hideFieldError(field) {
    const existingError = field.parentNode.querySelector('[data-custom-error="true"]');
    if (existingError) {
        existingError.remove();
    }
    field.classList.remove('is-invalid');
}

// Show loading state
function showLoading(element) {
    element.classList.add('disabled');
    element.setAttribute('disabled', 'true');
    
    const originalText = element.innerHTML;
    element.setAttribute('data-original-text', originalText);
    element.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Loading...';
}

// Hide loading state
function hideLoading(element) {
    element.classList.remove('disabled');
    element.removeAttribute('disabled');
    
    const originalText = element.getAttribute('data-original-text');
    if (originalText) {
        element.innerHTML = originalText;
        element.removeAttribute('data-original-text');
    }
}

// Format numbers
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Format dates
function formatDate(dateString, options = {}) {
    const date = new Date(dateString);
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    return date.toLocaleDateString('en-US', { ...defaultOptions, ...options });
}

// Local storage helpers (for user preferences)
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.warn('Could not save to localStorage:', e);
    }
}

function loadFromStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.warn('Could not load from localStorage:', e);
        return defaultValue;
    }
}

// Table enhancements
function initializeTableFeatures() {
    const tables = document.querySelectorAll('.table-sortable');
    
    tables.forEach(function(table) {
        const headers = table.querySelectorAll('th[data-sort]');
        
        headers.forEach(function(header) {
            header.style.cursor = 'pointer';
            header.addEventListener('click', function() {
                sortTable(table, header.getAttribute('data-sort'));
            });
        });
    });
}

// Simple table sorting
function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const columnIndex = Array.from(table.querySelectorAll('th')).findIndex(th => th.getAttribute('data-sort') === column);
    
    if (columnIndex === -1) return;
    
    const sortedRows = rows.sort((a, b) => {
        const aVal = a.cells[columnIndex].textContent.trim();
        const bVal = b.cells[columnIndex].textContent.trim();
        
        // Try to parse as numbers first
        const aNum = parseFloat(aVal);
        const bNum = parseFloat(bVal);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return aNum - bNum;
        }
        
        // Fall back to string comparison
        return aVal.localeCompare(bVal);
    });
    
    // Clear tbody and append sorted rows
    tbody.innerHTML = '';
    sortedRows.forEach(row => tbody.appendChild(row));
}

// Print functionality
function printPage() {
    window.print();
}

// Export functionality (basic CSV export)
function exportTableToCSV(tableId, filename = 'export.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const csvRow = [];
        
        cols.forEach(function(col) {
            csvRow.push('"' + col.textContent.replace(/"/g, '""') + '"');
        });
        
        csv.push(csvRow.join(','));
    });
    
    // Download CSV
    const csvFile = new Blob([csv.join('\n')], { type: 'text/csv' });
    const downloadLink = document.createElement('a');
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + / to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
    
    // ESC to clear modals/close elements
    if (e.key === 'Escape') {
        // Close any open dropdowns
        const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
        openDropdowns.forEach(dropdown => {
            const button = dropdown.previousElementSibling;
            if (button && button.classList.contains('dropdown-toggle')) {
                button.click();
            }
        });
    }
});

// Console welcome message (optional)
console.log('%cRestorative Justice Case Management System', 'color: #0d6efd; font-size: 16px; font-weight: bold;');
console.log('System loaded successfully. For support, contact your administrator.');