

 // ===== PRODUTOS DA LOJA =====
const produtos = [
    { id: 1, nome: "Cupcake de Chocolate", preco: 8.00 },
    { id: 2, nome: "Cupcake de Morango", preco: 9.00 },
    { id: 3, nome: "Cupcake de baunilha", preco:7.00 },
    { id: 4, nome: "Cupcake de pistache", preco:10.00},
    { id: 5, nome: "Cupcake de mirtilo com limão", preco: 9.00},
    { id: 6, nome: "Cupcake red velvet", preco: 9.00 }

];

// ===== CARRINHO DE COMPRAS =====
let carrinho = [];

// ===== FORMATAR PREÇOS =====
function formatarPreco(valor) {
    return valor.toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL"
    });
}

// ===== ADICIONAR AO CARRINHO =====
function adicionarAoCarrinho(id) {
    const produto = produtos.find(function(item) {
        return item.id === id;
    });

    if (!produto) return;

    const itemCarrinho = carrinho.find(function(item) {
        return item.id === id;
    });

    if (itemCarrinho) {
        itemCarrinho.quantidade++;
    } else {
        carrinho.push({
            id: produto.id,
            nome: produto.nome,
            preco: produto.preco,
            quantidade: 1
        });
    }

    atualizarCarrinho();
}

// ===== ATUALIZAR CARRINHO =====
function atualizarCarrinho() {
    const areaCarrinho = document.getElementById("itens-carrinho");
    const areaTotal = document.getElementById("total");

    areaCarrinho.innerHTML = "";

    if (carrinho.length === 0) {
        areaCarrinho.innerHTML = "<p>Seu carrinho está vazio.</p>";
        areaTotal.textContent = formatarPreco(0);
        return;
    }

    carrinho.forEach(function(item) {
        const linha = document.createElement("div");
        linha.className = "item-carrinho";

        const nome = document.createElement("p");
        const nomeForte = document.createElement("strong");
        nomeForte.textContent = item.nome;
        nome.appendChild(nomeForte);
        linha.appendChild(nome);

        const preco = document.createElement("p");
        preco.textContent = "Preço unitário: " + formatarPreco(item.preco);
        linha.appendChild(preco);

        const controles = document.createElement("div");
        controles.className = "controles-quantidade";

        const botaoMenos = document.createElement("button");
        botaoMenos.type = "button";
        botaoMenos.textContent = "−";
        botaoMenos.addEventListener("click", function() {
            alterarQuantidade(item.id, -1);
        });

        const quantidade = document.createElement("span");
        quantidade.textContent = " Quantidade: " + item.quantidade + " ";

        const botaoMais = document.createElement("button");
        botaoMais.type = "button";
        botaoMais.textContent = "+";
        botaoMais.addEventListener("click", function() {
            alterarQuantidade(item.id, 1);
        });

        controles.appendChild(botaoMenos);
        controles.appendChild(quantidade);
        controles.appendChild(botaoMais);
        linha.appendChild(controles);

        const subtotal = document.createElement("p");
        subtotal.textContent =
            "Subtotal: " + formatarPreco(item.preco * item.quantidade);
        linha.appendChild(subtotal);

        const remover = document.createElement("button");
        remover.type = "button";
        remover.className = "botao-remover";
        remover.textContent = "Remover produto";
        remover.addEventListener("click", function() {
            removerDoCarrinho(item.id);
        });
        linha.appendChild(remover);

        linha.appendChild(document.createElement("hr"));
        areaCarrinho.appendChild(linha);
    });

    const total = carrinho.reduce(function(soma, item) {
        return soma + item.preco * item.quantidade;
    }, 0);

    areaTotal.textContent = formatarPreco(total);
}

// ===== ALTERAR QUANTIDADE =====
function alterarQuantidade(id, variacao) {
    const item = carrinho.find(function(produto) {
        return produto.id === id;
    });

    if (!item) return;

    item.quantidade += variacao;

    if (item.quantidade <= 0) {
        removerDoCarrinho(id);
        return;
    }

    atualizarCarrinho();
}

// ===== REMOVER PRODUTO =====
function removerDoCarrinho(id) {
    carrinho = carrinho.filter(function(item) {
        return item.id !== id;
    });

    atualizarCarrinho();
}

// ===== ABRIR A FINALIZAÇÃO =====
function mostrarFinalizacao() {
    if (carrinho.length === 0) {
        alert("Adicione pelo menos um cupcake ao carrinho!");
        return;
    }

    document.getElementById("finalizacao").scrollIntoView({
        behavior: "smooth"
    });
}

// ===== ENVIAR E SALVAR PEDIDO NO BANCO =====
document.getElementById("formulario-pedido").addEventListener(
    "submit",
    async function(event) {
        event.preventDefault();

        if (carrinho.length === 0) {
            alert("Adicione pelo menos um cupcake ao carrinho!");
            return;
        }

        const nome = document.getElementById("nome").value.trim();
        const email = document.getElementById("email").value.trim();
        const endereco = document.getElementById("endereco").value.trim();
        const telefone = document.getElementById("telefone").value.trim();
        const observacoes = document.getElementById("observacoes").value.trim();

        if (!nome || !endereco || !telefone) {
            alert("Preencha seu nome, endereço e telefone.");
            return;
        }

        const dadosPedido = {
            nome: nome,
            email: email,
            endereco: endereco,
            telefone: telefone,
            observacoes: observacoes,
            itens: carrinho.map(function(item) {
                return {
                    id: item.id,
                    quantidade: item.quantidade
                };
            })
        };

        const botaoConfirmar = event.submitter;
        if (botaoConfirmar) {
            botaoConfirmar.disabled = true;
            botaoConfirmar.textContent = "Salvando pedido...";
        }

        try {
            const resposta = await fetch("/api/pedidos", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(dadosPedido)
            });

            const resultado = await resposta.json();

            if (!resposta.ok) {
                alert(resultado.erro || "Não foi possível salvar o pedido.");
                return;
            }

            const confirmacao = document.getElementById("confirmacao");
            confirmacao.replaceChildren();

            const titulo = document.createElement("h3");
            titulo.textContent = "Pedido confirmado!";
            confirmacao.appendChild(titulo);

            const numero = document.createElement("p");
            numero.textContent = "Número do pedido: " + resultado.pedido_id;
            confirmacao.appendChild(numero);

            const total = document.createElement("p");
            total.textContent = "Total: " + formatarPreco(resultado.total);
            confirmacao.appendChild(total);

            const agradecimento = document.createElement("p");
            agradecimento.textContent =
                "Obrigada por escolher a Sweet Cake! 🧁";
            confirmacao.appendChild(agradecimento);

            confirmacao.scrollIntoView({ behavior: "smooth" });

            carrinho = [];
            atualizarCarrinho();
            document.getElementById("formulario-pedido").reset();

        } catch (erro) {
            console.error("Erro ao enviar pedido:", erro);
            alert(
                "Não foi possível conectar ao servidor. " +
                "Verifique se o Python está funcionando."
            );
        } finally {
            if (botaoConfirmar) {
                botaoConfirmar.disabled = false;
                botaoConfirmar.textContent = "Confirmar pedido";
            }
        }
    }
);

// ===== INICIAR O CARRINHO =====
atualizarCarrinho();

