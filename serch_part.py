from flask import Blueprint, render_template
from flask import request, session
from models import Article, Author



serch_part = Blueprint('serch_part', __name__,
                        template_folder='templates')

@serch_part.route("/")
def index():
    username = None
    if "userLogged" in session:
            username = session["userLogged"]
    articles_list = Article.query.all()
    authors_list = Author.query.all()
    return render_template("index.html",
                           username=username,
                           authors=authors_list,
                           articles=articles_list)

@serch_part.route('/search', methods=['GET', 'POST'])
def search_author():
    articles_list = Article.query.all()
    username = None
    if "userLogged" in session:
        username = session["userLogged"]
    if request.method == 'POST':
        search_query = request.form['search_query_author']
        authors_list = Author.query.filter(Author.name.like(f"%{search_query}%")).all()
        return render_template("index.html",
                               username=username,
                               articles=articles_list,
                               authors=authors_list)

@serch_part.route('/', methods=['GET', 'POST'])
def search_article():
    username = None
    if "userLogged" in session:
        username = session["userLogged"]
    if request.method == 'POST':
        search_query = request.form['search_query']
        articles_list = Article.query.filter(Article.text.like(f"%{search_query}%")).all()
        authors_list = Author.query.all()
        return render_template("index.html",
                                username=username,
                                articles=articles_list,
                                authors=authors_list)