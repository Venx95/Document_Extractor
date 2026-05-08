"""
Entrypoint — keeps main.py to an absolute minimum.
All wiring lives in app/factory.py.
"""
import uvicorn

from app.services.factory import create_app

app = create_app()


if __name__ == "__main__":
    from app.core.config import get_settings

    s = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=s.DEBUG,
        log_config=None,  # We manage logging ourselves
    )
@app.get("/")
def root():
    return {"message": "Document Extraction API Running"}