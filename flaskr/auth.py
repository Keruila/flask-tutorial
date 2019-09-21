#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
@author: Keruila
@time: 2019/09/19
@file: auth.py
"""
import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register/', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = '用户名必填'
        elif not password:
            error = '密码必填'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            # fetchone() 根据查询返回一个记录行。 如果查询没有结果，则返回 None 。
            # 后面还用到 fetchall() ，它返回包括所有结果的列表。
            error = '用户 “{}” 已被注册'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()  # 将用户名和加密后的密码保存到数据库中
            return redirect(url_for('auth.login'))  # 重定向到登录页面

        flash(error)  # 用于储存在渲染模块时可以调用的信息。
        # Flashes a message to the next request.
        # In order to remove the flashed message from the session and to display it to the user,
        # the template has to call :func:`get_flashed_messages`.
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None
        if not username:
            error = '用户名必填'
        elif not password:
            error = '密码必填'

        if error is None:
            user = db.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()

            if user is None:
                error = '用户不存在'
            elif not check_password_hash(user['password'], password):
                error = '密码错误'

            if error is None:
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('index'))
        flash(error)
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id, )
        ).fetchone()


@bp.route('/logout/')
def logout():
    session.clear()  # 将用户id从session中移除
    return redirect(url_for('index'))


def login_required(view):
    """需要登录装饰器"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
