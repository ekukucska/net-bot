from fastapi import FastAPI

app = FastAPI(
    title="NetBot",
    description="Rule-based network diagnostics chatbot",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"status": "ok", "app": "NetBot"}
