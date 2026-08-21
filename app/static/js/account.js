document.addEventListener('DOMContentLoaded', () => {
    loadProfile();
    loadOrders();
});

function loadProfile() {
    const userRaw = localStorage.getItem('user');
    if (userRaw) {
        const user = JSON.parse(userRaw);
        document.getElementById('profileName').innerText = user.username;
        document.getElementById('profileEmail').innerText = user.email || 'Verified Customer';
        document.getElementById('logoutBtn').classList.remove('hidden');
    }
}

async function loadOrders() {
    const token = localStorage.getItem('token');
    if (!token) return;

    const res = await fetch('/api/orders/my-orders', {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    if (res.ok) {
        const data = await res.json();
        const container = document.getElementById('ordersContainer');
        if (data.orders.length === 0) {
            container.innerHTML = `<div class="text-center py-6 text-gray-500 text-sm">No orders placed yet.</div>`;
            return;
        }

        container.innerHTML = '';
        data.orders.forEach(order => {
            container.innerHTML += `
                <div class="bg-gray-800 border border-gray-700 rounded-xl p-3 flex justify-between items-center">
                    <div>
                        <p class="text-xs font-bold text-white">Order #${order.id}</p>
                        <p class="text-[10px] text-gray-400">${order.created_at}</p>
                    </div>
                    <div class="text-right">
                        <p class="text-sm font-extrabold text-orange-400">$${order.total_amount.toFixed(2)}</p>
                        <span class="text-[10px] bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full uppercase font-bold">${order.status}</span>
                    </div>
                </div>
            `;
        });
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.reload();
}
