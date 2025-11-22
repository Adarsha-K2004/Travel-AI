from fastapi import FastAPI
from agents.parent_agent import ParentAgent

app = FastAPI()
agent = ParentAgent()

@app.get("/")
def home():
    return {"message": "Tourism Multi-Agent System is running!"}

@app.get("/ask")
def ask(question: str):
    result = agent.process_request(question)
    return {"response": result}
