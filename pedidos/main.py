from fastapi import FastAPI, HTTPException, Header, Response
from pydantic import BaseModel, Field
import httpx
import uuid

app = FastAPI(title="Servico de Pedidos")
ESTOQUE_URL = "http://localhost:8001"

pedidos_db = {}
contador_pedidos = 1

class NovoPedido(BaseModel):
    produto_id: int
    # D9: 
    quantidade: int = Field(gt=0, description="A quantidade deve ser maior que zero")

@app.post("/pedidos", status_code=201)
def criar_pedido(
    pedido: NovoPedido, 
    response: Response, 
    x_correlation_id: str | None = Header(default=None) # D12:
):
    global contador_pedidos

    if not x_correlation_id:
        x_correlation_id = str(uuid.uuid4())

    url = f"{ESTOQUE_URL}/produtos/{pedido.produto_id}/estoque"
    
    # D12:
    headers_para_estoque = {"x-correlation-id": x_correlation_id}

    try:
        resposta = httpx.get(url, headers=headers_para_estoque, timeout=3.0)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Servico de estoque indisponivel")

    if resposta.status_code == 404:
        raise HTTPException(status_code=400, detail="Produto inexistente")
    if resposta.status_code != 200:
        raise HTTPException(status_code=502, detail="Falha ao consultar estoque")

    estoque = resposta.json()
    if estoque["quantidade_disponivel"] < pedido.quantidade:
        raise HTTPException(status_code=409, detail="Estoque insuficiente")

    # Desafio 10:
    pedido_id = contador_pedidos
    contador_pedidos += 1
    
    pedido_criado = {
        "pedido_id": pedido_id,
        "status": "aceito",
        "produto_id": pedido.produto_id,
        "quantidade": pedido.quantidade,
    }
    pedidos_db[pedido_id] = pedido_criado

    # D11:
    response.headers["Location"] = f"/pedidos/{pedido_id}"
    
    return pedido_criado

# D10:
@app.get("/pedidos/{pedido_id}")
def buscar_pedido(pedido_id: int):
    if pedido_id not in pedidos_db:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    return pedidos_db[pedido_id]