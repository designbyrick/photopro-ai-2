from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="PhotoPro AI API",
    description="AI-powered professional photo generation platform",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "message": "PhotoPro AI API is running!",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
