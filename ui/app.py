"""
    UI ENTRY POINT
    Run this file to start the UI version of TutorSec
"""
# IMPORTS ---------------
from flask import Flask, render_template, request, jsonify
import webbrowser, threading, os, signal

# APP CONFIG
APP = Flask(__name__)
PORT = 5000


# PRIMARY ROUTES ---------------
# Main route
@APP.route('/')
def index():
    return render_template('index.html')

# Shutdown route
@APP.route('/shutdown', methods=['POST'])
def shutdown():
    print("Shutting down the server...")
    os.kill(os.getpid(), signal.SIGINT)
    return '', 204  # No content response



# Open the UI in a new tab
def open_ui():
    # register edge as the browser to use
    webbrowser.register('edge', None, webbrowser.BackgroundBrowser("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"))

    # open the ui in a new tab
    webbrowser.get('edge').open_new_tab(f'http://localhost:{PORT}')



# MAIN ---------------
if __name__ == '__main__':
    threading.Timer(1, open_ui).start()
    APP.run(debug=False, port=PORT)

    #close browser when the server shuts down
    os.system("taskkill /IM msedge.exe /F")