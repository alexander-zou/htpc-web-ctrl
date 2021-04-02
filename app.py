#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

'''

@File   : test.py   
@Author : jiachen.zou@jiiov.com   
@Date   : 2021-04-01 11:15 CST(+0800)   
@Brief  :  

'''

import os
from flask import Flask
from flask import request
from flask import session
from flask import render_template, redirect, abort, send_from_directory

UPLOAD_FOLDER = 'shelf'
INVALID_FILENAMES = {
    '', 'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}

app = Flask(__name__)
app.config[ 'UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route( '/')
def homepage():
    return render_template( 'index.html')

@app.route( '/shelf')
def shelf():
    os.makedirs( UPLOAD_FOLDER, exist_ok=True)
    return render_template( 'shelf.html', files=os.listdir( UPLOAD_FOLDER))

@app.route( '/download/<string:name>')
def download( name):
    return send_from_directory( 'shelf', name)

@app.route( '/upload', methods=['POST'])
def upload():
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

if __name__ == '__main__':
    abspath = os.path.abspath( __file__)
    dname = os.path.dirname( abspath)
    os.chdir( dname)
    app.run( host='0.0.0.0', port=5000)

# End of 'test.py' 

