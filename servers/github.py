import requests
import os
import re

def fetch_data(url):
    web_url = url.replace('api.github.com/repos', 'github.com').replace('/contents/', '/tree/main/')
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(web_url, headers=headers, timeout=10)
        if res.status_code != 200:
            return []
        parts = web_url.split('github.com/')[1].split('/')
        user, repo = (parts[0], parts[1])
        path_in_repo = '/'.join(parts[4:]) if len(parts) > 4 else ''
        pattern = f'href="/{user}/{repo}/tree/main/{path_in_repo}/?([^"/]+)"'
        lib_names = list(set(re.findall(pattern, res.text)))
        results = []
        raw_base = f'https://raw.githubusercontent.com/{user}/{repo}/main/{path_in_repo}'
        for name in lib_names:
            if name in ['.github', 'docs', 'README.md', 'assets'] or '.' in name:
                continue
            icon_url = None
            try:
                lib_res = requests.get(f'{web_url}/{name}', headers=headers, timeout=5)
                img_match = re.search(f'/{user}/{repo}/blob/main/{path_in_repo}/{name}/([^"]+\\.(?:png|jpg|jpeg|ico))', lib_res.text, re.IGNORECASE)
                if img_match:
                    icon_url = f'{raw_base}/{name}/{img_match.group(1)}'.replace('//', '/').replace('https:/', 'https://')
            except:
                pass
            results.append((name, f'GitHub @{user}', icon_url))
        return results
    except:
        return []

def install_data(name, base_url, target_path):
    try:
        web_folder = base_url.replace('api.github.com/repos', 'github.com').replace('/contents/', f'/tree/main/') + f'/{name}'
        raw_folder = base_url.replace('api.github.com/repos', 'raw.githubusercontent.com').replace('/contents/', f'/main/') + f'/{name}'
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(web_folder, headers=headers, timeout=10)
        parts = web_folder.split('github.com/')[1].split('/')
        user, repo = (parts[0], parts[1])
        file_pattern = f'href="/{user}/{repo}/blob/main/[^"]+/({name}/[^"/? ]+)"'
        files_paths = list(set(re.findall(file_pattern, res.text)))
        if not files_paths:
            files_paths = list(set(re.findall(f'/{user}/{repo}/blob/main/[^"]+/([^" ]+\\.[a-z0-9]+)"', res.text)))
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        for f_path in files_paths:
            f_name = os.path.basename(f_path)
            download_url = f'{raw_folder}/{f_name}'.replace('//', '/').replace('https:/', 'https://')
            f_res = requests.get(download_url, timeout=15)
            if f_res.status_code == 200:
                with open(os.path.join(target_path, f_name), 'wb') as f:
                    f.write(f_res.content)
                print(f'[+] Downloaded: {f_name}')
        return True
    except Exception as e:
        print(f'[-] Install Error: {e}')
        return False