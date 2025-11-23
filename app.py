"""
FastAPI Backend for Image Authenticity Detector
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import shutil
import os
import json
import pickle
from typing import List, Optional
import numpy as np
from datetime import datetime

from baseline_detector import predict as baseline_predict

# Initialize FastAPI app
app = FastAPI(
    title="Image Authenticity Detector API",
    description="PCA-based detector for real vs AI-generated images",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = Path("uploads")
REAL_DIR = UPLOAD_DIR / "real"
FAKE_DIR = UPLOAD_DIR / "fake"
TEST_DIR = UPLOAD_DIR / "test"
MODELS_DIR = Path("models")
HISTORY_DIR = Path("history")
CACHE_DIR = Path("cache")

# Create directories
for dir_path in [UPLOAD_DIR, REAL_DIR, FAKE_DIR, TEST_DIR, MODELS_DIR, HISTORY_DIR, CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Model persistence file
MODEL_FILE = MODELS_DIR / "latest_model.pkl"
MODEL_INFO_FILE = MODELS_DIR / "latest_model_info.json"

# Baseline detector - no training needed!
# Uses statistical features and rule-based classification


@app.get("/")
async def root():
    """Root endpoint - serve React app"""
    return FileResponse("frontend/dist/index.html")


@app.get("/api/status")
async def get_status():
    """Get detector status"""
    return {
        "status": "ready",
        "detector": detector_status,
        "message": "Baseline detector ready - no training required"
    }


# Training endpoints removed - baseline detector doesn't need training


@app.post("/api/predict")
async def predict_image(file: UploadFile = File(...)):
    """Predict authenticity of an uploaded image - No training required!"""
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save temporarily
        import uuid
        unique_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
        temp_path = TEST_DIR / unique_name
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Predict using baseline detector (no training needed)
        result = baseline_predict(temp_path)
        
        # Clean up
        if temp_path.exists():
            temp_path.unlink()
        
        return {
            "success": True,
            "filename": file.filename,
            "prediction": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/predict/batch")
async def predict_batch(files: List[UploadFile] = File(...)):
    """Predict authenticity of multiple images - No training required!"""
    
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="No files provided"
        )
    
    try:
        results = []
        temp_files = []
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "predictions": []
        }
        
        import uuid
        
        for file in files:
            try:
                # Handle file content type check
                content_type = getattr(file, 'content_type', None)
                filename = getattr(file, 'filename', 'unknown.jpg')
                
                # Check file extension if content_type not available
                if not content_type:
                    ext = Path(filename).suffix.lower()
                    if ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
                        results.append({
                            "filename": filename,
                            "success": False,
                            "error": "Not a supported image format"
                        })
                        continue
                elif content_type and not content_type.startswith("image/"):
                    results.append({
                        "filename": filename,
                        "success": False,
                        "error": "Not an image"
                    })
                    continue
                
                # Generate unique filename to avoid conflicts
                unique_name = f"{uuid.uuid4().hex[:8]}_{filename}"
                temp_path = TEST_DIR / unique_name
                temp_files.append(temp_path)
                
                # Save file
                with open(temp_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # Verify file was saved and is readable
                if not temp_path.exists() or temp_path.stat().st_size == 0:
                    results.append({
                        "filename": filename,
                        "success": False,
                        "error": "File upload failed"
                    })
                    continue
                
                # Predict using baseline detector (no training needed)
                result = baseline_predict(temp_path)
                results.append({
                    "filename": filename,
                    "success": True,
                    "prediction": result
                })
                
                # Save to history
                history_entry["predictions"].append({
                    "filename": filename,
                    "label": result.get("label", "unknown"),
                    "confidence": result.get("confidence", 0.0),
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                error_msg = str(e)
                filename = getattr(file, 'filename', 'unknown')
                results.append({
                    "filename": filename,
                    "success": False,
                    "error": error_msg
                })
                print(f"Error predicting {filename}: {error_msg}")
                import traceback
                traceback.print_exc()
        
        # Save prediction history
        if history_entry["predictions"]:
            try:
                history_file = HISTORY_DIR / f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(history_file, "w") as f:
                    json.dump(history_entry, f, indent=2)
            except Exception as e:
                print(f"Failed to save history: {e}")
        
        # Clean up temp files
        for temp_path in temp_files:
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except Exception as e:
                print(f"Failed to delete temp file {temp_path}: {e}")
        
        return {
            "success": True,
            "results": results,
            "total": len(results),
            "successful": sum(1 for r in results if r.get("success", False))
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/api/stats")
async def get_statistics():
    """Get detector statistics"""
    return {
        "trained": True,
        "type": "baseline",
        "message": "Baseline detector - no training required",
        "features_used": [
            "gradient_variance",
            "gradient_entropy", 
            "high_frequency_ratio",
            "edge_density",
            "gradient_correlation"
        ]
    }


@app.get("/api/history")
async def get_prediction_history():
    """Get prediction history"""
    try:
        history_files = sorted(HISTORY_DIR.glob("predictions_*.json"), reverse=True)
        history = []
        for hist_file in history_files[:50]:  # Last 50 sessions
            try:
                with open(hist_file, "r") as f:
                    history.append(json.load(f))
            except:
                continue
        return {"success": True, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory")
async def get_memory_stats():
    """Get memory and storage statistics"""
    try:
        import psutil
        import os
        
        # System memory
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('.')
        
        # Directory sizes
        def get_dir_size(path):
            total = 0
            try:
                for entry in os.scandir(path):
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += get_dir_size(entry.path)
            except:
                pass
            return total
        
        uploads_size = get_dir_size(UPLOAD_DIR)
        models_size = get_dir_size(MODELS_DIR)
        history_size = get_dir_size(HISTORY_DIR)
        
        return {
            "success": True,
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_percent": round(disk.used / disk.total * 100, 2)
            },
            "storage": {
                "uploads_mb": round(uploads_size / (1024**2), 2),
                "models_mb": round(models_size / (1024**2), 2),
                "history_mb": round(history_size / (1024**2), 2),
                "total_mb": round((uploads_size + models_size + history_size) / (1024**2), 2)
            }
        }
    except ImportError:
        return {
            "success": False,
            "message": "psutil not installed. Install with: pip install psutil"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/reset")
async def reset_detector():
    """Reset detector (reinitializes baseline detector)"""
    global detector
    detector = BaselineDetector()
    return {"success": True, "message": "Detector reset to baseline"}


# Serve uploaded images
@app.get("/uploads/real/{filename}")
async def get_real_image(filename: str):
    """Serve real training images"""
    file_path = REAL_DIR / filename
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Image not found")

@app.get("/uploads/fake/{filename}")
async def get_fake_image(filename: str):
    """Serve fake training images"""
    file_path = FAKE_DIR / filename
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Image not found")

# Mount static files (React build)
try:
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
except:
    pass  # Frontend not built yet


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

