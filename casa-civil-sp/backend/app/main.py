from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import deputies, municipalities, secretariats, programs, dashboard

app = FastAPI(
    title="Casa Civil SP API",
    description="API do Centro de Governo — Casa Civil do Estado de São Paulo",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(deputies.router)
app.include_router(municipalities.router)
app.include_router(secretariats.router)
app.include_router(programs.router)
app.include_router(dashboard.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "casa-civil-sp"}
