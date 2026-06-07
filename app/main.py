import os
import math
import time
import socket
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="K8s FastAPI Demo",
    description="Aplikasi demonstrasi Kubernetes untuk proyek akhir",
    version="1.0.0"
)

# ENDPOINT 1: Root Health Check & Info Pod
@app.get("/")
async def root():
    return JSONResponse({
        "status": "healthy",
        "message": "Selamat datang di K8s FastAPI Demo",
        "pod_name": socket.gethostname(),
        "app_environment": os.getenv("APP_ENV", "unknown"),
        "app_version": os.getenv("APP_VERSION", "unknown"),
        "log_level": os.getenv("LOG_LEVEL", "unknown"),
    })

# ENDPOINT 2: Secret Membaca Data Sensitif
@app.get("/secret-info")
async def secret_info():
    db_password = os.getenv("DB_PASSWORD", "NOT_SET")
    api_key = os.getenv("API_KEY", "NOT_SET")
    
    masked_password = db_password[:3] + "****" if len(db_password) > 3 else "*****"
    masked_api_key = api_key[:5] + "****" if len(api_key) > 5 else "*****"
    
    return JSONResponse({
        "message": "Secret berhasil di-inject dari Kubernetes Secret",
        "db_password_preview": masked_password,
        "api_key_preview": masked_api_key,
        "secret_injection_status": "SUCCESS" if db_password != "NOT_SET" else "FAILED"
    })

# ENDPOINT 3: Load Test Simulasi Beban CPU
@app.get("/load-test")
async def load_test(duration: int = 5, intensity: int = 1000):
    start_time = time.time()
    result = 0
    end_time = start_time + duration
    
    while time.time() < end_time:
        for i in range(intensity):
            result += math.sqrt(i) * math.sin(i) * math.cos(i)
            
    elapsed = time.time() - start_time
    
    return JSONResponse({
        "message": f"Komputasi CPU selesai dalam {elapsed:.2f} detik",
        "pod_name": socket.gethostname(),
        "duration_requested": duration,
        "computation_result": result % 1000,
        "status": "load_test_complete"
    })

# ENDPOINT 4: Health Check untuk Kubernetes Probe
@app.get("/health")
async def health():
    return {"status": "ok"}
