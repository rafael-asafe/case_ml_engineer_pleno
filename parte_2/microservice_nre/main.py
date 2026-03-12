from fastapi import FastAPI

from microservice_nre.lifespan import lifespan
from microservice_nre.middleware import request_middleware
from microservice_nre.routers import health, model, predict

app = FastAPI(title='NRE Service', lifespan=lifespan)

# intercepta requisições para adicionar informações rastreio
app.middleware('http')(request_middleware)

# roteadores para endpoints da aplicação
app.include_router(model.router)
app.include_router(health.router)
app.include_router(predict.router)


@app.get('/')
async def root() -> dict[str, str]:
    return {'message': 'Hello World'}
