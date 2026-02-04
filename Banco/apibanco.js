const API = "http://127.0.0.1:5000";

// POST - cadastrar cliente
function cadastrar() {
    const nome = document.getElementById("nome").value;
    const cpf = document.getElementById("cpf").value;

    fetch(`${API}/clientes`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            nome: nome,
            cpf: cpf
        })
    })
    .then(res => res.json())
    .then(data => {
        alert("Cliente cadastrado!");
        listar();
    })
    .catch(err => console.error(err));
}

// GET - listar clientes
function listar() {
    fetch(`${API}/clientes`)
        .then(res => res.json())
        .then(clientes => {
            const lista = document.getElementById("lista");
            lista.innerHTML = "";

            clientes.forEach(c => {
                const li = document.createElement("li");
                li.innerText = `${c.id} - ${c.nome} | Saldo: R$ ${c.saldo}`;
                lista.appendChild(li);
            });
        });
}