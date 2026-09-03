from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="Servico de Pedidos")

ESTOQUE_URL = "http://localhost:8001"

class NovoPedido(BaseModel):
    produto_id: int
    quantidade: int

@app.post("/pedidos", status_code=201)
def criar_pedido(pedido: NovoPedido):
    url = f"{ESTOQUE_URL}/produtos/{pedido.produto_id}/estoque"
    try:
        resposta = httpx.get(url, timeout=3.0)
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Servico de estoque indisponivel"
        )
    
    if resposta.status_code == 404:
        raise HTTPException(status_code=400, detail="Produto inexistente")
    if resposta.status_code != 200:
        raise HTTPException(status_code=502, detail="Falha ao consultar estoque")
    
    estoque = resposta.json()
    if estoque["quantidade_disponivel"] < pedido.quantidade:
        raise HTTPException(status_code=409, detail="Estoque insuficiente")
    
    return {
        "pedido_id": 1,
        "status": "aceito",
        "produto_id": pedido.produto_id,
        "quantidade": pedido.quantidade,
    }