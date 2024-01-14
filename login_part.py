from flask import render_template, current_app, redirect, Blueprint
from flask import request, session, url_for, flash
from models import db, Author, Authorization
from werkzeug.utils import secure_filename
import os
import secrets
import string
from flask_mail import Mail, Message

login_part = Blueprint('login_part', __name__,
                        template_folder='templates')

mail = Mail()

def save_file(file):
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    file = file_path
    return file

def generate_random_string(length=6):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

@login_part.route("/sign", methods=['GET', 'POST'])
def sign():
    if request.method == "POST":
        if len(request.form["email"]) < 1 or len(request.form["password"]) < 1 or len(request.form["name"]) < 1:
            flash("all fields must be filled")
        else:
            logo = request.files['logo']
            if logo:
                file_path = save_file(logo)
            else:
                file_path = None

            existing_email = Author.query.filter_by(email=request.form["email"]).first()
            existing_name = Author.query.filter_by(name=request.form["name"]).first()

            if existing_email is not None or existing_name is not None:
                flash("user with that name or email already exists")

            else:
                msg = Message('Subject', sender='w464mercedes@gmail.com', recipients=[request.form["email"]])
                code = generate_random_string()
                msg.body = f'Підтвердіть свій обліковий запис: {code}  https://w464.pythonanywhere.com//check '
                mail.send(msg)

                author = Authorization(email=request.form["email"],
                                    password=request.form["password"],
                                    name=request.form["name"],
                                    logo=file_path,
                                    code=code)
                db.session.add(author)
                db.session.commit()
                session.clear()
                return redirect('/check')
    return render_template('sign.html')


@login_part.route('/check', methods=['GET', 'POST'])
def check():
    if request.method == "POST":
        user = Authorization.query.filter_by(code=request.form["code"]).first()
        if user:
            author = Author(email=user.email,
                            password=user.password,
                            name=user.name,
                            logo=user.logo)
            db.session.add(author)
            db.session.commit()
            db.session.delete(user)
            db.session.commit()
            return redirect("/")
        else:
            flash("incorrect code")
    return render_template('check.html')


@login_part.route("/login", methods=['GET', 'POST'])
def login():
    if "userLogged" in session:
        return redirect(url_for("profile", username=session["userLogged"]))
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        author = Author.query.filter_by(email=email).\
                              filter_by(password=password).first()
        if author:
            session["userLogged"] = author.name
            return redirect(url_for("author_part.profile", username=session["userLogged"]))
        else:
            flash("incorrect password or email. <a href='/forgot'>Забули пароль?</a>?")
    return render_template("login.html")

@login_part.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == "POST":
        author = Author.query.filter_by(email=request.form["email"]).first()
        if author:
            msg = Message('Subject', sender='w464mercedes@gmail.com', recipients=[request.form["email"]])
            msg.body = f'Your password - {author.password}  https://w464.pythonanywhere.com/login'
            mail.send(msg)
            return redirect('/login')
        else:
            flash("email missing")
    return render_template("forgot.html")

