#!/usr/bin/env python3
import subprocess
import re
import sys

Name = "Sherlock OSINT"
Description = "Realtime URLs from Sherlock scan"
EntityType = "Phrase"

url_regex = re.compile(r"https?://[^\s\"'>]+")

def send_debug(msg):
    """Debug على stderr فقط"""
    sys.stderr.write(f"[DEBUG] {msg}\n")
    sys.stderr.flush()

def run(input_value):
    """
    دالة لإرسال كل رابط فور اكتشافه في Maltego
    """
    username = str(input_value).strip().split(' ')[0]
    send_debug(f"Starting Sherlock scan for {username}")

    results = []
    unique_links = set()

    try:
        process = subprocess.Popen(
            ["sherlock", username, "--timeout", "5", "--print-found", "--no-color"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            line = line.strip()
            if not line:
                continue

            send_debug(line)

            for url in url_regex.findall(line):
                clean_url = url.rstrip(')].,')
                if clean_url not in unique_links:
                    unique_links.add(clean_url)
                    results.append({
                        "value": clean_url,
                        "type": "URL",
                        "properties": {
                            "url": clean_url,
                            "url.source": "Sherlock Scan"
                        }
                    })

    except Exception as e:
        send_debug(f"Error: {str(e)}")
        results.append({
            "value": f"Error: {str(e)}",
            "type": "Phrase"
        })

    return results
