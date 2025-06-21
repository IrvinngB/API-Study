from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from contextlib import asynccontextmanager

# Importar routers
from routers import auth, classes, tasks, calendar, habits, analytics, sync

# Configuración de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 StudyVault API iniciando...")
    print(f"🌍 Entorno: {'Desarrollo' if os.getenv('DEBUG', 'False').lower() == 'true' else 'Producción'}")
    yield
    # Shutdown
    print("🛑 StudyVault API cerrando...")

app = FastAPI(
    title="StudyVault API",
    description="API para la aplicación de gestión de estudios StudyVault",
    version="1.0.0",
    lifespan=lifespan
)

# Configuración de CORS más permisiva para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8081",
        "http://192.168.*.*:8081",  # Para desarrollo móvil
        "https://*.vercel.app",
        "https://*.netlify.app",
        "exp://192.168.*.*:8081",  # Para Expo
        "*"  # Temporal para debugging - REMOVER EN PRODUCCIÓN
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
)

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request, call_next):
    import time
    start_time = time.time()
    
    print(f"🌐 {request.method} {request.url}")
    print(f"📋 Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    print(f"⏱️  Procesado en {process_time:.4f}s - Status: {response.status_code}")
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "StudyVault API está funcionando correctamente",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Bienvenido a StudyVault API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(classes.router, prefix="/classes", tags=["Clases"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tareas"])
app.include_router(calendar.router, prefix="/calendar", tags=["Calendario"])
app.include_router(habits.router, prefix="/habits", tags=["Hábitos"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analíticas"])
app.include_router(sync.router, prefix="/sync", tags=["Sincronización"])

# Manejo global de errores
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    print(f"❌ HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print(f"💥 Unhandled Exception: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "status_code": 500,
            "error_type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
