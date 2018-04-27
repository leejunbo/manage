# coding:utf8
import math
import os
import shutil
import re
import mysql.connector as mc
from flask import Flask, request, g, session, redirect, url_for, abort, \
    render_template, flash, json, jsonify
import del_line
import add_file

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    con = mc.connect(host='192.168.28.130', user='root', passwd='pku2025', db='manage', port='3306')
    return con


app.config.update(dict(
    SECRET_KEY='development key',
))


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT account,psw FROM register ")
        cur = cursor.fetchall()
        for c in cur:
            sqlstr = "".join(c)
            poststr = request.form['username'] + request.form['password']
            if sqlstr != poststr:
                session.setdefault("login_error", "用户名或密码错误")
        # if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            else:
                session.setdefault("logged_in", True)
                session.pop("login_error", None)
                # return redirect(url_for('show_entries'))
                return render_template('index.html')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    # return redirect(url_for('show_entries'))
    return render_template("index.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        r = [request.form['account'], request.form['psw'], request.form['repsw'], request.form['phone'],
             request.form['email'], request.form['nickname'], request.form['realname'], request.form['address'],
             request.form['idcardnumber'], request.form['sex'], request.form['clause']]
        """r = [request.form['username'], request.form['psw'], request.form['repsw'], request.form['email'],
             request.form['mobile']]"""
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO register (account, psw, repsw, phone,email, nickname, "
                "realname,address,idcardnumber, sex, clause) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]))
            """cursor.execute(
                "INSERT INTO register2 (username, psw, repsw, email, mobile) VALUES (%s,%s,%s,%s,%s)",
                (r[0], r[1], r[2], r[3], r[4])
            )"""
            db.commit()
            flash('注册成功')
        except ImportError:
            db.rollback()
            flash('注册失败')
            return render_template("register.html")
    return render_template("register.html")


@app.route('/website')
def show_website():
    return render_template('website.html')


@app.route('/domain')
def show_entries():
    data = page()
    return render_template('domain.html', datas=data)


def page():
    datas = limit_start()
    limitstart = datas['limit_start']
    p = datas['p']
    show_shouye_status = datas['show_shouye_status']
    db = get_db()
    cursor = db.cursor()
    # sql = "select id,host,ip from ipmanages order by id ASC limit {0},10".format(limitstart)
    sql = "SELECT id,host,ip FROM winipmanages "
    cursor.execute(sql)
    cur = cursor.fetchall()
    show_entry = [dict(id=row[0], host=row[1], ip=row[2]) for row in cur]
    total = totalnum()
    dic = get_page(total, p)
    datas = {
        'show_entries': show_entry,
        'p': int(p),
        'total': total,
        'show_shouye_status': show_shouye_status,
        'dic_list': dic
    }
    db.commit()
    return datas


def totalnum():
    db = get_db()
    cursor = db.cursor()
    sql = "SELECT count(*) FROM winipmanages"
    cursor.execute(sql)
    countdata = cursor.fetchone()
    count = countdata[0]  # 总记录
    total = int(math.ceil(count / 10.0))  # 总页数
    return total


def limit_start():
    p = request.args.get("p", '')  # 页数
    show_shouye_status = 0  # 显示首页状态
    if p == '':
        p = 1
    else:
        p = int(p)
        if p > 1:
            show_shouye_status = 1
    limitstart = (int(p) - 1) * 10  # 起始
    datas = {
        'p': p,
        'show_shouye_status': show_shouye_status,
        'limit_start': limitstart
    }
    return datas


def get_page(total, p):
    show_page = 10  # 显示的页码数
    page_offset = 2  # 偏移量
    start = 1  # 分页条开始
    end = total  # 分页条结束

    if total > show_page:
        if p > page_offset:
            start = p - page_offset
            if total > p + page_offset:
                end = p + page_offset
            else:
                end = total
        else:
            start = 1
            if total > show_page:
                end = show_page
            else:
                end = total
        if p + page_offset > total:
            start = start - (p + page_offset - end)
    # 用于模版中循环
    dic = range(start, end + 1)
    return dic


@app.route('/addip', methods=['POST'])
def addip():
    if not session.get('logged_in'):
        abort(401)
    r = [request.form['host'], request.form['ip']]
    pattern = re.compile(
        '(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.'
        '(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)')
    p = pattern.search(r[1])
    if p is None:
        flash('IP格式不匹配')
        return redirect(url_for('show_entries'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT host,ip FROM winipmanages")
    cur = cursor.fetchall()
    for i in range(len(cur)):
        if cur[i][0] == r[0]:
            flash('域名已存在')
            return redirect(url_for('show_entries'))
    add_file.add_host_file(r[0], r[1])
    cursor.execute('INSERT INTO winipmanages (host,ip) VALUES (%s,%s)', (r[0], r[1]))
    db.commit()
    flash('添加成功')
    return redirect(url_for('show_entries'))


@app.route('/search/<args>')
def search(args):
    datas = limit_start()
    p = datas['p']
    show_shouye_status = ['show_shouye_status']
    limitstart = datas['limit_start']
    db = get_db()
    cursor = db.cursor()
    try:
        sql = "select host,ip from winipmanages order by " + args + " ASC limit {0},10".format(limitstart)
        cursor.execute(sql)
        cur = cursor.fetchall()
        search1 = [dict(host=row[1], ip=row[2]) for row in cur]
        total = totalnum()
        dic = get_page(total, p)
        datas = {
            'search': search1,
            'p': int(p),
            'total': total,
            'show_shouye_status': show_shouye_status,
            'dic_list': dic
        }
        db.commit()
    except ImportError:
        db.rollback()
    return render_template('example/search.html')


@app.route('/delete', methods=['POST'])
def delete():
    if not session.get('logged_in'):
        abort(401)
    data = request.get_data()
    data = strtojson(data)
    del_id = data['del_id']
    db = get_db()
    cursor = db.cursor()
    sql = "SELECT host,ip FROM winipmanages WHERE id=" + del_id
    try:
        cursor.execute(sql)
        cur = cursor.fetchone()
        host = cur[0]
        ip = cur[1]
        ip_host = ip + "   " + host
        del_file(host)
        del_line.del_line(ip_host)
        sql = "DELETE FROM winipmanages WHERE id=" + del_id
        cursor.execute(sql)
        flash('删除成功')
        db.commit()
    except ImportError:
        db.rollback()
    return jsonify(data)


@app.route('/save', methods=['POST'])
def save():
    if not session.get('logged_in'):
        abort(401)
    data = request.get_data()
    data = strtojson(data)
    _id_ = data["id"]
    host = data["host"]
    ip = data["ip"]
    db = get_db()
    cursor = db.cursor()
    pattern = re.compile(
        '(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.'
        '(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)')
    p = pattern.search(ip)
    if p is None:
        flash('IP格式不匹配')
        return redirect(url_for('edit'))
    sql = "SELECT host,ip FROM winipmanages WHERE id=" + _id_
    try:
        cursor.execute(sql)
        cur = cursor.fetchone()
        host_old = cur[0]
        ip_old = cur[1]
        del_line.del_line(ip_old)  # 删除旧的ip
        del_file(host_old)  # 删除旧的host
        add_file.add_host_file(host, ip)  # 添加新host文件，ip信息
        sql = "UPDATE winipmanages SET host='" + host + "',ip='" + ip + "' WHERE id=" + id
        cursor.execute(sql)
        db.commit()
        flash('修改成功')
    except ImportError:
        db.rollback()
    return jsonify(data)


def strtojson(jsonstr):
    jsondict = json.loads(jsonstr, encoding="utf-8")
    return jsondict


def del_file(cur):
    file = "F:/software/python/win/nginx-1.12.2/conf/conf.d/" + cur + ".conf"
    os.remove(file)


def del_file_dir():
    delDir = "F:/software/python/win/nginx-1.12.2/conf/conf.d/"
    delList = os.listdir(delDir)

    for f in delList:
        filePath = os.path.join(delDir, f)
        if os.path.isfile(filePath):
            os.remove(filePath)
            print(filePath + "was removed！")
        elif os.path.isdir(filePath):
            shutil.rmtree(filePath, True)
            print("Directory:" + filePath + "was removed！")


if __name__ == '__main__':
    app.run(port=8000)
