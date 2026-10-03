import urllib.request
import subprocess
import os
import sys

def download_and_install():
    url = "https://files.pythonhosted.org/packages/8a/13/2e4ba13f67fc4db43489ce933d4a25d5b6a167967b0f8a62ce09273ff83e/deltalake-1.5.1-cp310-abi3-win_amd64.whl"
    whl_path = "deltalake-1.5.1-cp310-abi3-win_amd64.whl"
    if not os.path.exists(whl_path):
        print("Downloading deltalake...")
        urllib.request.urlretrieve(url, whl_path)
    
    print("Installing deltalake...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", whl_path])
    
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Success")

if __name__ == "__main__":
    download_and_install()
