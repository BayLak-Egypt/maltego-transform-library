import os
import re
import requests

def fetch_data(url, session=None, **kwargs):
    if session is None:
        session = requests.Session()
    to = kwargs.get('timeout', 20)
    web_url = url.replace('api.github.com/repos', 'github.com').replace('/contents/', '/tree/main/')
    try:
        res = session.get(web_url, timeout=to, verify=False)
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
                lib_res = session.get(f'{web_url}/{name}', timeout=5, verify=False)
                img_match = re.search(f'/{user}/{repo}/blob/main/[^"]+/{name}/([^"]+\\.(?:png|jpg|jpeg|ico))', lib_res.text, re.IGNORECASE)
                if img_match:
                    icon_url = f'{raw_base}/{name}/{img_match.group(1)}'.replace('//', '/').replace('https:/', 'https://')
            except:
                pass
            results.append((name, f'GitHub @{user}', icon_url))
        return results
    except Exception as e:
        print(f'Driver Fetch Error: {e}')
        return []

def install_lib(name, base_url, target_path, progress_callback=None, session=None, **kwargs):
    if session is None:
        session = requests.Session()
    to = kwargs.get('timeout', 30)
    try:
        web_folder = base_url.replace('api.github.com/repos', 'github.com').replace('/contents/', '/tree/main/') + f'/{name}'
        raw_folder = base_url.replace('api.github.com/repos', 'raw.githubusercontent.com').replace('/contents/', '/main/') + f'/{name}'
        res = session.get(web_folder, timeout=to, verify=False)
        parts = web_folder.split('github.com/')[1].split('/')
        user, repo = (parts[0], parts[1])
        file_pattern = f'href="/{user}/{repo}/blob/main/[^"]+/({name}/[^"/? ]+)"'
        files_paths = list(set(re.findall(file_pattern, res.text)))
        if not files_paths:
            files_paths = list(set(re.findall(f'/{user}/{repo}/blob/main/[^"]+/([^" ]+\\.[a-z0-9]+)"', res.text)))
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        total_files = len(files_paths)
        if total_files == 0:
            return False
        for index, f_path in enumerate(files_paths):
            f_name = os.path.basename(f_path)
            download_url = f'{raw_folder}/{f_name}'.replace('//', '/').replace('https:/', 'https://')
            file_share = 100 / total_files
            base_percent = index * file_share
            with session.get(download_url, stream=True, timeout=to, verify=False) as f_res:
                f_res.raise_for_status()
                total_length = int(f_res.headers.get('content-length', 0))
                with open(os.path.join(target_path, f_name), 'wb') as f:
                    downloaded = 0
                    for chunk in f_res.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total_length > 0:
                                prog = int(base_percent + downloaded / total_length * file_share)
                                progress_callback(min(prog, 100))
            if progress_callback:
                progress_callback(int((index + 1) * file_share))
        return True
    except Exception as e:
        print(f'Driver Install Error: {e}')
        return False