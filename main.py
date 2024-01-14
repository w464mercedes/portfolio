from flask import Flask
from models import db, Article, Author, Comment, Subscription, Messages, Like, Authorization
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os
from dotenv import load_dotenv
from flask_mail import Mail
from author_part import author_part
from article_part import article_part
from serch_part import serch_part
from login_part import login_part
from chat_part import chat_part

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://w464:Xxx1941900@w464.mysql.pythonanywhere-services.com/w464$new_db'
app.secret_key = "s;lf;ewlkm;leqfmql"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
# mail service
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'w464mercedes@gmail.com'
app.config['MAIL_PASSWORD'] = 'ssyf nhqg voxm fksf'
# blueprint parts
app.register_blueprint(author_part)
app.register_blueprint(article_part)
app.register_blueprint(serch_part)
app.register_blueprint(login_part)
app.register_blueprint(chat_part)

mail = Mail(app)
db.init_app(app)


with app.app_context():
    db.create_all()

admin = Admin(app, name='Portfolio', template_mode='bootstrap3')
admin.add_view(ModelView(Article, db.session))
admin.add_view(ModelView(Author, db.session))
admin.add_view(ModelView(Comment, db.session))
admin.add_view(ModelView(Subscription, db.session))
admin.add_view(ModelView(Messages, db.session))
admin.add_view(ModelView(Like, db.session))
admin.add_view(ModelView(Authorization, db.session))



