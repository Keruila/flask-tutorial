#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Keruila
@time: 2019/09/16
@file: db.py
"""
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """
    在处理请求的某个时刻，连接被创建。在发送响应 之前连接被关闭。
    g 是一个特殊对象，独立于每一个请求。在处理请求过程中，它可以用于储存 可能多个函数都会用到的数据。
    把连接储存于其中，可以多次使用，而不用在同一个 请求中每次调用 get_db 时都创建一个新的连接。
    :return:g.db
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],  # 连接当前app的数据库
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # 告诉连接返回类似于字典的行，这样可以通过列名称来操作 数据。

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()  # 一个数据库连接对象

    with current_app.open_resource('schema.sql') as f:  # open_resource打开一个文件
        db.executescript(f.read().decode('utf8'))


# 定义一个名为 init-db 命令行，它调用 init_db 函数，并为用户显示一个成功的消息。
@click.command('init-db')
@with_appcontext
def init_db_command():
    """清空已存在的数据并创建新表"""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)  # 告诉 Flask 在返回响应后进行清理的时候调用此函数。
    app.cli.add_command(init_db_command)  # 添加一个新的 可以与 flask 一起工作的命令。
