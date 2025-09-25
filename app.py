#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/9/6 19:04
# @Author  : caijian
# @File    : app.py
# @Software: PyCharm
# app.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)