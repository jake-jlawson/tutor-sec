"""
    UI TEST ENTRY POINT (for UI debugging)
    Run this file to view the UI in debug mode without backend
"""
# IMPORTS ---------------
from flask import Flask, render_template, request, jsonify
import webbrowser, threading, os, signal, sys


# APP CONFIG
app = Flask(__name__)
PORT = 5000



# Main route
@app.route('/')
def index():
    return render_template('jobs.html')

# Shutdown route
@app.route('/shutdown', methods=['POST'])
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
    app.run(debug=True, port=PORT)

    #close browser when the server shuts down
    os.system("taskkill /IM msedge.exe /F")