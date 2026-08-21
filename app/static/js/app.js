let isLoginMode = true;
let cart = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchMenu();
    checkAuth();
});

function fetchMenu() {
    fetch('/api/menu')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('menuContainer');
            container.innerHTML = '';
            data.menu.forEach(item => {
                container.innerHTML += `
                    <div class="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden flex items-center p-3 shadow-sm">
                        <img src="${item.image_url}" alt="${item.name}" class="w-20 h-20 object-cover rounded-lg mr-3">
                        <div class="flex-1">
                            <span class="text-[10px] bg-orange-500/20 text-orange-400 px-2 py-0.5 rounded-full font-semibold uppercase">${item.category}</span>
                            <h3 class="font-bold text-sm text-white mt-1">${item.name}</h3>
                            <p class="text-orange-400 font-extrabold text-sm mt-1">$${item.price.toFixed(2)}</p>
                        </div>
                        <button onclick="addToCart(${item.id})" class="bg-gray-700 hover:bg-orange-500 text-white w-8 h-8 rounded-full flex items-center justify-center transition">
                            <i class="fa-solid fa-plus text-xs"></i>
                        </button>
                    </div>
                `;
            });
        });
}

function addToCart(itemId) {
    cart.push(itemId);
    document.getElementById('cartBadge').innerText = cart.length;
}

function openCart() {
    alert(`Items in cart: ${cart.length}`);
}

function openAuthModal() { document.getElementById('authModal').classList.remove('hidden'); }
function closeAuthModal() { document.getElementById('authModal').classList.add('hidden'); }

function toggleAuthMode() {
    isLoginMode = !isLoginMode;
    document.getElementById('modalTitle').innerText = isLoginMode ? 'Login to Account' : 'Create Account';
    document.getElementById('emailGroup').classList.toggle('hidden', isLoginMode);
    document.getElementById('toggleText').innerText = isLoginMode ? 'Need an account?' : 'Already registered?';
    document.getElementById('toggleBtn').innerText = isLoginMode ? 'Register' : 'Login';
}

document.getElementById('authForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('usernameInput').value;
    const password = document.getElementById('passwordInput').value;
    const email = document.getElementById('emailInput').value;

    const endpoint = isLoginMode ? '/api/auth/login' : '/api/auth/register';
    const body = isLoginMode ? { username, password } : { username, email, password };

    const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });

    const data = await res.json();
    if (res.ok) {
        if (isLoginMode) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            closeAuthModal();
            checkAuth();
        } else {
            alert('Registration successful! Please login.');
            toggleAuthMode();
        }
    } else {
        alert(data.message);
    }
});

function checkAuth() {
    const user = localStorage.getItem('user');
    const authStatus = document.getElementById('authStatus');
    if (user) {
        const parsed = JSON.parse(user);
        authStatus.innerHTML = `
            <span class="text-xs text-gray-300 mr-2">Hi, <b>${parsed.username}</b></span>
            <button onclick="logout()" class="text-xs text-red-400 hover:underline">Exit</button>
        `;
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    location.reload();
}
