from flask import Flask, render_template_string, request, jsonify, session
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'super-secret-key-2024'

# ---------- Products (32 items – same as before) ----------
PRODUCTS = [
    {"id":1,"name":"Men's Regular Fit Cotton Shirt","price":599,"old_price":1299,"discount":54,"rating":4.3,"reviews_count":1240,"image":"https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400","description":"Premium 100% cotton shirt.","category":"Men","seller":"FashionHub","seller_rating":4.5,"sold":3400,"sizes":["S","M","L","XL"],"colors":["White","Blue"]},
    {"id":2,"name":"Men's Slim Fit Jeans","price":899,"old_price":1999,"discount":55,"rating":4.4,"reviews_count":2100,"image":"https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=400","description":"Stretchable slim fit jeans.","category":"Men","seller":"DenimWorld","seller_rating":4.3,"sold":5600,"sizes":["28","30","32","34"],"colors":["Blue","Black"]},
    {"id":3,"name":"Men's Sports Shoes","price":1299,"old_price":3999,"discount":67,"rating":4.6,"reviews_count":3450,"image":"https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400","description":"Lightweight breathable mesh.","category":"Men","seller":"Sportify","seller_rating":4.7,"sold":8900,"sizes":["6","7","8","9","10"],"colors":["Black/Red","Blue"]},
    {"id":4,"name":"Men's Leather Wallet","price":399,"old_price":999,"discount":60,"rating":4.2,"reviews_count":890,"image":"https://images.unsplash.com/photo-1627123424574-724758594e93?w=400","description":"Genuine leather wallet.","category":"Men","seller":"LeatherCraft","seller_rating":4.4,"sold":2100},
    {"id":5,"name":"Men's Analog Watch","price":1499,"old_price":3499,"discount":57,"rating":4.5,"reviews_count":1670,"image":"https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400","description":"Stainless steel watch.","category":"Men","seller":"TimeKeeper","seller_rating":4.6,"sold":4300},
    {"id":6,"name":"Women's Floral Dress","price":1199,"old_price":2999,"discount":60,"rating":4.7,"reviews_count":2340,"image":"https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=400","description":"Lightweight viscose dress.","category":"Women","seller":"GlamourStore","seller_rating":4.8,"sold":7800,"sizes":["XS","S","M","L"],"colors":["Pink","Blue"]},
    {"id":7,"name":"Women's High Heel Sandals","price":899,"old_price":2499,"discount":64,"rating":4.4,"reviews_count":1560,"image":"https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400","description":"4 inch heel sandals.","category":"Women","seller":"FootFashion","seller_rating":4.3,"sold":3400,"sizes":["5","6","7","8"],"colors":["Black","Nude"]},
    {"id":8,"name":"Wireless Earbuds","price":1299,"old_price":3499,"discount":63,"rating":4.5,"reviews_count":3450,"image":"https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400","description":"Bluetooth 5.0 earbuds.","category":"Electronics","seller":"GadgetHub","seller_rating":4.6,"sold":12300,"colors":["White","Black"]},
    {"id":9,"name":"Smart Watch","price":1999,"old_price":4999,"discount":60,"rating":4.4,"reviews_count":2890,"image":"https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=400","description":"Heart rate monitor.","category":"Electronics","seller":"TechZone","seller_rating":4.5,"sold":8900},
    {"id":10,"name":"Kids Cartoon T-Shirt","price":349,"old_price":799,"discount":56,"rating":4.5,"reviews_count":670,"image":"https://images.unsplash.com/photo-1622298430330-d3e2b69c3b9b?w=400","description":"100% cotton printed.","category":"Kids","seller":"KidsFashion","seller_rating":4.6,"sold":2300,"sizes":["2-3Y","3-4Y"],"colors":["Blue","Red"]},
]

def get_product(pid):
    for p in PRODUCTS:
        if p["id"] == pid:
            return p.copy()
    return None

