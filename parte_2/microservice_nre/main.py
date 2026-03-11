from fastapi import FastAPI

from microservice_nre.routers import health, model, predict

app = FastAPI(title='NRE Service')

app.include_router(model.router)
app.include_router(health.router)
app.include_router(predict.router)


@app.get('/')
async def root() -> None:
    return {'message': 'Hello World'}
