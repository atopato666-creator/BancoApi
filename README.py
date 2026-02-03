# BancoApi 
from flask import Flask, jsonify, request
import sqlite3
import requests
import re

app = Flask(__name__)
DATABASE = "Bancodb"

#validar cpf 
def validar_cpf(cpf):
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Verifica se tem 11 dígitos ou se todos os dígitos são iguais (ex: 111.111.111-11)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Cálculo do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    digito_1 = 0 if resto == 10 else resto

    # Cálculo do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    digito_2 = 0 if resto == 10 else resto

    # Compara os dígitos calculados com os dígitos reais
    return cpf[-2:] == f"{digito_1}{digito_2}"


#----------------------
# Funcão para a conexão 
#----------------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------------
# Criar tabela (1ª execução)
# ----------------------

def criar_tabela():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL,
            saldo INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# ---------------------------
# GET - listar usuarios
# ---------------------------
@app.route("/banco", methods=["GET"])
def listar_usuarios():
    conn = get_db_connection()
    usuarios = conn.execute("SELECT * FROM usuarios").fetchall()
    conn.close()

    return jsonify([dict(usuario) for usuario in usuarios])

# ---------------------------
# GET - buscar usuario por id
# ---------------------------
@app.route("/banco/<int:id>", methods=["GET"])
def buscar_usuario(id):
    conn = get_db_connection()
    usuario = conn.execute(
        "SELECT * FROM usuarios WHERE id = ?", (id,)
    ).fetchone()
    conn.close()

    if usuario is None:
        return jsonify({"erro": "usuario não encontrado"}), 404

    return jsonify(dict(usuario))

# ---------------------------
# POST - criar usuario
# ---------------------------
@app.route("/banco", methods=["POST"])
def criar_usuario():
    dados = request.json

    if "nome" not in dados or "cpf" not in dados:
        return jsonify({"erro": "nome e cpf são obrigatórios"}), 400
    if not validar_cpf(dados["cpf"]):
        return jsonify({"erro": "CPF inválido"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO usuarios (nome, cpf,saldo) VALUES (?, ?, ?)",
    (dados["nome"], dados["cpf"], 0)
)

    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "id": novo_id,
        "nome": dados["nome"],
        "cpf": dados["cpf"],
        "saldo": 0
}), 201

# ---------------------------
# Atualizar saldo
# ---------------------------
@app.route("/banco/<int:id>/depositar", methods=["POST"])
def depositar(id):
    dados = request.json
    valor = dados.get("valor")
    if not valor or valor <= 0:
        return jsonify({"erro": "Valor inválido"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT saldo FROM usuarios WHERE id = ?", (id,))
    usuario = cursor.fetchone()
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    novo_saldo = usuario["saldo"] + valor
    cursor.execute("UPDATE usuarios SET saldo = ? WHERE id = ?", (novo_saldo, id))
    conn.commit()
    conn.close()

    return jsonify({"id": id, "saldo": novo_saldo, "mensagem": "Depósito realizado com sucesso"})
# ---------------------------
# Saque bancario
# ---------------------------
@app.route("/banco/<int:id>/sacar", methods=["POST"])
def sacar(id):
    dados = request.json
    valor = dados.get("valor")
    if not valor or valor <= 0:
        return jsonify({"erro": "Valor inválido"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT saldo FROM usuarios WHERE id = ?", (id,))
    usuario = cursor.fetchone()
    if not usuario or usuario["saldo"] < valor:
        return jsonify({"erro": "Saldo insuficiente ou usuário não encontrado"}), 400

    novo_saldo = usuario["saldo"] - valor
    cursor.execute("UPDATE usuarios SET saldo = ? WHERE id = ?", (novo_saldo, id))
    conn.commit()
    conn.close()

    return jsonify({"id": id, "saldo": novo_saldo})
if __name__ == "__main__":
    criar_tabela()
app.run(debug=True)

url = "http://127.0.0.1:5000/banco"

payload = {
    "nome": "Mariana",
    "cpf": "529.982.247-25"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print("Status:", response.status_code)
print("Resposta:", response.json())



