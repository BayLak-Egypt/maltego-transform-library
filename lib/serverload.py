import os
import importlib.util
import shutil
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ServerEngine:

    def __init__(self, servers_dir='servers'):
        self.servers_dir = servers_dir
        self.drivers = {}
        self.load_drivers()

    def load_drivers(self):
        if not os.path.exists(self.servers_dir):
            os.makedirs(self.servers_dir)
        for file in os.listdir(self.servers_dir):
            if file.endswith('.py'):
                name = file[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(name, os.path.join(self.servers_dir, file))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.drivers[name] = module
                    print(f'[+] Driver Loaded: {name}')
                except Exception as e:
                    print(f'[-] Error loading driver {name}: {e}')

class LinkManager:

    def __init__(self, filename='links.txt'):
        self.filename = filename

    def load_all_servers(self):
        servers = {}
        if not os.path.exists(self.filename):
            print(f'⚠️ Warning: {self.filename} not found. Creating empty file.')
            try:
                with open(self.filename, 'w', encoding='utf-8') as f:
                    pass
            except Exception as e:
                print(f'❌ Error creating file: {e}')
            return servers
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '|' not in line:
                        print(f"Line {line_num}: Invalid format (Missing '|')")
                        continue
                    try:
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 3:
                            title = parts[0]
                            driver = parts[1]
                            url = parts[2]
                            servers[title] = {'driver': driver, 'url': url, 'id': line_num}
                        else:
                            print(f'Line {line_num}: Incomplete data (Needs 3 parts)')
                    except Exception as e:
                        print(f'Line {line_num}: Error parsing - {e}')
                        continue
        except Exception as e:
            print(f'❌ Fatal error reading {self.filename}: {e}')
        return servers

    def filter_targets(self, all_servers, selection):
        if not all_servers:
            return []
        selection_upper = str(selection).strip().upper()
        if selection_upper == 'ALL SERVERS' or selection_upper == 'الكل':
            return list(all_servers.items())
        for title, data in all_servers.items():
            if title.strip().upper() == selection_upper:
                return [(title, data)]
        return []

    def save_link(self, title, driver, url):
        try:
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(f'\n{title} | {driver} | {url}')
            return True
        except Exception as e:
            print(f'❌ Error saving link: {e}')
            return False