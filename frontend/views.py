# -*- coding: utf-8 -*- 
from flask import render_template, request, redirect, url_for, g
from urllib2 import urlopen, HTTPError
from urllib import quote, urlencode
import json
from frontend import frontend
from pymongo import MongoClient
from pymongo.son_manipulator import AutoReference, NamespaceInjector

DB_HOST = 'localhost'
DB_NAME = 'book_manager'
DB_USERNAME = 'admin'
DB_PASSWORD = 'admin'
DB_PORT = '27017'

@frontend.before_request
def before_request():
    client = MongoClient(DB_HOST, int(DB_PORT))
    db = client[DB_NAME]
    # 自动解引用
    db.add_son_manipulator(NamespaceInjector())
    db.add_son_manipulator(AutoReference(db))
    # 设置全局代理
    g.client = client
    g.db = db
    

@frontend.teardown_request
def teardown_request(exception):
    # 删除全局代理
    del g.db
    g.client.close()
    del g.client
    
@frontend.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        q = request.form['q'].encode('utf-8')
        data = {'q': q, 'tag': '', 'start': 0, 'count': 5}
        url = 'https://api.douban.com/v2/book/search' + '?' + urlencode(data)
        try: 
            u = urlopen(url)
        except HTTPError, e:
            print e
            if e.code == 400:
                return '400 Bad Request'
            elif e.code == 404:
                return '404 Not Found'
            else:
                return 'Unkown Error'
        else:
            result_json = u.read()
            u.close()
        
            result_dict = json.loads(result_json)
            if result_dict['total'] > 0:
                # 将书籍信息存入数据库
                books = result_dict['books']
                for book in books:
                    # 优先检测 ISBN-13 编号，其次是 ISBN-10
                    if 'isbn13' in book:
                        g.db.book.update({'isbn13': book['isbn13']}, book, upsert=True)
                    elif 'isbn10' in book:
                        g.db.book.update({'isbn10': book['isbn10']}, book, upsert=True)
                    else:
                        raise
                return redirect(url)
            else:
                return redirect(url_for('.search'))
    elif request.method == 'GET':
        return render_template('search.html')