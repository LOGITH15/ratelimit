from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app= FastAPI()

origins= [
    "http://localhost",
    "http://localhost:3000",
    "null",
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class SubmitData(BaseModel):
    name: str
    message: str

@app.post("/submit")
def submit(data: SubmitData):
    return {"received": data.model_dump()}

@app.get("/")
def home():
    return {"message": "Hello from FastAPI with CORS setup!"}