# ---------- HTML Template (with full Order Now flow) ----------
# Modified: Added manifest link and service worker registration (PWA support)
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes, viewport-fit=cover">
    <title>ShopZen - Order Now</title>
    <link rel="manifest" href="/manifest.json">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { -webkit-tap-highlight-color: transparent; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .glass { background: rgba(255,255,255,0.95); backdrop-filter: blur(12px); }
        .line-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        input, select, textarea, button { font-size: 16px; } /* prevents zoom on mobile */
    </style>
</head>
<body class="bg-gray-100 flex justify-center items-center min-h-screen font-sans">
<div class="w-full max-w-[450px] h-[100dvh] bg-white shadow-2xl overflow-hidden flex flex-col relative">


    <!-- Login Screen -->
    <div id="auth-screen" class="absolute inset-0 z-50 bg-white flex flex-col p-6">
        <div class="flex-1 flex flex-col justify-center">
            <div class="w-20 h-20 bg-rose-500 rounded-2xl flex items-center justify-center text-white text-3xl font-bold mx-auto">S</div>
            <h1 class="text-2xl font-bold text-center mt-6">Welcome to ShopZen</h1>
            <div class="mt-8">
                <label class="text-xs font-semibold">Mobile Number</label>
                <div class="relative mt-1">
                    <span class="absolute left-4 top-3.5">+91</span>
                    <input id="phone-input" type="tel" placeholder="98765 43210" class="w-full border rounded-xl py-3 pl-12 pr-4">
                </div>
            </div>
            <button onclick="sendOTP()" class="w-full bg-rose-500 text-white font-bold py-3 rounded-xl mt-6">Send OTP</button>
            <p class="text-center text-xs text-gray-400 mt-6">Demo OTP: 1234</p>
        </div>
    </div>

    <!-- OTP Screen -->
    <div id="otp-screen" class="absolute inset-0 z-50 bg-white flex flex-col p-6 hidden">
        <button onclick="showAuth()" class="w-10 h-10 rounded-full bg-gray-100 mb-4"><i class="fas fa-arrow-left"></i></button>
        <h2 class="text-2xl font-bold">Enter OTP</h2>
        <p class="text-gray-500 text-sm mt-1">Sent to +91 <span id="otp-phone"></span></p>
        <div class="flex gap-3 my-6 justify-center">
            <input type="text" maxlength="1" class="otp-input w-14 h-14 text-center text-2xl font-bold border rounded-xl">
            <input type="text" maxlength="1" class="otp-input w-14 h-14 text-center text-2xl font-bold border rounded-xl">
            <input type="text" maxlength="1" class="otp-input w-14 h-14 text-center text-2xl font-bold border rounded-xl">
            <input type="text" maxlength="1" class="otp-input w-14 h-14 text-center text-2xl font-bold border rounded-xl">
        </div>
        <button onclick="completeLogin()" class="w-full bg-rose-500 text-white font-bold py-3 rounded-xl">Verify & Login</button>
    </div>

    <!-- Main Header (after login) -->
    <header id="main-header" class="sticky top-0 bg-white border-b px-4 py-2 hidden">
        <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-rose-500 rounded-lg flex items-center justify-center text-white font-bold">S</div>
            <div class="flex-1"><h1 class="font-bold">ShopZen</h1><p class="text-[10px] text-gray-500"><i class="fas fa-map-marker-alt text-rose-500"></i> Delhi, 110001</p></div>
            <button onclick="showScreen('wishlist')" class="relative"><i class="fas fa-heart text-xl"></i><span id="wishlist-badge" class="absolute -top-1 -right-2 bg-rose-500 text-white text-[9px] w-4 h-4 rounded-full hidden">0</span></button>
            <button onclick="showScreen('profile')"><i class="fas fa-user-circle text-xl"></i></button>
        </div>
        <div class="relative mt-2">
            <input type="text" id="search-input" placeholder="Search products..." onkeyup="filterProducts()" class="w-full bg-gray-100 rounded-xl py-2.5 pl-10 pr-4 text-sm">
            <i class="fas fa-search absolute left-3 top-3 text-gray-400"></i>
        </div>
        <div class="flex gap-2 mt-2 overflow-x-auto no-scrollbar">
            <button data-cat="all" class="cat-chip active px-3 py-1 bg-rose-500 text-white text-xs rounded-full">All</button>
            <button data-cat="Men" class="cat-chip px-3 py-1 bg-gray-100 text-xs rounded-full">Men</button>
            <button data-cat="Women" class="cat-chip px-3 py-1 bg-gray-100 text-xs rounded-full">Women</button>
            <button data-cat="Kids" class="cat-chip px-3 py-1 bg-gray-100 text-xs rounded-full">Kids</button>
            <button data-cat="Electronics" class="cat-chip px-3 py-1 bg-gray-100 text-xs rounded-full">Electronics</button>
        </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto pb-20 bg-gray-50">
        <!-- Home Screen -->
        <div id="screen-home" class="screen">
            <div class="px-4 mt-2"><div class="rounded-xl overflow-hidden h-32 bg-gradient-to-r from-pink-500 to-purple-600 flex items-center justify-center text-white font-bold text-2xl">Mega Sale</div></div>
            <div class="px-4 mt-4"><div class="flex justify-between"><h3 class="font-bold">Flash Deals</h3><span class="text-rose-500 text-sm" onclick="showAllFlash()">View All</span></div><div id="flash-deals-container" class="flex gap-3 overflow-x-auto mt-2 pb-2"></div></div>
            <div class="px-4 mt-4"><div class="flex justify-between"><h3 class="font-bold">Products</h3></div><div id="products-container" class="grid grid-cols-2 gap-3 mt-2"></div></div>
        </div>

        <!-- Product Detail Screen -->
        <div id="screen-product" class="screen hidden bg-white pb-24"></div>

        <!-- Quick Order Flow: Step 1 - Address Details -->
        <div id="screen-quick-order-address" class="screen hidden flex flex-col h-full">
            <div class="sticky top-0 bg-white p-4 border-b flex items-center gap-3">
                <button onclick="showScreen('product')"><i class="fas fa-arrow-left"></i></button>
                <h2 class="font-bold text-xl">Order Details</h2>
            </div>
            <div class="flex-1 p-4 space-y-4 overflow-y-auto">
                <div class="bg-rose-50 p-3 rounded-xl text-center">
                    <p class="font-bold text-lg" id="quick-product-name"></p>
                    <p class="text-rose-600 font-bold text-xl" id="quick-product-price"></p>
                </div>
                <div class="space-y-3">
                    <input type="text" id="order-name" placeholder="Full Name" class="w-full border rounded-xl p-3">
                    <input type="tel" id="order-phone" placeholder="Phone Number" class="w-full border rounded-xl p-3">
                    <input type="text" id="order-pincode" placeholder="Pincode" class="w-full border rounded-xl p-3">
                    <input type="text" id="order-city" placeholder="City" class="w-full border rounded-xl p-3">
                    <textarea id="order-address" placeholder="Full Address (Street, House No.)" class="w-full border rounded-xl p-3" rows="2"></textarea>
                </div>
            </div>
            <div class="sticky bottom-0 bg-white p-4 border-t">
                <button onclick="goToPaymentStep()" class="w-full bg-rose-600 text-white font-bold py-3 rounded-xl">Next: Payment →</button>
            </div>
        </div>

        <!-- Quick Order Flow: Step 2 - Payment Method -->
        <div id="screen-quick-order-payment" class="screen hidden flex flex-col h-full">
            <div class="sticky top-0 bg-white p-4 border-b flex items-center gap-3">
                <button onclick="showScreen('quick-order-address')"><i class="fas fa-arrow-left"></i></button>
                <h2 class="font-bold text-xl">Select Payment</h2>
            </div>
            <div class="flex-1 p-4 space-y-4 overflow-y-auto">
                <div class="space-y-2">
                    <label class="flex items-center gap-3 p-3 border rounded-xl"><input type="radio" name="payment-method" value="cod" checked> <i class="fas fa-money-bill-wave w-6"></i> Cash on Delivery</label>
                    <label class="flex items-center gap-3 p-3 border rounded-xl"><input type="radio" name="payment-method" value="card"> <i class="fas fa-credit-card w-6"></i> Credit/Debit Card</label>
                    <label class="flex items-center gap-3 p-3 border rounded-xl"><input type="radio" name="payment-method" value="upi"> <i class="fas fa-mobile-alt w-6"></i> UPI (Google Pay, PhonePe)</label>
                    <label class="flex items-center gap-3 p-3 border rounded-xl"><input type="radio" name="payment-method" value="netbanking"> <i class="fas fa-university w-6"></i> Net Banking</label>
                </div>
            </div>
            <div class="sticky bottom-0 bg-white p-4 border-t">
                <button onclick="placeQuickOrder()" class="w-full bg-green-600 text-white font-bold py-3 rounded-xl text-lg">✅ Confirm Order</button>
            </div>
        </div>

        <!-- Cart Screen -->
        <div id="screen-cart" class="screen hidden flex flex-col h-full">
            <div class="sticky top-0 bg-white p-4 border-b flex items-center gap-3"><button onclick="showScreen('home')"><i class="fas fa-arrow-left"></i></button><h2 class="font-bold text-xl">My Cart</h2></div>
            <div id="cart-items-list" class="flex-1 p-4 space-y-3"></div>
            <div class="sticky bottom-0 bg-white p-4 border-t">
                <div class="flex justify-between mb-2"><span>Total</span><span id="cart-total">₹0</span></div>
                <input type="text" id="coupon-code" placeholder="Coupon code (SAVE10)" class="w-full border rounded-xl p-2 text-sm mb-2">
                <button onclick="applyCoupon()" class="w-full bg-rose-500 text-white py-2 rounded-xl">Apply Coupon</button>
                <button onclick="proceedToCheckout()" class="w-full bg-rose-600 text-white font-bold py-3 rounded-xl mt-3">Place Order</button>
            </div>
        </div>

        <!-- Wishlist Screen -->
        <div id="screen-wishlist" class="screen hidden p-4"><div class="flex items-center gap-3 mb-4"><button onclick="showScreen('home')"><i class="fas fa-arrow-left"></i></button><h2 class="font-bold text-xl">Wishlist</h2></div><div id="wishlist-items-list"></div></div>

        <!-- Orders Screen -->
        <div id="screen-orders" class="screen hidden p-4"><div class="flex items-center gap-3 mb-4"><button onclick="showScreen('home')"><i class="fas fa-arrow-left"></i></button><h2 class="font-bold text-xl">My Orders</h2></div><div id="orders-list"></div></div>

        <!-- Profile Screen -->
        <div id="screen-profile" class="screen hidden p-4"><div class="flex items-center gap-4"><div class="w-16 h-16 bg-rose-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">JD</div><div><h2 class="font-bold text-xl">John Doe</h2><p class="text-sm text-gray-500">+91 9876543210</p></div></div><div class="mt-6 space-y-2"><button onclick="showScreen('orders')" class="w-full flex justify-between items-center p-3 bg-gray-100 rounded-xl"><span>My Orders</span><i class="fas fa-chevron-right"></i></button><button onclick="showScreen('address-book')" class="w-full flex justify-between items-center p-3 bg-gray-100 rounded-xl"><span>Address Book</span><i class="fas fa-chevron-right"></i></button><button onclick="logout()" class="w-full bg-red-50 text-red-600 font-bold py-3 rounded-xl mt-4">Logout</button></div></div>

        <!-- Address Book -->
        <div id="screen-address-book" class="screen hidden p-4"><div class="flex items-center gap-3 mb-4"><button onclick="showScreen('profile')"><i class="fas fa-arrow-left"></i></button><h2 class="font-bold text-xl">Address Book</h2></div><div id="address-list"></div><button onclick="showAddAddress()" class="w-full bg-rose-500 text-white py-3 rounded-xl mt-4">+ Add New Address</button></div>

        <!-- Add Address -->
        <div id="screen-add-address" class="screen hidden p-4"><div class="flex items-center gap-3 mb-4"><button onclick="showScreen('address-book')"><i class="fas fa-arrow-left"></i></button><h2 class="font-bold text-xl">Add Address</h2></div><input type="text" id="addr-name" placeholder="Full Name" class="w-full border rounded-xl p-3 mb-2"><input type="text" id="addr-phone" placeholder="Phone" class="w-full border rounded-xl p-3 mb-2"><textarea id="addr-full" placeholder="Full Address" class="w-full border rounded-xl p-3"></textarea><button onclick="saveAddress()" class="w-full bg-rose-500 text-white py-3 rounded-xl mt-4">Save</button></div>

        <!-- Checkout Screen (from cart) -->
        <div id="screen-checkout" class="screen hidden flex flex-col h-full">
            <div class="sticky top-0 bg-white p-4 border-b flex items-center gap-3"><button onclick="showScreen('cart')"><i class="fas fa-arrow-left"></i></button><h2 class="font-bold text-xl">Checkout</h2></div>
            <div class="flex-1 p-4 space-y-4 overflow-y-auto">
                <div id="checkout-address" class="bg-gray-100 p-3 rounded-xl"><div class="flex justify-between"><span class="font-semibold">Delivery Address</span><button onclick="showScreen('address-book')" class="text-rose-500 text-sm">Change</button></div><p id="selected-address" class="text-sm mt-1">No address selected</p></div>
                <div id="checkout-items" class="space-y-2"></div>
                <div class="bg-gray-100 p-3 rounded-xl"><div class="flex justify-between"><span>Subtotal</span><span id="checkout-subtotal">₹0</span></div><div class="flex justify-between"><span>GST (18%)</span><span id="checkout-gst">₹0</span></div><div class="flex justify-between font-bold mt-2"><span>Total</span><span id="checkout-total">₹0</span></div></div>
                <div><h3 class="font-semibold mb-2">Payment Method</h3><label class="flex items-center gap-3 p-2 border rounded-xl"><input type="radio" name="payment" value="cod" checked> Cash on Delivery</label></div>
            </div>
            <div class="sticky bottom-0 bg-white p-4 border-t"><button onclick="placeOrder()" class="w-full bg-rose-600 text-white font-bold py-3 rounded-xl">Confirm Order</button></div>
        </div>
    </main>

    <!-- Bottom Nav -->
    <nav class="glass absolute bottom-0 left-0 right-0 flex justify-around py-2 border-t z-40 hidden" id="bottom-nav">
        <button onclick="showScreen('home')" class="nav-btn active flex flex-col items-center p-2 text-rose-500" data-screen="home"><i class="fas fa-home text-xl"></i><span class="text-[10px]">Home</span></button>
        <button onclick="showScreen('cart')" class="nav-btn flex flex-col items-center p-2 text-gray-500" data-screen="cart"><div class="relative"><i class="fas fa-shopping-cart text-xl"></i><span id="cart-badge" class="absolute -top-1 -right-2 bg-rose-500 text-white text-[9px] w-4 h-4 rounded-full hidden">0</span></div><span class="text-[10px]">Cart</span></button>
        <button onclick="showScreen('orders')" class="nav-btn flex flex-col items-center p-2 text-gray-500" data-screen="orders"><i class="fas fa-box text-xl"></i><span class="text-[10px]">Orders</span></button>
        <button onclick="showScreen('profile')" class="nav-btn flex flex-col items-center p-2 text-gray-500" data-screen="profile"><i class="fas fa-user text-xl"></i><span class="text-[10px]">Profile</span></button>
    </nav>

    <div id="toast" class="fixed top-20 left-1/2 transform -translate-x-1/2 bg-black text-white px-4 py-2 rounded-full text-sm opacity-0 transition-all z-50 pointer-events-none">Message</div>
</div>

<script>
    // Helper functions
    function showToast(msg) { let t=document.getElementById('toast'); t.innerText=msg; t.classList.remove('opacity-0'); t.classList.add('opacity-100'); setTimeout(()=>{ t.classList.remove('opacity-100'); t.classList.add('opacity-0'); },2500); }
    async function fetchJSON(url, opts={}) { try { let res=await fetch(url,opts); if(!res.ok) throw new Error(`HTTP ${res.status}`); return await res.json(); } catch(e){ showToast('Network error'); return null; } }

    // Auth (same as before)
    let currentPhone="";
    async function checkAuth() { let res=await fetchJSON('/api/check-auth'); if(res&&res.logged_in){ document.getElementById('auth-screen').classList.add('hidden'); document.getElementById('otp-screen').classList.add('hidden'); document.getElementById('main-header').classList.remove('hidden'); document.getElementById('bottom-nav').classList.remove('hidden'); loadHomePage(); loadCartCount(); loadWishlistCount(); showScreen('home'); } else { document.getElementById('auth-screen').classList.remove('hidden'); document.getElementById('main-header').classList.add('hidden'); document.getElementById('bottom-nav').classList.add('hidden'); } }
    function sendOTP() { let phone=document.getElementById('phone-input').value; if(phone.length<10){ showToast('Enter 10 digits'); return; } currentPhone=phone; document.getElementById('otp-phone').innerText=phone; document.getElementById('auth-screen').classList.add('hidden'); document.getElementById('otp-screen').classList.remove('hidden'); }
    function showAuth() { document.getElementById('otp-screen').classList.add('hidden'); document.getElementById('auth-screen').classList.remove('hidden'); }
    async function completeLogin() { let otp=Array.from(document.querySelectorAll('.otp-input')).map(i=>i.value).join(''); if(otp!=='1234'){ showToast('Invalid OTP'); return; } let res=await fetchJSON('/verify-otp',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone:currentPhone, otp})}); if(res&&res.success){ document.getElementById('otp-screen').classList.add('hidden'); document.getElementById('main-header').classList.remove('hidden'); document.getElementById('bottom-nav').classList.remove('hidden'); loadHomePage(); loadCartCount(); loadWishlistCount(); showScreen('home'); } else showToast('Login failed'); }
    async function logout() { await fetchJSON('/logout',{method:'POST'}); location.reload(); }

    // Products & Home
    let allProducts=[];
    async function loadHomePage() { let res=await fetchJSON('/api/products/all'); if(res&&res.products){ allProducts=res.products; renderFlashDeals(); filterProducts(); } }
    function renderFlashDeals() { let deals=allProducts.filter(p=>[1,2,3,8,9].includes(p.id)); document.getElementById('flash-deals-container').innerHTML=deals.map(p=>`<div class="min-w-[130px] bg-white rounded-xl p-2 shadow cursor-pointer" onclick="showProductDetail(${p.id})"><img src="${p.image}" class="w-full h-28 object-cover rounded-lg"><h4 class="text-sm font-semibold line-clamp-1">${p.name}</h4><div class="text-rose-600 font-bold">₹${p.price}</div></div>`).join(''); }
    function filterProducts() { let search=document.getElementById('search-input')?.value.toLowerCase()||''; let cat=document.querySelector('.cat-chip.active')?.dataset.cat||'all'; let filtered=allProducts.filter(p=> (cat==='all'||p.category===cat) && (search===''||p.name.toLowerCase().includes(search))); document.getElementById('products-container').innerHTML=filtered.map(p=>`<div class="bg-white rounded-xl overflow-hidden shadow cursor-pointer" onclick="showProductDetail(${p.id})"><img src="${p.image}" class="w-full h-40 object-cover"><div class="p-2"><h4 class="font-semibold line-clamp-2 text-sm">${p.name}</h4><div class="text-rose-600 font-bold">₹${p.price}</div></div></div>`).join(''); }
    document.querySelectorAll('.cat-chip').forEach(c=>c.addEventListener('click',function(){ document.querySelectorAll('.cat-chip').forEach(c=>c.classList.remove('bg-rose-500','text-white')); this.classList.add('bg-rose-500','text-white'); filterProducts(); }));

    // Product Detail (with Order Now button)
    async function showProductDetail(pid) {
        let res=await fetchJSON(`/api/product/${pid}`);
        if(!res||!res.product){ showToast('Product not found'); return; }
        let p=res.product;
        let sizesHtml=p.sizes?`<div class="mt-3"><p class="font-semibold">Size:</p><div class="flex gap-2 mt-1">${p.sizes.map(s=>`<button class="size-btn border rounded-full px-3 py-1 text-sm">${s}</button>`).join('')}</div></div>`:'';
        let colorsHtml=p.colors?`<div class="mt-3"><p class="font-semibold">Color:</p><div class="flex gap-2 mt-1">${p.colors.map(c=>`<button class="color-btn w-8 h-8 rounded-full border" style="background:${c.toLowerCase()}"></button>`).join('')}</div></div>`:'';
        let html=`<div class="relative"><img src="${p.image}" class="w-full h-72 object-cover"><button onclick="showScreen('home')" class="absolute top-4 left-4 w-10 h-10 bg-white rounded-full shadow"><i class="fas fa-arrow-left"></i></button><button onclick="addToWishlist(${p.id})" class="absolute top-4 right-4 w-10 h-10 bg-white rounded-full shadow"><i class="far fa-heart"></i></button></div>
        <div class="p-4"><h1 class="text-xl font-bold">${p.name}</h1><div class="flex items-center gap-2 mt-1"><i class="fas fa-star text-yellow-400"></i><span>${p.rating}</span><span>(${p.reviews_count} ratings)</span></div>
        <div class="flex items-baseline gap-2 mt-2"><span class="text-2xl font-bold text-rose-600">₹${p.price}</span><span class="text-sm line-through text-gray-400">₹${p.old_price}</span><span class="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded">${p.discount}% off</span></div>
        <p class="text-sm text-gray-600 mt-2">${p.description}</p><div class="mt-2 text-xs bg-gray-100 p-2 rounded">Seller: ${p.seller} ⭐ ${p.seller_rating} | Sold: ${p.sold}</div>
        ${sizesHtml}${colorsHtml}<div class="mt-4"><div class="flex gap-2"><textarea id="review-text" placeholder="Write a review..." class="flex-1 border rounded-xl p-2 text-sm"></textarea><button onclick="addReview(${p.id})" class="bg-rose-500 text-white px-4 py-2 rounded-xl text-sm">Post Review</button><button onclick="openOrderNow(${p.id})" class="bg-green-600 text-white px-4 py-2 rounded-xl text-sm">Order Now</button></div></div>
        <div id="reviews-list" class="mt-4 space-y-2"></div></div>
        <div class="fixed bottom-0 left-0 right-0 max-w-[450px] mx-auto bg-white p-3 border-t flex gap-3 z-20"><button onclick="addToCart(${p.id})" class="flex-1 border border-rose-500 text-rose-500 font-semibold py-2 rounded-xl">Add to Cart</button><button onclick="buyNow(${p.id})" class="flex-1 bg-rose-500 text-white font-semibold py-2 rounded-xl">Buy Now</button></div>`;
        document.getElementById('screen-product').innerHTML=html;
        showScreen('product');
        loadReviews(p.id);
        document.querySelectorAll('.size-btn, .color-btn').forEach(btn=>{ btn.onclick=()=>{ document.querySelectorAll('.size-btn, .color-btn').forEach(b=>b.classList.remove('border-2','border-rose-500')); btn.classList.add('border-2','border-rose-500'); }; });
    }
    async function loadReviews(pid) { let res=await fetchJSON(`/api/reviews/${pid}`); if(res&&res.reviews) document.getElementById('reviews-list').innerHTML=res.reviews.map(r=>`<div class="bg-gray-100 p-2 rounded"><div class="flex justify-between"><span class="font-semibold">${r.user}</span><span class="text-xs">${r.date}</span></div><p class="text-sm">${r.text}</p></div>`).join(''); else document.getElementById('reviews-list').innerHTML='<p>No reviews yet</p>'; }
    async function addReview(pid) { let text=document.getElementById('review-text')?.value; if(!text) return; await fetchJSON('/api/add-review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_id:pid, text})}); showToast('Review added'); loadReviews(pid); document.getElementById('review-text').value=''; }

    // Order Now Flow
    let currentOrderProduct = null;
    function openOrderNow(pid) {
        let product = allProducts.find(p=>p.id===pid);
        if(!product) return;
        currentOrderProduct = product;
        document.getElementById('quick-product-name').innerText = product.name;
        document.getElementById('quick-product-price').innerHTML = `₹${product.price}`;
        // Clear previous form values
        document.getElementById('order-name').value = '';
        document.getElementById('order-phone').value = '';
        document.getElementById('order-pincode').value = '';
        document.getElementById('order-city').value = '';
        document.getElementById('order-address').value = '';
        showScreen('quick-order-address');
    }
    function goToPaymentStep() {
        let name = document.getElementById('order-name').value.trim();
        let phone = document.getElementById('order-phone').value.trim();
        let pincode = document.getElementById('order-pincode').value.trim();
        let city = document.getElementById('order-city').value.trim();
        let address = document.getElementById('order-address').value.trim();
        if(!name || !phone || !pincode || !city || !address) {
            showToast('Please fill all address details');
            return;
        }
        if(phone.length<10) { showToast('Enter valid phone number'); return; }
        if(pincode.length<6) { showToast('Enter valid pincode'); return; }
        // Store in sessionStorage for order placement
        sessionStorage.setItem('order_name', name);
        sessionStorage.setItem('order_phone', phone);
        sessionStorage.setItem('order_pincode', pincode);
        sessionStorage.setItem('order_city', city);
        sessionStorage.setItem('order_address', address);
        showScreen('quick-order-payment');
    }
    async function placeQuickOrder() {
        if(!currentOrderProduct) return;
        let paymentMethod = document.querySelector('input[name="payment-method"]:checked').value;
        let name = sessionStorage.getItem('order_name');
        let phone = sessionStorage.getItem('order_phone');
        let pincode = sessionStorage.getItem('order_pincode');
        let city = sessionStorage.getItem('order_city');
        let address = sessionStorage.getItem('order_address');
        // Simulate order placement
        let orderData = {
            product: currentOrderProduct,
            quantity: 1,
            total: currentOrderProduct.price,
            customer: {name, phone, address, pincode, city},
            payment: paymentMethod,
            date: new Date().toISOString()
        };
        // Send to backend (same as cart order but single item)
        let res = await fetchJSON('/api/place-quick-order', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify(orderData)
        });
        if(res && res.success) {
            showToast(`✅ Order placed successfully! Order ID: ${res.order_id}`);
            // Clear session storage
            sessionStorage.removeItem('order_name');
            sessionStorage.removeItem('order_phone');
            sessionStorage.removeItem('order_pincode');
            sessionStorage.removeItem('order_city');
            sessionStorage.removeItem('order_address');
            currentOrderProduct = null;
            showScreen('orders');
            loadOrders(); // refresh orders list
        } else {
            showToast('Order failed. Please try again.');
        }
    }

    // Cart (unchanged but ensure buyNow works)
    async function loadCartCount() { let res=await fetchJSON('/api/cart/count'); if(res){ let badge=document.getElementById('cart-badge'); if(res.count>0){ badge.innerText=res.count; badge.classList.remove('hidden'); badge.classList.add('flex'); } else badge.classList.add('hidden'); } }
    async function addToCart(pid) { let res=await fetchJSON('/api/cart/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_id:pid})}); if(res&&res.success){ loadCartCount(); showToast('Added to cart'); } }
    async function buyNow(pid) { await addToCart(pid); showScreen('cart'); }
    async function loadCartScreen() { let res=await fetchJSON('/api/cart'); if(!res) return; let container=document.getElementById('cart-items-list'); if(res.items.length===0){ container.innerHTML='<p class="text-center text-gray-500">Cart empty</p>'; document.getElementById('cart-total').innerText='₹0'; return; } container.innerHTML=res.items.map(item=>`<div class="flex gap-3 bg-gray-100 p-3 rounded-xl"><img src="${item.product.image}" class="w-20 h-20 object-cover rounded"><div class="flex-1"><h4 class="font-semibold">${item.product.name}</h4><div class="flex justify-between items-center mt-1"><div class="flex gap-2"><button onclick="updateCartQty(${item.product.id},-1)" class="w-6 h-6 bg-white rounded-full">-</button><span>${item.quantity}</span><button onclick="updateCartQty(${item.product.id},1)" class="w-6 h-6 bg-white rounded-full">+</button></div><span class="font-bold">₹${item.product.price*item.quantity}</span><button onclick="removeFromCart(${item.product.id})" class="text-red-500 text-xs">Remove</button></div></div></div>`).join(''); document.getElementById('cart-total').innerText=`₹${res.total}`; }
    async function updateCartQty(pid,delta) { await fetchJSON('/api/cart/update',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_id:pid, delta})}); loadCartCount(); loadCartScreen(); }
    async function removeFromCart(pid) { await fetchJSON('/api/cart/remove',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_id:pid})}); loadCartCount(); loadCartScreen(); showToast('Removed'); }
    let couponDiscount=0;
    function applyCoupon() { let code=document.getElementById('coupon-code').value; if(code==='SAVE10'){ couponDiscount=10; showToast('Coupon applied! 10% off'); loadCartScreen(); } else showToast('Invalid coupon'); }
    async function proceedToCheckout() { let res=await fetchJSON('/api/cart'); if(!res||res.items.length===0){ showToast('Cart empty'); return; } let subtotal=res.total; let gst=Math.round(subtotal*0.18); let total=subtotal+gst; if(couponDiscount) total=Math.round(total*(1-couponDiscount/100)); document.getElementById('checkout-subtotal').innerText=`₹${subtotal}`; document.getElementById('checkout-gst').innerText=`₹${gst}`; document.getElementById('checkout-total').innerText=`₹${total}`; document.getElementById('checkout-items').innerHTML=res.items.map(item=>`<div class="flex justify-between"><span>${item.product.name} x${item.quantity}</span><span>₹${item.product.price*item.quantity}</span></div>`).join(''); showScreen('checkout'); }
    async function placeOrder() { let res=await fetchJSON('/api/place-order',{method:'POST'}); if(res&&res.success){ showToast('Order placed!'); loadCartCount(); couponDiscount=0; showScreen('orders'); } else showToast('Order failed'); }

    // Wishlist
    async function loadWishlistCount() { let res=await fetchJSON('/api/wishlist/count'); if(res){ let badge=document.getElementById('wishlist-badge'); if(res.count>0){ badge.innerText=res.count; badge.classList.remove('hidden'); } else badge.classList.add('hidden'); } }
    async function addToWishlist(pid) { let res=await fetchJSON('/api/wishlist/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_id:pid})}); if(res&&res.success){ loadWishlistCount(); showToast('Added to wishlist'); } }
    async function loadWishlistScreen() { let res=await fetchJSON('/api/wishlist'); if(!res) return; let container=document.getElementById('wishlist-items-list'); if(res.items.length===0){ container.innerHTML='<p class="text-center text-gray-500">Empty</p>'; return; } container.innerHTML=res.items.map(item=>`<div class="flex gap-3 bg-gray-100 p-3 rounded-xl"><img src="${item.image}" class="w-20 h-20 object-cover rounded"><div><h4 class="font-semibold">${item.name}</h4><div class="flex justify-between items-center mt-1"><span class="font-bold">₹${item.price}</span><button onclick="removeFromWishlist(${item.id})" class="text-red-500 text-sm">Remove</button></div></div></div>`).join(''); }
    async function removeFromWishlist(pid) { await fetchJSON('/api/wishlist/remove',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_id:pid})}); loadWishlistCount(); loadWishlistScreen(); showToast('Removed'); }

    // Orders
    async function loadOrders() { let res=await fetchJSON('/api/orders'); if(!res) return; let container=document.getElementById('orders-list'); if(res.orders.length===0){ container.innerHTML='<p class="text-center text-gray-500">No orders</p>'; return; } container.innerHTML=res.orders.map(o=>`<div class="bg-gray-100 p-3 rounded-xl mb-2"><div class="flex justify-between"><span class="font-semibold">Order #${o.id}</span><span class="text-xs bg-green-200 px-2 rounded-full">${o.status}</span></div><p class="text-xs text-gray-500">${o.date}</p><div>${o.items.map(i=>`<div class="flex justify-between text-sm"><span>${i.name} x${i.qty}</span><span>₹${i.price*i.qty}</span></div>`).join('')}</div><div class="font-bold mt-1">Total: ₹${o.total}</div></div>`).join(''); }

    // Address Book (localStorage)
    let addresses=JSON.parse(localStorage.getItem('addresses')||'[]');
    function loadAddressBook() { let container=document.getElementById('address-list'); if(addresses.length===0){ container.innerHTML='<p class="text-gray-500">No addresses</p>'; return; } container.innerHTML=addresses.map((a,idx)=>`<div class="bg-gray-100 p-3 rounded-xl mb-2"><p class="font-semibold">${a.name}</p><p>${a.phone}</p><p>${a.address}</p><button onclick="selectAddress(${idx})" class="text-rose-500 text-sm mt-1">Select</button></div>`).join(''); }
    function saveAddress() { let name=document.getElementById('addr-name').value, phone=document.getElementById('addr-phone').value, address=document.getElementById('addr-full').value; if(name&&phone&&address){ addresses.push({name,phone,address}); localStorage.setItem('addresses',JSON.stringify(addresses)); showToast('Address saved'); showScreen('address-book'); loadAddressBook(); } else showToast('Fill all fields'); }
    function selectAddress(idx) { let addr=addresses[idx]; document.getElementById('selected-address').innerHTML=`${addr.name}, ${addr.address}, ${addr.phone}`; showScreen('checkout'); }
    function showAddAddress() { showScreen('add-address'); }

    // Screen navigation
    function showScreen(screenName) { document.querySelectorAll('.screen').forEach(s=>s.classList.add('hidden')); document.getElementById(`screen-${screenName}`)?.classList.remove('hidden'); document.querySelectorAll('.nav-btn').forEach(btn=>{ btn.classList.remove('text-rose-500'); btn.classList.add('text-gray-500'); if(btn.dataset.screen===screenName) btn.classList.remove('text-gray-500'), btn.classList.add('text-rose-500'); }); if(screenName==='cart') loadCartScreen(); if(screenName==='orders') loadOrders(); if(screenName==='wishlist') loadWishlistScreen(); if(screenName==='address-book') loadAddressBook(); }
    function showAllFlash() { showToast('All flash deals'); }
    setInterval(()=>{ document.getElementById('clock').innerText=new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}); },1000);
    document.querySelectorAll('.otp-input').forEach((inp,idx)=>{ inp.addEventListener('keyup',(e)=>{ if(e.target.value.length===1&&idx<3) document.querySelectorAll('.otp-input')[idx+1].focus(); }); });
    checkAuth();

    // ---------- PWA: Register Service Worker ----------
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js').then(reg => console.log('SW registered')).catch(err => console.log('SW registration failed', err));
    }
