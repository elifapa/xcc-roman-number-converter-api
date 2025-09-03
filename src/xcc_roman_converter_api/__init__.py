from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

# sys.process["easyconvert"]

@app.get("/")
async def root():
    return {"message": "Hello Elif!"}

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}

@app.post("/items/")
async def create_item(item: Item):
    return {"item": item}

def main() -> None:
    print("Hello from xcc-roman-converter-api!")
    app()
