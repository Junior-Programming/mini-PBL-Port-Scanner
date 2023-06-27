from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_mysqldb import MySQL, MySQLdb
import bcrypt
import socket

app = Flask(__name__)
app.secret_key = "membuatLOginFlask1"  # bebas

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'the_hell'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/download')
def download_file():
    return send_file("Port Scanner.exe", as_attachment=True)


@app.route('/project', methods=['POST'])
def scanner():

    target = request.form["ip"]
    ports = request.form["port"]
    ports = ports.split(",")
    msg = ""

    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, int(port)))
            if result == 0:
                msg += f"Port {port} terbuka\n"
            else:
                msg += f"Port {port} tertutup\n"
            sock.close()

        except KeyboardInterrupt:
            msg = "Scanning dihentikan"
            break

        except socket.gaierror:
            msg = "Hostname tidak ditemukan. Silahkan cek kembali alamat IP"
            break

        except socket.error:
            msg = "Tidak dapat terhubung ke target"
            break

    return render_template("project.html", ip=target, port=ports, msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = curl.fetchone()
        curl.close()

        if user is not None and len(user) > 0:
            if bcrypt.hashpw(password, user['password'].encode('utf-8')) == user['password'].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
                return redirect(url_for('home'))
            else:
                flash("Gagal, Email dan Password Tidak Cocok")
                return redirect(url_for('login'))
        else:
            flash("Gagal, User Tidak Ditemukan")
            return redirect(url_for('login'))
    else:
        return render_template("login.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)",
                    (name, email, hash_password))
        mysql.connection.commit()
        session['name'] = request.form['name']
        session['email'] = request.form['email']
        return redirect(url_for('home'))


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/portofolio')
def portofolio():
    if 'email' in session:
        return render_template("portofolio.html")
    else:
        return redirect(url_for('home'))


@app.route('/project')
def contact():
    if 'email' in session:
        return render_template("project.html")
    else:
        return redirect(url_for('home'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=8080)
