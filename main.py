import uvicorn
import sys
import os

if __name__ == "__main__":
    # Ensure src is in the python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    print("Starting HoloSecure FastAPI Backend on port 8000...")
    try:
        uvicorn.run("src.api.server:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"Server Error: {e}")
        sys.exit(1)
