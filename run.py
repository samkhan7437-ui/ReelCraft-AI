import os
import sys
import uvicorn

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

if __name__ == "__main__":
    # Render, Railway, and other cloud providers pass the port via $PORT
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")

    print("\n" + "="*60)
    print("   [REELCRAFT AI] Faceless Video Studio & Auto-Poster")
    print(f"   Studio running at: http://{host}:{port}")
    print("   Open your browser to start creating viral reels!")
    print("="*60 + "\n")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
