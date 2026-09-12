import json
import urllib.request
import os

REPO = "NuvioMedia/NuvioMobile"
API_URL = f"https://api.github.com/repos/{REPO}/releases/latest"

def main():
    req = urllib.request.Request(API_URL)
    req.add_header('User-Agent', 'Mozilla/5.0')
    
    # Use the workflow's GitHub token to avoid IP rate limits
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())

    # Extract relevant release data
    version = data.get("tag_name", "").lstrip("v")
    version_date = data.get("published_at")
    version_desc = data.get("body", "Latest official release of Nuvio Mobile")

    # Find the .ipa download link
    ipa_url = None
    ipa_size = 0
    for asset in data.get("assets", []):
        if asset["name"].endswith(".ipa"):
            ipa_url = asset["browser_download_url"]
            ipa_size = asset["size"]
            break

    if not ipa_url:
        print("No IPA found in the latest release.")
        return

    # Create the base AltStore manifest structure
    manifest = {
        "name": "Nuvio Auto-Update Repo",
        "identifier": "com.custom.nuvio.repo",
        "apps": [{
            "name": "Nuvio",
            "bundleIdentifier": "com.nuvio.app",
            "developerName": "NuvioMedia",
            "localizedDescription": "A free, open-source media app for your phone, your desktop, and the TV you already own.",
            "iconURL": "https://nuvio.tv/assets/nuvio-app-logo-wordmark.webp",
            "tintColor": "#000000"
        }]
    }

    # Load existing manifest if it exists to preserve custom changes
    if os.path.exists("apps.json"):
        with open("apps.json", "r") as f:
            try:
                manifest = json.load(f)
            except Exception:
                pass

    # Update app details with the latest release info
    app = manifest["apps"][0]
    app["version"] = version
    app["versionDate"] = version_date
    app["versionDescription"] = version_desc
    app["downloadURL"] = ipa_url
    app["size"] = ipa_size

    # Save the updated manifest
    with open("apps.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Successfully updated apps.json to Nuvio version {version}")

if __name__ == "__main__":
    main()
