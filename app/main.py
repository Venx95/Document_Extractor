from fastapi import FastAPI

app = FastAPI(title="Intelligent Document Extraction Platform")

@app.get("/")
def health_check():
    return {"status": "running"}