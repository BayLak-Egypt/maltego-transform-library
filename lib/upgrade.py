import os
import json
import urllib.request
import hashlib
import sys
USER = 'BayLak-Egypt'
REPO = 'maltego-transform-library'
BRANCH = 'main'

def get_remote_files():
    api_url = f'https://api.github.com/repos/{USER}/{REPO}/git/trees/{BRANCH}?recursive=1'
    try:
        with urllib.request.urlopen(api_url, timeout=5) as r:
            data = json.loads(r.read().decode())
            return [f for f in data.get('tree', []) if f['type'] == 'blob']
    except Exception:
        return []

def sync_file(item):
    path = item['path']
    remote_sha = item['sha']
    raw_url = f'https://raw.githubusercontent.com/{USER}/{REPO}/{BRANCH}/{path}'
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    update_needed = True
    if os.path.exists(path):
        with open(path, 'rb') as f:
            content = f.read()
            header = f'blob {len(content)}\x00'.encode('utf-8')
            local_sha = hashlib.sha1(header + content).hexdigest()
        if local_sha == remote_sha:
            update_needed = False
    if update_needed:
        try:
            urllib.request.urlretrieve(raw_url, path)
            return True
        except:
            return False
    return False

def start_sync():
    files = get_remote_files()
    if not files:
        return False
    any_updated = False
    for f in files:
        if sync_file(f):
            any_updated = True
    return any_updated