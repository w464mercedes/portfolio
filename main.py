from flask import Flask, render_template, redirect, request, url_for
from models import db, Article, Author, Comment, Subscription, Messages, Like, Authorization, User
from flask_admin import Admin
from dotenv import load_dotenv
from flask_mail import Mail
from author_part import author_part
from article_part import article_part
from serch_part import serch_part
from login_part import login_part
from chat_part import chat_part
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, login_user, current_user
from wtforms_alchemy import ModelForm
login_manager = LoginManager()

load_dotenv()

app = Flask(__name__)
login_manager.init_app(app)

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

class MicroBlogModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class UserForm(ModelForm):
    class Meta:
        model = User

@app.route('/admin/login', methods=['POST','GET'])
def admin_login():
    form = UserForm()
    if request.method == "POST":
        user = User.query.filter_by(name=request.form['name'], password=request.form['password']).first()
        if user:
            login_user(user)
            return redirect('/admin')
    return render_template('admin_login.html',form=form)


with app.app_context():
    db.create_all()

admin = Admin(app, name='Portfolio', template_mode='bootstrap3')
admin.add_view(MicroBlogModelView(Article, db.session))
admin.add_view(MicroBlogModelView(Author, db.session))
admin.add_view(MicroBlogModelView(Comment, db.session))
admin.add_view(MicroBlogModelView(Subscription, db.session))
admin.add_view(MicroBlogModelView(Messages, db.session))
admin.add_view(MicroBlogModelView(Like, db.session))
admin.add_view(MicroBlogModelView(Authorization, db.session))
admin.add_view(MicroBlogModelView(User, db.session))


