import os
import shutil
import site

def fix_nvidia_dlls():
    """
    Brute force fix for Windows DLL search issues: 
    Finds pip-installed NVIDIA DLLs and copies them directly into the .venv Scripts folder.
    """
    venv_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(venv_base, ".venv", "Scripts")
    
    if not os.path.exists(target_dir):
        # Fallback to current environment's Scripts if running inside venv
        target_dir = os.path.join(sys.prefix, "Scripts")
    
    print(f"Target Directory for DLL injection: {target_dir}")
    
    found_any = False
    for site_pkg in site.getsitepackages():
        nvidia_base = os.path.join(site_pkg, 'nvidia')
        if not os.path.exists(nvidia_base):
            continue
            
        print(f"Searching for DLLs in {nvidia_base}...")
        for root, dirs, files in os.walk(nvidia_base):
            for file in files:
                if file.endswith(".dll"):
                    source_path = os.path.join(root, file)
                    dest_path = os.path.join(target_dir, file)
                    
                    if not os.path.exists(dest_path):
                        print(f"  Copying: {file}")
                        try:
                            shutil.copy2(source_path, dest_path)
                            found_any = True
                        except Exception as e:
                            print(f"    Failed to copy {file}: {e}")
                    else:
                        print(f"  Already exists: {file}")
                        found_any = True
                        
    if found_any:
        print("\nDLL injection complete! Try running the script again.")
    else:
        print("\nNo NVIDIA DLLs found in site-packages. Did you run 'pip install nvidia-cublas-cu12'?")

if __name__ == "__main__":
    import sys
    fix_nvidia_dlls()
