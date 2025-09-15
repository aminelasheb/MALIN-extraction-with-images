import os
import shutil
import subprocess
import sys

# Directories to reset each run
DIRS_TO_RESET = ["files_images", "output"]

def reset_directories():
    """Delete and recreate fresh empty target directories."""
    for directory in DIRS_TO_RESET:
        try:
            shutil.rmtree(directory, ignore_errors=True)  # nuke everything
            os.makedirs(directory, exist_ok=True)         # recreate
            print(f"[OK] Reset: {directory}")
        except Exception as e:
            print(f"[ERR] Could not reset {directory}: {e}")
            sys.exit(1)

def run_script(script_name):
    """Run a Python script, stream its output live, and wait until it's finished."""
    print(f"\n[RUN] Running {script_name}...")

    process = subprocess.Popen(
        [sys.executable, script_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    # Stream script output line by line
    for line in iter(process.stdout.readline, ''):
        if line:
            print(line, end="")
        else:
            break

    process.stdout.close()
    process.wait()

    if process.returncode == 0:
        print(f"[OK] {script_name} finished successfully")
    else:
        print(f"[ERR] {script_name} failed. Stopping pipeline.")
        sys.exit(1)

if __name__ == "__main__":
    # ✅ Reset dirs once, avoid permission errors
    reset_directories()

    # Strict sequential order
    run_script("detectImages.py")
    run_script("cropImages.py")
    run_script("drawBoxes.py")
    run_script("extraction-gemini-vision.py")

    print("\n[DONE] All tasks completed successfully!")
