from flask import Blueprint, render_template, redirect, current_app
from flask import request, session, url_for
from models import db, Article, Author, Comment, Subscription, Messages
from sqlalchemy.orm import sessionmaker
import os
from werkzeug.utils import secure_filename
import secrets
import string



author_part = Blueprint('author_part', __name__,
                        template_folder='templates')

def save_file(file):
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    file = file_path
    return file

def generate_random_string(length=6):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

def create_db_session():
    return sessionmaker(bind=db.engine)()

def search(data, attribute_name):
    lists = []
    for i in data:
        attr_value = getattr(i, attribute_name)
        lists.append(attr_value)
    return lists

def find_massages(data,list):
    for massage in data:
        list.append(massage)



@author_part.route("/author/<author_name>", methods=['GET', 'POST'])
def author(author_name):
    username = None
    if "userLogged" in session:
        username = session["userLogged"]

    author = Author.query.filter_by(name=author_name).first()
    authors_list = Author.query.all()
    subscriber = Author.query.filter_by(name=username).first()
    follower_id = Subscription.query.filter_by(author_id=author.id).all()
    following = Subscription.query.filter_by(subscriber_name=author_name).all()
    followers = search(follower_id,'subscriber_name')

    if request.method == "POST":
        if "userLogged" not in session or session["userLogged"] != username:
            return redirect(url_for('login'))

        subscriber = Author.query.filter_by(name=username).first()
        author = Author.query.filter_by(name=author_name).first()

        if subscriber and author:
            subscription = Subscription.query.filter_by(subscriber_name=subscriber.name, author_id=author.id).first()
            if subscription:
                db.session.delete(subscription)
                db.session.commit()
                return redirect(url_for('author_part.author', author_name=author.name))

        subscription = Subscription(subscriber_name=subscriber.name, author_id=author.id)
        db.session.add(subscription)
        db.session.commit()
        return redirect(url_for('author_part.author', author_name=author.name))

    return render_template("author.html",
                           authors=authors_list,
                           author=author,
                           username=username,
                           followers=followers,
                           following=following)



def following_serch(data):
    list = []
    for i in data:
        list.append(Author.query.filter_by(id=i).first())
    return list

@author_part.route("/author/<author_name>/following", methods=['GET', 'POST'])
def following(author_name):
    username = None
    if "userLogged" in session:
        username = session["userLogged"]
    author = Author.query.filter_by(name=author_name).first()
    authors_list = Author.query.all()
    subscriber = Author.query.filter_by(name=username).first()
    follower_id = Subscription.query.filter_by(subscriber_name=username).all()
    following = Subscription.query.filter_by(subscriber_name=author_name).all()
    followers = search(follower_id,'author_id')
    following_id = search(following,'author_id')
    followings = following_serch(following_id)


    if request.method == "POST":
        if "userLogged" not in session or session["userLogged"] != username:
            return redirect(url_for('login'))


        subscription = Subscription.query.filter_by(subscriber_name=subscriber.name, author_id=request.form['author.id']).first()
        if subscription:
            db.session.delete(subscription)
            db.session.commit()
            return redirect(url_for('author_part.author', author_name=author.name) + '/following')
        else:
            subscription = Subscription(subscriber_name=subscriber.name, author_id=request.form['author.id'])
            db.session.add(subscription)
            db.session.commit()
            return redirect(url_for('author_part.author', author_name=author.name) + '/following')
    return render_template("following.html",
                           authors=authors_list,
                           author=author,
                           author_page = author.name,
                           username=username,
                           followings=followings,
                           followers=followers)

def follower_search(data):
    list = []
    for i in data:
        list.append(Author.query.filter_by(name=i).first())
    return list

