import os
import sys
import subprocess

def main():
    print("=================================================================")
    print("  Starting MARKETIQ AI — Intelligent Marketing Intelligence App  ")
    print("  Tagline: 'Turn Marketing Spend into Measurable Growth'         ")
    print("=================================================================")
    
    # Launch Streamlit server
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=8501", "--server.headless=false"]
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nMARKETIQ AI shut down gracefully.")

if __name__ == "__main__":
    main()
