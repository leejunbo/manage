import manage


@manage.app.route('/register')
def register():
    db = manage.get_db()
    cursor = db.cursor()
    sql = "INSERT INTO register (account,psw,repsw,phone,email) VALUES (%s,%s,%s,%s,%s)",
    cursor.execute(sql)
    return manage.render_template("register.html")
