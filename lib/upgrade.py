import os
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
        response = session.get(api_url, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            return [f for f in data.get('tree', []) if f['type'] == 'blob']
    except:
        pass
    return []

def sync_file(item):
    path = item['path']
    remote_sha = item['sha']
    raw_url = f'https://raw.githubusercontent.com/{USER}/{REPO}/{BRANCH}/{path}'
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        try:
            with open(path, 'rb') as f:
                content = f.read()
                clean_content = content.replace(b'\r\n', b'\n')
                header = f'blob {len(clean_content)}\x00'.encode('utf-8')
                local_sha = hashlib.sha1(header + clean_content).hexdigest()
            if local_sha == remote_sha:
                return False
        except:
            pass
    try:
        session = proxy_mgr.get_session()
        r = session.get(raw_url, timeout=15, verify=False)
        if r.status_code == 200:
            new_content = r.content.replace(b'\r\n', b'\n')
            with open(path, 'wb') as f:
                f.write(new_content)
            return True
    except:
        pass
    return False