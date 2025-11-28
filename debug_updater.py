import urllib.request
import json
import ssl

def check_github_releases():
    url = "https://api.github.com/repos/andiusndd/Ultimate_Bak3/releases"
    print(f"Checking: {url}")
    
    try:
        context = ssl._create_unverified_context()
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Python-Debug-Script')
        
        with urllib.request.urlopen(req, context=context) as response:
            data = json.loads(response.read().decode())
            
        if len(data) > 0:
            latest = data[0]
            print(f"LATEST: {latest.get('tag_name')}")
            print(f"Name: {latest.get('name')}")
            print(f"Zipball: {latest.get('zipball_url')}")
            
            assets = latest.get('assets', [])
            if assets:
                print(f"Assets ({len(assets)}):")
                for a in assets:
                    print(f" - {a.get('name')}")
            else:
                print("NO ASSETS FOUND (Will use Source Code Zip)")
        else:
            print("No releases found.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_github_releases()
