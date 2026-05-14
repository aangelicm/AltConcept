// === Глобальные функции ===

// Показать уведомление
function showAlert(message, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert ${type}`;
    alert.textContent = message;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alert, container.firstChild);
    
    setTimeout(() => alert.remove(), 5000);
}

// Подтверждение действия
function confirmAction(message) {
    return confirm(message);
}

// === Поиск товаров (живой) ===
function setupSearch() {
    const searchInput = document.getElementById('search-input');
    const products = document.querySelectorAll('.product-card');
    
    if (!searchInput || !products.length) return;
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        
        products.forEach(card => {
            const name = card.dataset.name?.toLowerCase() || '';
            const desc = card.dataset.desc?.toLowerCase() || '';
            
            if (name.includes(query) || desc.includes(query)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

// === Корзина ===
async function addToCart(productId, quantity = 1) {
    try {
        const response = await fetch(`/buyer/cart/add/${productId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `quantity=${quantity}`
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('✅ Товар добавлен в корзину', 'success');
            updateCartCount();
        } else {
            showAlert(result.detail || 'Ошибка', 'error');
        }
    } catch (err) {
        showAlert('Ошибка сети', 'error');
        console.error(err);
    }
}

async function removeFromCart(productId) {
    if (!confirmAction('Удалить товар из корзины?')) return;
    
    try {
        const response = await fetch(`/buyer/cart/remove/${productId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showAlert('Товар удалён', 'success');
            location.reload();
        }
    } catch (err) {
        showAlert('Ошибка', 'error');
    }
}

async function updateQuantity(productId, quantity) {
    // Можно расширить, если бэкенд поддерживает обновление количества
    console.log('Update quantity:', productId, quantity);
}

// === Счётчик корзины ===
async function updateCartCount() {
    const badge = document.getElementById('cart-count');
    if (!badge) return;
    
    try {
        const response = await fetch('/buyer/cart');
        if (response.ok) {
            const data = await response.json();
            const count = data.items?.reduce((sum, item) => sum + item.quantity, 0) || 0;
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline' : 'none';
        }
    } catch (err) {
        console.error('Не удалось обновить счётчик корзины', err);
    }
}

// === Удаление товара (продавец) ===
async function deleteProduct(productId) {
    if (!confirmAction('Вы уверены? Товар будет удалён безвозвратно.')) return;
    
    try {
        const response = await fetch(`/seller/product/delete/${productId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showAlert('Товар удалён', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            const data = await response.json();
            showAlert(data.detail || 'Ошибка', 'error');
        }
    } catch (err) {
        showAlert('Ошибка сети', 'error');
    }
}

// === Оформление заказа ===
async function checkout() {
    if (!confirmAction('Оформить заказ?')) return;
    
    try {
        const response = await fetch('/buyer/checkout', { method: 'POST' });
        const result = await response.json();
        
        if (response.ok) {
            showAlert(`✅ Заказ оформлен! Сумма: ${result.total} ₽`, 'success');
            setTimeout(() => location.href = '/buyer/catalog', 2000);
        } else {
            showAlert(result.detail || 'Ошибка', 'error');
        }
    } catch (err) {
        showAlert('Ошибка сети', 'error');
    }
}

// === Инициализация при загрузке ===
document.addEventListener('DOMContentLoaded', () => {
    setupSearch();
    updateCartCount();
    
    // Кнопки "Добавить в корзину"
    document.querySelectorAll('.btn-add-to-cart').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const id = btn.dataset.id;
            addToCart(id);
        });
    });
    
    // Кнопки "Удалить из корзины"
    document.querySelectorAll('.btn-remove-from-cart').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const id = btn.dataset.id;
            removeFromCart(id);
        });
    });
    
    // Кнопки "Удалить товар" (продавец)
    document.querySelectorAll('.btn-delete-product').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const id = btn.dataset.id;
            deleteProduct(id);
        });
    });
    
    // Кнопка оформления заказа
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            checkout();
        });
    }
});

