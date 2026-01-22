// Dados dos Produtos (Simulação)
const products = [
    { id: 1, name: "SmartPhone Alpha", price: 1200.00 },
    { id: 2, name: "Celular Beta Pro", price: 2500.00 },
    { id: 3, name: "Phone Gamma Lite", price: 899.90 },
    { id: 4, name: "Ultra Phone X", price: 4500.00 },
    { id: 5, name: "Foldable Z", price: 6200.00 },
    { id: 6, name: "Mini Phone S", price: 1500.00 }
];

let cart = [];

// Renderiza os produtos na tela
function renderCatalog() {
    const catalog = document.getElementById('catalog');
    catalog.innerHTML = ""; // Limpa

    products.forEach(product => {
        const div = document.createElement('div');
        div.className = 'product-card';
        div.innerHTML = `
            <div class="placeholder-img">Imagem Celular</div>
            <h3>${product.name}</h3>
            <p class="price">R$ ${product.price.toFixed(2).replace('.', ',')}</p>
            <button class="add-btn" onclick="addToCart(${product.id})">Adicionar ao Carrinho</button>
        `;
        catalog.appendChild(div);
    });
}

// Adiciona item ao carrinho
function addToCart(id) {
    const product = products.find(p => p.id === id);
    cart.push(product);
    updateCartDisplay();
}

// Atualiza o contador e a lista do modal
function updateCartDisplay() {
    // Atualiza contador no topo
    document.getElementById('cart-count').innerText = cart.length;

    // Atualiza lista no modal
    const cartList = document.getElementById('cart-items');
    cartList.innerHTML = "";
    
    let total = 0;

    cart.forEach((item, index) => {
        total += item.price;
        const li = document.createElement('li');
        li.className = 'cart-item';
        li.innerHTML = `
            <span>${item.name}</span>
            <span>R$ ${item.price.toFixed(2).replace('.', ',')} 
            <a href="#" onclick="removeFromCart(${index})" style="color:red; margin-left:10px; text-decoration:none;">X</a></span>
        `;
        cartList.appendChild(li);
    });

    document.getElementById('cart-total-value').innerText = total.toFixed(2).replace('.', ',');
}

// Remove item do carrinho (bônus)
function removeFromCart(index) {
    cart.splice(index, 1);
    updateCartDisplay();
}

// Abre/Fecha o Modal
function toggleCart() {
    const modal = document.getElementById('cart-modal');
    // Se estiver visível (block ou flex), esconde. Se não, mostra.
    if (modal.style.display === 'block') {
        modal.style.display = 'none';
    } else {
        modal.style.display = 'block';
    }
}

// Finalizar compra (Apenas alerta)
function checkout() {
    if (cart.length === 0) {
        alert("Seu carrinho está vazio!");
    } else {
        alert(`Compra finalizada! Total: R$ ${document.getElementById('cart-total-value').innerText}`);
        cart = [];
        updateCartDisplay();
        toggleCart();
    }
}

// Inicializa
renderCatalog();