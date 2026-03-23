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
        r = session.get(api_url, timeout=10, verify=False)
        if r.status_code == 200:
            return [f for f in r.json().get('tree', []) if f['type'] == 'blob']
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
                header = f'blob {len(content)}\x00'.encode('utf-8')
                local_sha = hashlib.sha1(header + content).hexdigest()
            if local_sha == remote_sha:
                return False
        except:
            pass
    try:
        session = proxy_mgr.get_session()
        r = session.get(raw_url, timeout=15, verify=False)
        if r.status_code == 200:
            with open(path, 'wb') as f:
                f.write(r.content)
            return True
    except:
        pass
    return False