# Maltego Data Leak Transform Library 🛡️

A lightweight, user-friendly library designed to integrate and support various data leak tools directly within **Maltego**. This project provides a flexible framework for managing transforms and fetching data from multiple remote and local sources.

## 🚀 Key Features

* **Multi-Source Support:** Seamlessly integrate libraries from GitHub, local servers, or via TCP/UDP protocols.
* **Modular Architecture:** Easily add your own custom libraries into the `library/` directory.
* **Dynamic Server Management:** Customize and add specific data-receiving protocols.
* **Unified Configuration:** Manage all settings, including servers, themes, languages, and proxies, from a single JSON file.
* **Lightweight & Fast:** Built for efficiency with minimal overhead.

---

## 📁 Project Structure

### 1. `library/` Folder
This is the core directory for libraries downloaded directly from the web. It is designed for extensibility—you can create and drop your own libraries inside this folder, and they will be recognized by the system.

### 2. `Maltego Transform library/lib/`
Contains the essential system libraries required to run the program. 
> **Note:** These are internal software libraries and are distinct from the data leak transform modules. They can be modified to customize the core behavior of the application.

### 3. `Maltego Transform library/servers/`
This directory hosts the protocols and specific server configurations used to receive data. You can customize server types here, including:
* Local Servers
* GitHub Repositories
* TCP Online / UDP Streams

---

## ⚙️ Configuration (`settings.json`)
All application states are persisted in `settings.json`. This includes:
* **Server Lists:** Manage which servers the app pulls data from.
* **Localization & UI:** Current language and theme preferences.
* **Proxy Settings:** Currently supports **HTTP/S** web servers. 
    * *Known Issue:* Non-web protocols may experience connectivity issues through the proxy in the current version.

---

## 🛠️ Roadmap (Upcoming Features)

We are actively working on expanding the library's capabilities:
* **Encrypted Libraries:** Support for adding and utilizing encrypted modules for enhanced security.
* **User Accounts:** A built-in account system to upload your own libraries to the cloud.
* **Community Interaction:** Ability to write comments and reviews for specific libraries and their features.

---

## 👨‍💻 Contribution
If you would like to improve the proxy support or add new server protocols, feel free to explore the `servers/` or `lib/` directories. Pull requests and feedback are always welcome!
