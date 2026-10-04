const state = {
  menu: [],
  cart: JSON.parse(localStorage.getItem("foodieflow_cart") || "[]"),
  category: "All"
};

const money = value => "₦" + Number(value).toLocaleString("en-NG");
const $ = id => document.getElementById(id);

document.addEventListener("DOMContentLoaded", () => {
  loadCategories();
  loadMenu();
  syncAuth();
  renderCart();
  bindSearch();
});

async function loadCategories() {
  const res = await fetch("/api/categories");
  const data = await res.json();
  const wrap = $("categoryChips");
  if (!wrap) return;
  wrap.innerHTML = ["All", ...data.categories].map(c =>
    `<button class="${c === state.category ? "active" : ""}" onclick="filterCategory('${c.replace(/'/g, "\\'")}')">${c}</button>`
  ).join("");
}

async function loadMenu() {
  const query = state.category !== "All" ? "?category=" + encodeURIComponent(state.category) : "";
  const res = await fetch("/api/menu" + query);
  const data = await res.json();
  state.menu = data.menu;
  renderMenu();
}

function renderMenu() {
  const wrap = $("menuContainer");
  if (!wrap) return;
  const search = ($("menuSearch")?.value || "").toLowerCase();
  const items = state.menu.filter(x =>
    !search || x.name.toLowerCase().includes(search) || x.description.toLowerCase().includes(search)
  );
  wrap.innerHTML = items.length ? items.map(item => `
    <article class="food-card">
      <div class="food-img">
        <img src="${item.image_url}" alt="${escapeHtml(item.name)}" loading="lazy">
        ${item.featured ? '<span class="badge">Popular</span>' : ""}
      </div>
      <div class="food-body">
        <h3>${escapeHtml(item.name)}</h3>
        <p>${escapeHtml(item.description)}</p>
        <div class="food-foot">
          <span class="price">${money(item.price)}</span>
          <button class="add-btn" aria-label="Add ${escapeHtml(item.name)}" onclick="addToCart(${item.id})">+</button>
        </div>
      </div>
    </article>
  `).join("") : '<div class="form-card" style="grid-column:1/-1;text-align:center">No dishes matched your search.</div>';
}

function filterCategory(category) {
  state.category = category;
  document.querySelectorAll("#categoryChips button").forEach(b => b.classList.remove("active"));
  loadCategories();
  loadMenu();
}

function bindSearch() {
  $("menuSearch")?.addEventListener("input", renderMenu);
}

function addToCart(id) {
  const item = state.menu.find(x => x.id === id);
  if (!item) return;
  const existing = state.cart.find(x => x.id === id);
  if (existing) existing.quantity += 1;
  else state.cart.push({...item, quantity: 1});
  saveCart();
  renderCart();
  openCart();
}

function changeQty(id, delta) {
  const item = state.cart.find(x => x.id === id);
  if (!item) return;
  item.quantity += delta;
  if (item.quantity <= 0) state.cart = state.cart.filter(x => x.id !== id);
  saveCart(); renderCart();
}

function saveCart() {
  localStorage.setItem("foodieflow_cart", JSON.stringify(state.cart));
  const count = state.cart.reduce((n, x) => n + x.quantity, 0);
  document.querySelectorAll("[data-cart-count]").forEach(x => x.textContent = count);
}

function renderCart() {
  saveCart();
  const wrap = $("cartItems");
  if (!wrap) return;
  if (!state.cart.length) {
    wrap.innerHTML = '<div class="form-card" style="text-align:center"><strong>Your basket is empty.</strong><p class="section-sub">Add something delicious and it will appear here.</p></div>';
  } else {
    wrap.innerHTML = state.cart.map(item => `
      <div class="cart-row">
        <img src="${item.image_url}" alt="">
        <div><strong style="font-size:13px">${escapeHtml(item.name)}</strong><div class="section-sub">${money(item.price)} each</div>
          <div class="qty"><button onclick="changeQty(${item.id},-1)">−</button><span>${item.quantity}</span><button onclick="changeQty(${item.id},1)">+</button></div>
        </div>
        <strong>${money(item.price * item.quantity)}</strong>
      </div>`).join("");
  }
  const subtotal = state.cart.reduce((n, x) => n + x.price * x.quantity, 0);
  const delivery = subtotal ? (subtotal < 15000 ? 1500 : 0) : 0;
  if ($("cartSubtotal")) $("cartSubtotal").textContent = money(subtotal);
  if ($("cartDelivery")) $("cartDelivery").textContent = money(delivery);
  if ($("cartTotal")) $("cartTotal").textContent = money(subtotal + delivery);
}

function openCart() { $("cartDrawer")?.classList.add("open"); }
function closeCart() { $("cartDrawer")?.classList.remove("open"); }

function openAuth() { $("authModal")?.classList.add("open"); }
function closeAuth() { $("authModal")?.classList.remove("open"); }

function toggleAuth() {
  const login = $("authLogin").style.display !== "none";
  $("authLogin").style.display = login ? "none" : "block";
  $("authRegister").style.display = login ? "block" : "none";
  $("authTitle").textContent = login ? "Create your account" : "Welcome back";
  $("authSwitch").textContent = login ? "Already have an account? Sign in" : "New here? Create an account";
  $("authError").classList.remove("show");
}

async function submitAuth(event) {
  event.preventDefault();
  const login = $("authLogin").style.display !== "none";
  const payload = {
    username: $("authUsername").value.trim(),
    password: $("authPassword").value
  };
  if (!login) payload.email = $("authEmail").value.trim();

  const res = await fetch(login ? "/api/auth/login" : "/api/auth/register", {
    method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (!res.ok) {
    $("authError").textContent = data.message || "Something went wrong.";
    $("authError").classList.add("show");
    return;
  }
  if (login) {
    localStorage.setItem("foodieflow_token", data.token);
    localStorage.setItem("foodieflow_user", JSON.stringify(data.user));
    closeAuth(); syncAuth();
  } else {
    $("authError").textContent = "Account created. Sign in to continue.";
    $("authError").classList.add("show");
    toggleAuth();
  }
}

function syncAuth() {
  const user = JSON.parse(localStorage.getItem("foodieflow_user") || "null");
  document.querySelectorAll("[data-auth-label]").forEach(x => x.textContent = user ? user.username : "Sign in");
}

function logout() {
  localStorage.removeItem("foodieflow_token");
  localStorage.removeItem("foodieflow_user");
  location.reload();
}

async function checkout() {
  if (!state.cart.length) return alert("Your basket is empty.");
  const token = localStorage.getItem("foodieflow_token");
  if (!token) { closeCart(); openAuth(); return; }
  const address = prompt("Enter your delivery address:");
  if (!address?.trim()) return;

  const res = await fetch("/api/orders", {
    method:"POST",
    headers:{"Content-Type":"application/json","Authorization":"Bearer " + token},
    body:JSON.stringify({delivery_address:address,items:state.cart})
  });
  const data = await res.json();
  if (res.status === 401) { logout(); return; }
  if (!res.ok) return alert(data.message || "Unable to place order.");
  state.cart = []; saveCart(); renderCart(); closeCart();
  alert("Order #" + data.order_id + " placed. Total: " + money(data.total));
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, m => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));
}
