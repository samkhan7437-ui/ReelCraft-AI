import sys
import uvicorn
from app.config import HOST, PORT

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("   [REELCRAFT AI] Faceless Video Studio & Auto-Poster")
    print(f"   Studio running at: http://{HOST}:{PORT}")
    print("   Open your browser to start creating viral reels!")
    print("="*60 + "\n")
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)
