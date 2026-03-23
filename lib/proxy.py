import json, os, requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class ProxyManager:

    def __init__(self, settings_path='settings.json'):
        self.settings_path = settings_path

    def get_settings(self):
        if not os.path.exists(self.settings_path):
            return {'enabled': False, 'ip': '127.0.0.1', 'port': '9050'}
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('proxy', {'enabled': False, 'ip': '127.0.0.1', 'port': '9050'})
        except:
            return {'enabled': False, 'ip': '127.0.0.1', 'port': '9050'}

    def get_session(self):
        session = requests.Session()
        session.trust_env = False
        settings = self.get_settings()
        if settings.get('enabled'):
            p_url = f'socks5h://{settings.get('ip')}:{settings.get('port')}'
            session.proxies = {'http': p_url, 'https': p_url}
            session.timeout = 15
        else:
            session.proxies = {}
            session.timeout = 20
        adapter = HTTPAdapter(max_retries=Retry(total=2))
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
proxy_mgr = ProxyManager()