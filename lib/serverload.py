import os
import importlib.util
import requests
import urllib3
import json
from lib.proxy import proxy_mgr
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ServerEngine:

    def __init__(self, servers_dir='servers'):
        self.drivers = {}
        self.servers_dir = servers_dir
        self.load_drivers()

    def load_drivers(self):
        if not os.path.exists(self.servers_dir):
            os.makedirs(self.servers_dir)
        for file in os.listdir(self.servers_dir):
            if file.endswith('.py'):
                name = file[:-3]
                try:
                    file_path = os.path.join(self.servers_dir, file)
                    spec = importlib.util.spec_from_file_location(name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.drivers[name] = module
                    print(f'✅ Driver Loaded: {name}')
                except Exception as e:
                    print(f'❌ Failed to load driver {name}: {e}')

    def fetch_data(self, driver_name, url):
        driver = self.drivers.get(driver_name)
        if driver and hasattr(driver, 'fetch_data'):
            try:
                current_session = proxy_mgr.get_session()
                to = getattr(current_session, 'timeout', 20)
                return driver.fetch_data(url, session=current_session, timeout=to)
            except Exception as e:
                print(f'Engine Fetch Error: {e}')
        return []

    def install_data(self, driver_name, lib_name, url, save_path, callback=None):
        driver = self.drivers.get(driver_name)
        method_to_call = None
        if hasattr(driver, 'install_data'):
            method_to_call = driver.install_data
        elif hasattr(driver, 'install_lib'):
            method_to_call = driver.install_lib
        if driver and method_to_call:
            try:
                current_session = proxy_mgr.get_session()
                return method_to_call(lib_name, url, save_path, session=current_session, progress_callback=callback)
            except Exception as e:
                print(f'Engine Install Error: {e}')
        else:
            print(f"⚠️ Driver '{driver_name}' has no installation method.")
        return False

class LinkManager:

    def __init__(self, filename='links.txt'):
        self.filename = filename

    def load_all_servers(self):
        servers = {}
        if not os.path.exists(self.filename):
            return servers
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#') or '|' not in line:
                        continue
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 3:
                        title, driver, url = (parts[0], parts[1], parts[2])
                        servers[title] = {'driver': driver, 'url': url, 'id': line_num}
        except Exception as e:
            print(f'❌ Error reading links: {e}')
        return servers

    def filter_targets(self, all_servers, selection):
        if not all_servers:
            return []
        sel = str(selection).strip().upper()
        if sel in ['ALL SERVERS', 'الكل']:
            return list(all_servers.items())
        return [(t, d) for t, d in all_servers.items() if t.strip().upper() == sel]