</script>
</body>
</html>
"""

# ---------- Flask Routes (add quick order endpoint) ----------
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/check-auth')
def check_auth():
    return {'logged_in': 'user' in session}

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    if data.get('otp') == '1234':
        session['user'] = {'phone': data.get('phone'), 'name': 'John Doe'}
        return {'success': True}
    return {'success': False}

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    session.pop('cart', None)
    session.pop('wishlist', None)
    return {'success': True}

@app.route('/api/products/all')
def api_all_products():
    return {'products': PRODUCTS}

@app.route('/api/product/<int:pid>')
def api_product(pid):
    p = get_product(pid)
    return {'product': p} if p else ({}, 404)

@app.route('/api/reviews/<int:pid>')
def api_reviews(pid):
    return {'reviews': session.get(f'reviews_{pid}', [])}

@app.route('/api/add-review', methods=['POST'])
def add_review():
    data = request.json
    pid = data['product_id']
    text = data['text']
    reviews = session.get(f'reviews_{pid}', [])
    reviews.append({'user': session.get('user', {}).get('name', 'User'), 'text': text, 'date': datetime.now().strftime("%d %b")})
    session[f'reviews_{pid}'] = reviews[-5:]
    return {'success': True}

def get_cart():
    return session.get('cart', {})
def save_cart(cart):
    session['cart'] = cart

@app.route('/api/cart/count')
def cart_count():
    cart = get_cart()
    count = sum(item['quantity'] for item in cart.values())
    return {'count': count}

@app.route('/api/cart/add', methods=['POST'])
def cart_add():
    data = request.json
    pid = data['product_id']
    product = get_product(pid)
    if not product:
        return {'success': False}, 404
    cart = get_cart()
    key = str(pid)
    if key in cart:
        cart[key]['quantity'] += 1
    else:
        cart[key] = {'product_id': pid, 'quantity': 1, 'product': product}
    save_cart(cart)
    return {'success': True}

@app.route('/api/cart/update', methods=['POST'])
def cart_update():
    data = request.json
    pid = str(data['product_id'])
    delta = data['delta']
    cart = get_cart()
    if pid in cart:
        new_qty = cart[pid]['quantity'] + delta
        if new_qty <= 0:
            del cart[pid]
        else:
            cart[pid]['quantity'] = new_qty
        save_cart(cart)
    return {'success': True}

@app.route('/api/cart/remove', methods=['POST'])
def cart_remove():
    pid = str(request.json['product_id'])
    cart = get_cart()
    if pid in cart:
        del cart[pid]
        save_cart(cart)
    return {'success': True}

@app.route('/api/cart')
def api_cart():
    cart = get_cart()
    items = list(cart.values())
    total = sum(item['product']['price'] * item['quantity'] for item in items)
    return {'items': items, 'total': total}

def get_wishlist():
    return session.get('wishlist', {})
def save_wishlist(wl):
    session['wishlist'] = wl

@app.route('/api/wishlist/count')
def wishlist_count():
    return {'count': len(get_wishlist())}

@app.route('/api/wishlist/add', methods=['POST'])
def wishlist_add():
    pid = request.json['product_id']
    product = get_product(pid)
    if not product:
        return {'success': False}
    wl = get_wishlist()
    wl[str(pid)] = product
    save_wishlist(wl)
    return {'success': True}

@app.route('/api/wishlist/remove', methods=['POST'])
def wishlist_remove():
    pid = str(request.json['product_id'])
    wl = get_wishlist()
    if pid in wl:
        del wl[pid]
        save_wishlist(wl)
    return {'success': True}

@app.route('/api/wishlist')
def api_wishlist():
    wl = get_wishlist()
    items = list(wl.values())
    return {'items': items}

# Place order from cart
@app.route('/api/place-order', methods=['POST'])
def place_order():
    if 'user' not in session:
        return {'success': False}, 401
    cart = get_cart()
    if not cart:
        return {'success': False}
    total = sum(item['product']['price'] * item['quantity'] for item in cart.values())
    gst = int(total * 0.18)
    grand = total + gst
    orders = session.get('orders', [])
    order_id = len(orders) + 1001
    items = [{'name': item['product']['name'], 'qty': item['quantity'], 'price': item['product']['price']} for item in cart.values()]
    statuses = ['Processing', 'Shipped', 'Out for Delivery', 'Delivered']
    orders.append({
        'id': order_id,
        'date': datetime.now().strftime("%d %b %Y, %I:%M %p"),
        'status': random.choice(statuses),
        'items': items,
        'total': grand
    })
    session['orders'] = orders
    session['cart'] = {}
    return {'success': True}

# New endpoint for quick order (single product)
@app.route('/api/place-quick-order', methods=['POST'])
def place_quick_order():
    if 'user' not in session:
        return {'success': False}, 401
    data = request.json
    product = data['product']
    quantity = data['quantity']
    customer = data['customer']
    payment = data['payment']
    total = product['price'] * quantity
    gst = int(total * 0.18)
    grand = total + gst
    orders = session.get('orders', [])
    order_id = len(orders) + 2001
    items = [{'name': product['name'], 'qty': quantity, 'price': product['price']}]
    statuses = ['Processing', 'Shipped', 'Out for Delivery', 'Delivered']
    orders.append({
        'id': order_id,
        'date': datetime.now().strftime("%d %b %Y, %I:%M %p"),
        'status': random.choice(statuses),
        'items': items,
        'total': grand,
        'customer': customer,
        'payment_method': payment
    })
    session['orders'] = orders
    return {'success': True, 'order_id': order_id}

@app.route('/api/orders')
def api_orders():
    return {'orders': session.get('orders', [])}

# ---------- PWA Routes (Added without changing anything else) ----------
@app.route('/manifest.json')
def manifest():
    return {
        "name": "ShopZen",
        "short_name": "ShopZen",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#f43f5e",
        "icons": [
            {"src": "https://cdn-icons-png.flaticon.com/512/888/888879.png", "sizes": "192x192", "type": "image/png"}
        ]
    }

@app.route('/sw.js')
def sw():
    return """self.addEventListener('fetch', function(event) { event.respondWith(fetch(event.request)); });""", 200, {'Content-Type': 'application/javascript'}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
