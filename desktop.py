# desktop.py
import webview
import threading
import os
import subprocess
import time

# Function to run Django server
def start_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "retail.settings")
    subprocess.Popen(["python", "manage.py", "runserver"])

# Start the Django server in a separate thread
threading.Thread(target=start_django).start()

# Give the server a few seconds to start
time.sleep(3)

# Open PyWebView
webview.create_window("Retail Management System", "http://127.0.0.1:8000")
webview.start()
