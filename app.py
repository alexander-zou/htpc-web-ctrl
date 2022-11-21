#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''

@File   : test.py   
@Author : alexander.here@gmail.com
@Date   : 2021-04-01 11:15 CST(+0800)   
@Brief  :  

'''

import os, threading, time, hashlib, webbrowser
from flask import Flask
from flask import request
from flask import make_response, render_template, redirect, abort, send_from_directory
import pyautogui, pyperclip

PASS = '123'
EXPIRATION_SEC = 60 * 60 * 24 * 30
UPLOAD_FOLDER = 'shelf'
DEFAULT_BROWSER = 'chrome'

INVALID_FILENAMES = {
    '', 'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}
pyautogui.FAILSAFE = False

def hibernate( delay=0):
    if delay > 0:
        time.sleep( delay)
    # print( 'Hibernate!')
    os.system(r'rundll32.exe powrprof.dll,SetSuspendState Hibernate')

def power_off( delay=0):
    # hibernate( delay)
    if delay > 0:
        time.sleep( delay)
    os.system( 'shutdown -s -t 0')
    print( 'Power Off!')

def open_browser( browser=None):
    if browser is None:
        browser = DEFAULT_BROWSER
    os.startfile( browser)

def open_page( url, browser=None):
    if browser == 'chrome':
        webbrowser.get( 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s').open_new( url)
    elif browser == 'firefox':
        webbrowser.get( 'C:/Program Files/Mozilla Firefox/firefox.exe %s').open_new( url)
    elif browser == 'edge':
        webbrowser.get( 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe %s').open_new( url)
    else:
        webbrowser.open_new( url)

FIXED_BUTTONS = [ "⦿", "ESC", "空格", "Enter", "⇦", "⇨", "⇧", "⇩", "🔊+", "🔉-"]
FIXED_BUTTON_FUNCTIONS = [
    power_off,
    'esc',
    'space',
    'enter',
    'left',
    'right',
    'up',
    'down',
    'volumeup',
    'volumedown',
]
GRID_BUTTONS = [ "⏮", "⏯", "⏭︎", 'PgUp', 'PgDn', "音响", "切换", "关闭", "桌面", "开始", "浏览器", "刷新", "关标签", "菜单", "最大化"]
GRID_BUTTON_FUNCTIONS = [
    'prevtrack',
    'playpause',
    'prevtrack',
    'pageup',
    'pagedown',
    'volumemute',
    ( 'ctrl', 'alt', 'tab'),
    ( 'alt', 'f4'),
    ( 'win', 'd'),
    ( 'ctrl', 'esc'),
    open_browser,
    'browserrefresh',
    ( 'ctrl', 'w'),
    'apps',
    ( 'win', 'up'),
]

is_mouse_down = False

app = Flask(__name__)
app.config[ 'UPLOAD_FOLDER'] = UPLOAD_FOLDER

def readable_size( bytes):
    if bytes < 1024:
        return str( bytes) + 'Bytes'
    kb = bytes / 1024.0
    if kb < 1024:
        return '%.2fKB' % ( kb)
    mb = kb / 1024.0
    if mb < 1024:
        return '%.2fMB' % ( mb)
    gb = mb / 1024.0
    if gb < 1024:
        return '%.2fGB' % ( gb)
    tb = gb / 1024.0
    if tb < 1024:
        return '%.2fTB' % ( tb)
    pb = tb / 1024.0
    return '%.2fPB' % ( pb)

def generate_token( ip, ts):
    md5 = hashlib.md5()
    md5.update( ip.encode('utf-8'))
    md5.update( str( ts).encode('utf-8'))
    md5.update( PASS.encode('utf-8'))
    return md5.hexdigest()

def is_login():
    try:
        ip = request.remote_addr
        ts = request.cookies.get( 'ts')
        timepast = int( time.time()) - int( ts)
        if timepast < 0 or timepast > EXPIRATION_SEC:
            return False, dict()
        token = request.cookies.get( 'token')
        if generate_token( ip, ts) == token:
            return True, dict()
    except:
        pass
    if 'ps' in request.values and request.values[ 'ps'] == PASS:
        ts = int( time.time())
        token = generate_token( request.remote_addr, ts)
        return True, { 'ts': str( ts), 'token': token}
    return False, dict()
    
@app.route( '/')
def homepage():
    logged, update_cookies = is_login()
    if not logged:
        return redirect( '/login?url=/')
    page = make_response( render_template( 'index.html',
                                        grid_btn_text=GRID_BUTTONS,
                                        fixed_btn_text=FIXED_BUTTONS))
    for k, v in update_cookies.items():
        page.set_cookie( k, v)
    return page

@app.route( '/shelf')
def shelf():
    logged, update_cookies = is_login()
    if not logged:
        return redirect( '/login?url=/shelf')
    os.makedirs( UPLOAD_FOLDER, exist_ok=True)
    files = []
    for name in os.listdir( UPLOAD_FOLDER):
        path = os.path.join( UPLOAD_FOLDER, name)
        if os.path.isfile( path):
            files.append( ( name, readable_size( os.path.getsize( path))))
    return render_template( 'shelf.html', files=files)

@app.route( '/text', methods=['POST','GET'])
def text():
    if request.method == 'POST':
        cmd = request.values[ 'cmd']
        txt = request.values[ 'txt']
        if 'get' == cmd:
            return pyperclip.paste()
        elif 'send' == cmd:
            pyperclip.copy( txt)
        elif 'url' == cmd:
            os.startfile( txt)
        elif cmd in ( 'chrome', 'firefox', 'edge'):
            open_page( txt, cmd)
        return 'OK'
    else:
        logged, update_cookies = is_login()
        if not logged:
            return redirect( '/login?url=/text')
        return render_template( 'text.html')

@app.route( '/input')
def input():
    logged, update_cookies = is_login()
    if not logged:
        return redirect( '/login?url=/input')
    return render_template( 'input.html')

@app.route( '/api', methods=['POST','GET'])
def api():
    global is_mouse_down
    logged, update_cookies = is_login()
    if not logged:
        abort( 401, 'Must login first')
    if request.values[ 'evt'] == 'click':
        if is_mouse_down:
            pyautogui.mouseUp()
            is_mouse_down = False
        else:
            pyautogui.click()
    elif request.values[ 'evt'] == 'dbclick':
        pyautogui.rightClick()
    elif request.values[ 'evt'] == 'drag':
        if is_mouse_down:
            pyautogui.mouseUp()
            is_mouse_down = False
        else:
            pyautogui.mouseDown()
            is_mouse_down = True
    elif request.values[ 'evt'] == 'move':
        x, y = float( request.values[ 'x']), float( request.values[ 'y'])
        l2 = x**2 + y**2
        k = l2/20000.0 + 1.05
        pyautogui.moveRel( x*k, y*k, 0.02)
    elif request.values[ 'evt'] == 'scroll':
        x, y = float( request.values[ 'x']), float( request.values[ 'y'])
        pyautogui.scroll( int(0.5+y))
        pyautogui.hscroll( int(0.5+x))
    elif request.values[ 'evt'] == 'key':
        # print( 'KEY: ', request.values[ 'keys'].split( '|'))
        pyautogui.hotkey( *tuple( request.values[ 'keys'].split( '|')))
    return 'OK'

@app.route( '/button', methods=['POST','GET'])
def button():
    logged, update_cookies = is_login()
    if not logged:
        abort( 401, 'Must login first')
    id = int( request.values[ 'id'])
    if request.values[ 't'] == 'fixed':
        func = FIXED_BUTTON_FUNCTIONS[ id]
    elif request.values[ 't'] == 'grid':
        func = GRID_BUTTON_FUNCTIONS[ id]
    else:
        abort( 400, 'Wrong arguments')
    if type( func) is str:
        pyautogui.press( func)
    elif type( func) is tuple:
        pyautogui.hotkey( *func)
    elif callable( func):
        func()
    return 'OK'

@app.route( '/download/<string:name>')
def download( name):
    logged, update_cookies = is_login()
    if not logged:
        abort( 401, 'Must login first')
    return send_from_directory( 'shelf', name)

@app.route( '/file/<string:op>/<string:file>', methods=['POST','GET'])
def file_op( op, file):
    logged, update_cookies = is_login()
    if not logged:
        abort( 401, 'Must login first')
    path = os.path.join( UPLOAD_FOLDER, file)
    if not os.path.exists( path):
        abort( 404)
    if 'open' == op:
        os.startfile( path)
    elif 'delete' == op:
        os.remove( path)
    return 'OK'

@app.route( '/upload', methods=['POST'])
def upload():
    logged, update_cookies = is_login()
    if not logged:
        abort( 401, 'Must login first')
    if 'file' not in request.files:
        abort( 400, 'Missing file')
    uploaded = request.files[ 'file']
    if uploaded.filename == '':
        abort( 400, 'Missing Filename')
    if uploaded:
        filename = ''.join( filter( lambda x:x not in '<>:"/\|?*', uploaded.filename))
        if filename.upper() in INVALID_FILENAMES:
            abort( 400, 'Invalid filename')
        path = os.path.join( UPLOAD_FOLDER, filename)
        if os.path.exists( path):
            abort( 400, 'Already Exists')
        os.makedirs( UPLOAD_FOLDER, exist_ok=True)
        uploaded.save( path)
        return redirect( '/shelf')
    abort( 400, 'Missing data')

@app.route( '/screen')
def screen():
    logged, update_cookies = is_login()
    if not logged:
        return redirect( '/login?url=/screen')
    return render_template( 'screen.html', timestamp=int(time.time()))

@app.route( '/screenshot.jpg')
def screenshot_png():
    logged, update_cookies = is_login()
    if not logged:
        abort( 401, 'Must login first')
    pyautogui.screenshot( os.path.join( 'statics', 'screenshot.jpg'))
    return send_from_directory( 'statics', 'screenshot.jpg')

@app.route( '/login', methods=['POST','GET'])
def login():
    if request.method == 'POST' and 'pass' in request.values:
        if request.values[ 'pass'] == PASS:
            #success:
            ts = int( time.time())
            token = generate_token( request.remote_addr, ts)
            if 'url' in request.args:
                url = request.args[ 'url']
            else:
                url = '/'
            resp = redirect( url)
            resp.set_cookie( 'ts', str( ts))
            resp.set_cookie( 'token', token)
            return resp
        else:
            time.sleep( 1)
    if 'url' in request.args:
        url = request.args[ 'url']
    else:
        url = '/'
    return render_template( 'login.html', url=url)

@app.route( '/shutdown', methods=[ 'POST'])
def shutdown():
    logged, update_cookies = is_login()
    if not logged:
        abort( 401, 'Must login first')
    threading.Thread( target=power_off, args=(1,)).start()
    return 'Bye'

@app.route( '/favicon.ico')
def icon():
    return send_from_directory( 'statics', 'favicon.ico')


if __name__ == '__main__':
    abspath = os.path.abspath( __file__)
    dname = os.path.dirname( abspath)
    os.chdir( dname)
    app.run( host='0.0.0.0', port=5000)

# End of 'test.py' 

