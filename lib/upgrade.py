import os
import json
import hashlib
import requests
import urllib3
from lib.proxy import proxy_mgr
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
USER = 'BayLak-Egypt'
REPO = 'maltego-transform-library'
BRANCH = 'main'

def get_remote_files():
    api_url = f'https://api.github.com/repos/{USER}/{REPO}/git/trees/{BRANCH}?recursive=1'
    try:
        session = proxy_mgr.get_session()
        response = session.get(api_url, timeout=15, verify=False)
        if response.status_code == 200:
            data = response.json()
            return [f for f in data.get('tree', []) if f['type'] == 'blob']
        else:
            print(f'⚠️ GitHub API Error: {response.status_code}')
    except Exception as e:
        print(f'⚠️ Proxy/Network Error: {e}')
    return []

def sync_file(item):
    path = item['path']
    remote_sha = item['sha']
    raw_url = f'https://raw.githubusercontent.com/{USER}/{REPO}/{BRANCH}/{path}'
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    update_needed = True
    if os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                content = f.read()
                header = f'blob {len(content)}\x00'.encode('utf-8')
                local_sha = hashlib.sha1(header + content).hexdigest()
            if local_sha == remote_sha:
                update_needed = False
        except Exception:
            update_needed = True
    else:
        update_needed = True
    if update_needed:
        try:
            session = proxy_mgr.get_session()
            response = session.get(raw_url, stream=True, verify=False, timeout=20)
            if response.status_code == 200:
                with open(path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True
            else:
                print(f'⚠️ Failed to download {path}. Status code: {response.status_code}')
                return False
        except Exception as e:
            print(f'⚠️ Connection Error while syncing {path}: {e}')
            return False
    return False