from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="hackathon-practice")


class EchoRequest(BaseModel):
    message: str


class EchoResponse(BaseModel):
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/echo", response_model=EchoResponse)
def echo(payload: EchoRequest):
    return EchoResponse(message=payload.message)
