from fastapi import FastAPI

from .routes import pixel

app = FastAPI()
app.include_router(pixel.router)
