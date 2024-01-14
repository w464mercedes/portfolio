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

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DB']
app.config['FLASK_ADMIN_SWATCH'] = os.environ['ADMIN_THEME']
app.secret_key = os.environ['SEKRET_KEY']
app.config['UPLOAD_FOLDER'] = os.environ['UPLOAD_FOLDER']
# mail service **
app.config['MAIL_SERVER'] = os.environ['MAIL_SERVER']
app.config['MAIL_PORT'] = os.environ['MAIL_PORT']
app.config['MAIL_USE_TLS'] = os.environ['MAIL_USE_TLS']
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME'] 
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
# blueprint parts **
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

if __name__ == '__main__':
    app.run()

