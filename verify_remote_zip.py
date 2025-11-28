import urllib.request
import json
import ssl
import zipfile
import io
import os

def verify_remote_zip():
    print("--- VERIFYING REMOTE GITHUB RELEASE ---")
    url = "https://api.github.com/repos/andiusndd/Ultimate_Bak3/releases"
    
    try:
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Python-Debug-Script')
        
        print("1. Fetching releases...")
        with urllib.request.urlopen(req, context=context) as response:
            data = json.loads(response.read().decode())
            
        if not data:
            print("No releases found!")
            return

        latest = data[0]
        tag = latest.get('tag_name')
        print(f"2. Latest Release: {tag}")
        
        assets = latest.get('assets', [])
        download_url = None
        
        if assets:
            asset = assets[0]
            print(f"3. Found Asset: {asset.get('name')}")
            download_url = asset.get('browser_download_url')
        else:
            print("3. No assets found, using Source Code Zip")
            download_url = latest.get('zipball_url')
            
        print(f"4. Downloading from: {download_url}")
        
        # Download zip into memory
        req_zip = urllib.request.Request(download_url)
        req_zip.add_header('User-Agent', 'Python-Debug-Script')
        
        with urllib.request.urlopen(req_zip, context=context) as response:
            zip_data = response.read()
            
        print(f"5. Downloaded {len(zip_data)} bytes")
        
        # Inspect zip content
        print("6. Inspecting zip content...")
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            # Find __init__.py
            init_file = None
            for name in z.namelist():
                if name.endswith("__init__.py") and "Ultimate_Bak3" in name:
                    init_file = name
                    break
                # Also check root level if structure is flat
                if name == "__init__.py" or name.endswith("/__init__.py"):
                     init_file = name
            
            if init_file:
                print(f"   Found init file: {init_file}")
                with z.open(init_file) as f:
                    content = f.read().decode('utf-8')
                    # Find version line
                    for line in content.splitlines():
                        if '"version":' in line or "'version':" in line:
                            print(f"   >>> REMOTE VERSION IN ZIP: {line.strip()}")
            else:
                print("   ❌ Could not find __init__.py in zip!")
                print("   Zip contents (first 10):")
                for n in z.namelist()[:10]:
                    print(f"    - {n}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_remote_zip()
