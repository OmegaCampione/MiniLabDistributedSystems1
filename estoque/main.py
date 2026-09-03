from fastapi import FastAPI, HTTPException

app = FastAPI(title="Servico de Estoque")

produtos = {
    1: {"nome": "Teclado", "quantidade": 10},
    2: {"nome": "Mouse", "quantidade": 0},
    3: {"nome": "Monitor", "quantidade": 4},
}

@app.get("/produtos/{produto_id}/estoque")
def consultar_estoque(produto_id: int):
    produto = produtos.get(produto_id)
    if produto is None:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    return {
        "produto_id": produto_id,
        "nome": produto["nome"],
        "quantidade_disponivel": produto["quantidade"],
    }