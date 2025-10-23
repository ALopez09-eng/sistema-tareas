// Funciones JavaScript para la aplicación
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips y funcionalidades
    initializeApp();
});

function initializeApp() {
    // Validación de formularios
    initializeFormValidation();
    
    // Manejo de mensajes flash
    initializeFlashMessages();
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    showFieldError(field, 'Este campo es obligatorio');
                } else {
                    clearFieldError(field);
                }
            });
            
            // Validación de contraseñas en registro
            if (form.id === 'register-form' || form.querySelector('#confirm_password')) {
                const password = form.querySelector('#password');
                const confirmPassword = form.querySelector('#confirm_password');
                
                if (password && confirmPassword && password.value !== confirmPassword.value) {
                    valid = false;
                    showFieldError(confirmPassword, 'Las contraseñas no coinciden');
                }
            }
            
            if (!valid) {
                e.preventDefault();
            }
        });
    });
}

function showFieldError(field, message) {
    clearFieldError(field);
    field.style.borderColor = '#e74c3c';
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.style.color = '#e74c3c';
    errorDiv.style.fontSize = '0.8rem';
    errorDiv.style.marginTop = '0.25rem';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(field) {
    field.style.borderColor = '';
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

function initializeFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash');
    
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transition = 'opacity 0.5s';
            setTimeout(() => message.remove(), 500);
        }, 5000);
    });
}

// Función para cargar datos via API
async function loadApiData() {
    const apiDataContainer = document.getElementById('api-data');
    
    try {
        apiDataContainer.innerHTML = '<p>Cargando datos...</p>';
        
        const response = await fetch('/api/items');
        const data = await response.json();
        
        if (data.length === 0) {
            apiDataContainer.innerHTML = '<p>No hay items para mostrar.</p>';
            return;
        }
        
        const formattedData = JSON.stringify(data, null, 2);
        apiDataContainer.innerHTML = `<pre>${formattedData}</pre>`;
        
    } catch (error) {
        apiDataContainer.innerHTML = `<p class="error">Error al cargar datos: ${error.message}</p>`;
    }
}

// Utilidades adicionales
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('es-ES', options);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Exportar funciones para uso global
window.loadApiData = loadApiData;
window.formatDate = formatDate;