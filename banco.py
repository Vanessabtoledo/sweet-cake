import sqlite3



def criar_banco():
    conexao = sqlite3.connect("sweetcake.db")
    cursor = conexao.cursor()

    # Cria a tabela de pedidos, caso ainda não exista
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT,
            endereco TEXT NOT NULL,
            telefone TEXT NOT NULL,
            observacoes TEXT,
            total REAL NOT NULL,
            data_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Verifica quais colunas já existem
    cursor.execute("PRAGMA table_info(pedidos)")
    colunas = [coluna[1] for coluna in cursor.fetchall()]

    # Adiciona email caso ainda não exista
    if "email" not in colunas:
        cursor.execute(
            "ALTER TABLE pedidos ADD COLUMN email TEXT"
        )

    # Adiciona status caso ainda não exista
    if "status" not in colunas:
        cursor.execute("""
            ALTER TABLE pedidos
            ADD COLUMN status TEXT NOT NULL
            DEFAULT 'Pedido recebido'
        """)

    # Cria a tabela de itens do pedido
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
        )
    """)

    conexao.commit()
    conexao.close()

    print("Banco de dados da Sweet Cake criado com sucesso!")


if __name__ == "__main__":
    criar_banco()