import os
import threading
import shutil
from tkinter import messagebox

class ReloadManager:

    @staticmethod
    def run_async(target, args=()):
        thread = threading.Thread(target=target, args=args, daemon=True)
        thread.start()
        return thread

    @staticmethod
    def get_local_libs(lib_dir):
        if not os.path.exists(lib_dir):
            os.makedirs(lib_dir)
        return [(d, 'Ready') for d in os.listdir(lib_dir) if os.path.isdir(os.path.join(lib_dir, d))]

    @staticmethod
    def safe_uninstall(lib_dir, name, callback):
        try:
            path = os.path.join(lib_dir, name)
            if os.path.exists(path):
                shutil.rmtree(path)
            callback(True, None)
        except Exception as e:
            callback(False, str(e))

    @staticmethod
    def fetch_cloud_data(engine, servers_dict, selected_server, local_dir):
        all_cloud = []
        lib_sources = {}
        targets = servers_dict.items() if selected_server == 'ALL SERVERS' else [(selected_server, servers_dict.get(selected_server))] if selected_server in servers_dict else []
        for title, data in targets:
            if not data:
                continue
            d_name, url = data
            if d_name in engine.drivers:
                try:
                    libs = engine.drivers[d_name].fetch_data(url)
                    for item in libs:
                        all_cloud.append(item)
                        lib_sources[item[0]] = (d_name, url)
                except:
                    continue
        local_set = set([d for d in os.listdir(local_dir) if os.path.isdir(os.path.join(local_dir, d))]) if os.path.exists(local_dir) else set()
        final_list = [x for x in all_cloud if x[0] not in local_set]
        return (final_list, lib_sources)