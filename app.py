#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''

@File   : test.py   
@Author : alexander.here@gmail.com
@Date   : 2021-04-01 11:15 CST(+0800)   
@Brief  :  

'''

import os, time, hashlib
from flask import Flask
from flask import request
from flask import render_template, redirect, abort, send_from_directory

PASS = '123456'
EXPIRATION_SEC = 30
UPLOAD_FOLDER = 'shelf'
INVALID_FILENAMES = {
    '', 'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}

app = Flask(__name__)
app.config[ 'UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            return False
        token = request.cookies.get( 'token')
        return generate_token( ip, ts) == token
    except:
        return False
    
@app.route( '/')
def homepage():
    if not is_login():
        return redirect( '/login?url=/')
    return render_template( 'index.html')

@app.route( '/shelf')
def shelf():
    if not is_login():
        return redirect( '/login?url=/shelf')
    os.makedirs( UPLOAD_FOLDER, exist_ok=True)
    return render_template( 'shelf.html', files=os.listdir( UPLOAD_FOLDER))

@app.route( '/download/<string:name>')
def download( name):
    if not is_login():
        abort( 401, 'Must login first')
    return send_from_directory( 'shelf', name)

@app.route( '/upload', methods=['POST'])
def upload():
    if not is_login():
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

if __name__ == '__main__':
    abspath = os.path.abspath( __file__)
    dname = os.path.dirname( abspath)
    os.chdir( dname)
    app.run( host='0.0.0.0', port=5000)

# End of 'test.py' 