@author_part.route("/author/<author_name>/follower", methods=['GET', 'POST'])
def follower(author_name):
    username = None
    if "userLogged" in session:
        username = session["userLogged"]
    author = Author.query.filter_by(name=author_name).first()
    authors_list = Author.query.all()
    subscriber = Author.query.filter_by(name=username).first()
    follower = Subscription.query.filter_by(author_id=author.id).all()
    my_follower = Subscription.query.filter_by(subscriber_name=username).all()
    my_followers = search(my_follower,'author_id')
    follower_id = search(follower,'subscriber_name')
    followers = follower_search(follower_id)
    if request.method == "POST":
        if "userLogged" not in session or session["userLogged"] != username:
            return redirect(url_for('login'))

        subscription = Subscription.query.filter_by(subscriber_name=subscriber.name, author_id=request.form['author.id']).first()
        if subscription:
            db.session.delete(subscription)
            db.session.commit()
            return redirect(url_for('author_part.author', author_name=author.name) + '/follower')

        else:
            subscription = Subscription(subscriber_name=subscriber.name, author_id=request.form['author.id'])
            db.session.add(subscription)
            db.session.commit()
            return redirect(url_for('author_part.author', author_name=author.name) + '/follower')
    return render_template("follower.html",
                           authors=authors_list,
                           author=author,
                           author_page = author.name,
                           username=username,
                           followers=followers,
                           my_followers=my_followers)


@author_part.route("/profile/<username>")
def profile(username):
    if "userLogged" not in session or session["userLogged"] != username:
        return redirect('/login')
    authors_list = Author.query.all()
    author = Author.query.filter_by(name=username).first()
    return render_template("profile.html",
                           author=author,
                           authors=authors_list,
                           username=username)

@author_part.route('/profile/logout/<username>')
def logout(username):
    if "userLogged" in session and session["userLogged"] == username:
        session.clear()
    return redirect("/")


@author_part.route("/profile/<username>/set", methods=['GET', 'POST'])
def set_profile(username):
    if "userLogged" in session:
        logged_user = session["userLogged"]
    else:
        return redirect(url_for("login"))
    author = db.session.query(Author).filter(Author.name == logged_user).first()
    if request.method == 'POST':
        if 'photo' in request.files and request.files['photo'].filename:
            photo = request.files['photo']
            file_path = save_file(photo)
            author.photo = file_path
        if 'logo' in request.files and request.files['logo'].filename:
            logo = request.files['logo']
            file_path = save_file(logo)
            author.logo = file_path
        if 'age' in request.form and request.form['age'].isdigit():
            author.age = int(request.form['age'])
        else:
            author.age = None
        if 'work' in request.form and request.form['work']:
            author.work = request.form['work']
        else:
            author.work = None
        if 'hobby' in request.form and request.form['hobby']:
            author.hobby = request.form['hobby']
        else:
            author.hobby = None
        db.session.commit()

        return redirect(url_for("author_part.profile", username=logged_user))
    return render_template('set_profile.html',
                            username=logged_user,
                            author=author)

@author_part.route('/profile/<username>/delete', methods=['GET', 'POST'])
def delete_profile(username):
    if request.method == 'POST':
        def delete_data(data):
            for i in data:
                db.session.delete(i)
        author = db.session.query(Author).filter(Author.name==username).first()
        articles_author = db.session.query(Article).filter(Article.author_name==author.name).all()
        comments_author = db.session.query(Comment).filter(Comment.author_id==author.id).all()
        followers_author = db.session.query(Subscription).filter(Subscription.subscriber_name==author.name).all()
        followings_author = db.session.query(Subscription).filter(Subscription.author_id==author.id).all()
        messeages_author = db.session.query(Messages).filter(Messages.author_id==author.id).all()
        if author:
            if followers_author:
                delete_data(followers_author)
            if followings_author:
                delete_data(followings_author)
            if articles_author:
                delete_data(articles_author)
            if comments_author:
                delete_data(comments_author)
            if followers_author:
                delete_data(messeages_author)
            db.session.delete(author)
            db.session.commit()
            session.clear()
        return redirect('/')
    return render_template('delete_author.html',
                           username=username)



