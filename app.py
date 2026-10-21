from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
from banco import criar_banco

app = Flask(__name__)


# ===== PRODUTOS DA LOJA =====

PRODUTOS = {
    1: {"nome": "Cupcake de Chocolate", "preco": 8.00},
    2: {"nome": "Cupcake de Morango", "preco": 9.00},
    3: {"nome": "Cupcake de Baunilha", "preco": 7.00},
    4: {"nome": "Cupcake de pistache", "preco": 10.00},
    5: {"nome": "Cupcake de mirtilo com limão", "preco": 9.00},
    6: {"nome": "Cupcake red velvet", "preco": 9.00 }
}


# ===== CONECTAR AO BANCO DE DADOS =====

def conectar_banco():
    conexao = sqlite3.connect("sweetcake.db")
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


# ===== PÁGINA INICIAL DA LOJA =====

@app.route("/")
def inicio():
    return render_template("index.html")

# ===== PÁGINA DE ACOMPANHAMENTO DO PEDIDO =====

@app.route("/acompanhar", methods=["GET"])
def acompanhar_pedido():
    pedido_id = request.args.get("pedido_id", "").strip()

    if not pedido_id.isdigit() or int(pedido_id) < 1:
        return render_template(
            "acompanhar.html",
            pedido=None,
            consultou=False,
            erro="Informe um número de pedido válido."
        )

    with conectar_banco() as conexao:
        pedido = conexao.execute(
            """
            SELECT id, status
            FROM pedidos
            WHERE id = ?
            """,
            (int(pedido_id),)
        ).fetchone()

    return render_template(
        "acompanhar.html",
        pedido=pedido,
        consultou=True,
        erro=None
    )


# ===== SALVAR PEDIDO =====

@app.route("/api/pedidos", methods=["POST"])
def salvar_pedido():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Dados do pedido inválidos."}), 400

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    endereco = dados.get("endereco", "")
    telefone = dados.get("telefone", "")
    observacoes = dados.get("observacoes", "")
    itens = dados.get("itens")

    if not all(isinstance(valor, str) for valor in
               [nome, email, endereco, telefone, observacoes]):
        return jsonify({"erro": "Os dados do cliente são inválidos."}), 400

    nome = nome.strip()
    email = email.strip()
    endereco = endereco.strip()
    telefone = telefone.strip()
    observacoes = observacoes.strip()

    if not nome or not endereco or not telefone:
        return jsonify({
            "erro": "Preencha nome, endereço e telefone."
        }), 400

    if not isinstance(itens, list) or not itens:
        return jsonify({"erro": "O carrinho está vazio."}), 400

    total = 0
    itens_validos = []

    try:
        for item in itens:
            if not isinstance(item, dict):
                return jsonify({
                    "erro": "Os dados dos itens são inválidos."
                }), 400

            produto_id = int(item["id"])
            quantidade = int(item["quantidade"])

            if produto_id not in PRODUTOS or quantidade < 1:
                return jsonify({
                    "erro": "Produto ou quantidade inválidos."
                }), 400

            produto = PRODUTOS[produto_id]

            total += produto["preco"] * quantidade

            itens_validos.append((
                produto["nome"],
                quantidade,
                produto["preco"]
            ))

        with conectar_banco() as conexao:

            cursor = conexao.execute(
                """
                INSERT INTO pedidos
                (nome, email, endereco, telefone, observacoes, total)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (nome, email, endereco, telefone, observacoes, total)
            )

            pedido_id = cursor.lastrowid

            for produto, quantidade, preco in itens_validos:
                conexao.execute(
                    """
                    INSERT INTO itens_pedido
                    (pedido_id, produto, quantidade, preco_unitario)
                    VALUES (?, ?, ?, ?)
                    """,
                    (pedido_id, produto, quantidade, preco)
                )

        return jsonify({
            "mensagem": "Pedido salvo com sucesso!",
            "pedido_id": pedido_id,
            "total": round(total, 2)
        }), 201

    except (KeyError, TypeError, ValueError):
        return jsonify({
            "erro": "Os dados dos itens são inválidos."
        }), 400

    except sqlite3.Error:
        app.logger.exception("Erro ao salvar pedido")

        return jsonify({
            "erro": "Não foi possível salvar o pedido."
        }), 500


# ===== CONSULTAR PEDIDOS E SEUS PRODUTOS =====

@app.route("/pedidos")
def consultar_pedidos():
    conexao = conectar_banco()

    pedidos = conexao.execute(
        """
        SELECT id, nome, email, endereco, telefone,
               observacoes, total, data_pedido, status
        FROM pedidos
        ORDER BY id DESC
        """
    ).fetchall()

    itens_por_pedido = {}

    for pedido in pedidos:
        itens = conexao.execute(
            """
            SELECT produto, quantidade, preco_unitario
            FROM itens_pedido
            WHERE pedido_id = ?
            """,
            (pedido[0],)
        ).fetchall()

        itens_por_pedido[pedido[0]] = itens

    conexao.close()

    return render_template(
        "pedidos.html",
        pedidos=pedidos,
        itens_por_pedido=itens_por_pedido
    )

# ===== ATUALIZAR STATUS DO PEDIDO =====

@app.route("/atualizar_status/<int:pedido_id>", methods=["POST"])
def atualizar_status(pedido_id):
    novo_status = request.form.get("status", "").strip()

    status_validos = [
        "Pedido recebido",
        "Em preparo",
        "Saiu para entrega",
        "Entregue"
    ]

    if novo_status not in status_validos:
        return "Status inválido.", 400

    with conectar_banco() as conexao:
        resultado = conexao.execute(
            "SELECT id FROM pedidos WHERE id = ?",
            (pedido_id,)
        ).fetchone()

        if resultado is None:
            return "Pedido não encontrado.", 404

        conexao.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?",
            (novo_status, pedido_id)
        )

    return redirect("/pedidos")


# ===== INICIAR O SERVIDOR =====

criar_banco()

if __name__ == "__main__":
    app.run(debug=True)

