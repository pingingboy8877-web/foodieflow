document.addEventListener('DOMContentLoaded', renderCart);

function getCart() {
    return JSON.parse(localStorage.getItem('cart') || '[]');
}

function renderCart() {
    const items = getCart();
    const container = document.getElementById('cartItemsContainer');
    
    if (items.length === 0) {
        container.innerHTML = `<div class="text-center py-10 text-gray-500 text-sm">Your cart is empty.</div>`;
        updateTotals(0);
        return;
    }

    container.innerHTML = '';
    let subtotal = 0;

    items.forEach((item, index) => {
        subtotal += item.price;
        container.innerHTML += `
            <div class="bg-gray-800 border border-gray-700 rounded-xl p-3 flex items-center justify-between">
                <div>
                    <h4 class="font-bold text-sm text-white">${item.name}</h4>
                    <p class="text-orange-400 font-bold text-xs">$${item.price.toFixed(2)}</p>
                </div>
                <button onclick="removeItem(${index})" class="text-gray-500 hover:text-red-400 text-sm p-2">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        `;
    });

    updateTotals(subtotal);
}

function updateTotals(subtotal) {
    const delivery = subtotal > 0 ? 2.50 : 0;
    document.getElementById('cartSubtotal').innerText = `$${subtotal.toFixed(2)}`;
    document.getElementById('cartTotal').innerText = `$${(subtotal + delivery).toFixed(2)}`;
}

function removeItem(index) {
    let items = getCart();
    items.splice(index, 1);
    localStorage.setItem('cart', JSON.stringify(items));
    renderCart();
}

function clearCart() {
    localStorage.removeItem('cart');
    renderCart();
}

async function processCheckout() {
    const token = localStorage.getItem('token');
    const items = getCart();

    if (!token) {
        alert('Please login first on the Account page to place your order.');
        window.location.href = '/account.html';
        return;
    }

    if (items.length === 0) {
        alert('Your cart is empty!');
        return;
    }

    const subtotal = items.reduce((sum, item) => sum + item.price, 0);
    const total_amount = subtotal + 2.50;

    const res = await fetch('/api/orders', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ total_amount, items })
    });

    if (res.ok) {
        alert('Order placed successfully!');
        clearCart();
        window.location.href = '/account.html';
    } else {
        alert('Failed to place order. Token might be expired.');
    }
}
