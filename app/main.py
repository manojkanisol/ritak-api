from fastapi import FastAPI
from .api.v1.endpoints import embedding, chat

app = FastAPI(title="Resource Server (Ritak)", version="0.0.1")
app.include_router(embedding.router, prefix="/api/v1", tags=["embedding"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])