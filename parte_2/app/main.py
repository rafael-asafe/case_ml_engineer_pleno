from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": " Hello World"}


@app.post("/load")
async def load():
    """ Registra uma nova versão do modelo caso não exista baixa uma o modelo"""
    return {"message": " not implemented"}

@app.get("/list")
async def list_request():
    """ Lista as predições realizadas"""
    return {"message": " not implemented"}

@app.get("/models")
async def list_models():
    """ Lista as predições realizadas"""
    return {"message": " not implemented"}

@app.post("/predict")
async def predict():
    """ Realiza inferência utilizando o modelo ativo ou uma versão específica."""
    return {"message": " not implemented"}

@app.delete("/models/{version}")
async def delete_model(version):
    """deleta versão específica do modelo"""
    return {"message": " not implemented"}
    
@app.get("/health")
async def health_status():
    """confere saude da aplicação"""
    return {"message": " not implemented"}



