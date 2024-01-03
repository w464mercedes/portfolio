from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone
from sqlalchemy import DateTime

db = SQLAlchemy()

class Article(db.Model):
    __tablename__ = "article"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow().replace(microsecond=0))
    content = db.Column(db.String(100))
    author_name = db.Column(db.String(50), db.ForeignKey('author.name'))
    likes = db.relationship('Like', backref='article_like', lazy='dynamic')
    comments = db.relationship('Comment', backref='article_comments', lazy='dynamic') 
    like_count = db.Column(db.Integer, default=0)

    def __str__(self):
        return self.text

class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    author_name = db.Column(db.String(50), db.ForeignKey('author.name'))
    authors = db.relationship('Author', backref='author_like', lazy='joined', foreign_keys=[author_name])


class Author(db.Model):
    __tablename__ = "author"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    name = db.Column(db.String(50), unique=True)
    age = db.Column(db.String(50))
    hobby = db.Column(db.String(250))
    work = db.Column(db.String(250))
    photo = db.Column(db.String(100))
    logo = db.Column(db.String(250))
    likes = db.relationship('Like', backref='author_like', lazy='dynamic')
    articles = db.relationship('Article', backref='author', lazy='dynamic')
    author_comments = db.relationship('Comment', backref='comments_authored', lazy='dynamic')
    
    def __str__(self):
        return self.name

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow().replace(microsecond=0))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))  
    author = db.relationship('Author', backref='comments', lazy='joined')
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]))  

    def __str__(self):
        return self.text


class Messages(db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow().replace(microsecond=0))
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    receiver_id =  db.Column(db.Integer, db.ForeignKey('author.id'))

    def __str__(self):
        return self.text
    
class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = db.Column(db.Integer, primary_key=True)
    subscriber_name = db.Column(db.String(50), db.ForeignKey('author.name'))  
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))  

    def __str__(self):
        return f"Subscriber: {self.subscriber_name} -> Author: {self.author_id}"
    

class Authorization(db.Model):
    __tablename__ = 'authorization'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6))
    email = db.Column(db.String(50))
    password = db.Column(db.String(50))
    name = db.Column(db.String(50))
    logo = db.Column(db.String(250))