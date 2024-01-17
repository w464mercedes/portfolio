from flask import Blueprint, render_template, redirect
from flask import current_app
from flask import request, session, url_for, flash
from models import db, Article, Author, Comment, Like
import os
from werkzeug.utils import secure_filename



article_part = Blueprint('article_part', __name__,
                        template_folder='templates')

def save_file(file):
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    file = file_path
    return file

@article_part.route('/article/add/<username>', methods=['GET', 'POST'])
def add_article(username):
    if request.method == "POST":
        if "userLogged" in session:
            username = session["userLogged"]

        author = Author.query.filter_by(name=username).first()
        file_path = None
        if request.files['content']:
            file_path = save_file(request.files['content'])

        if len(request.form['text']) > 1 or request.files['content']:
            article = Article(
                text=request.form['text'],
                content=file_path if file_path else None)
            author.articles.append(article)
            db.session.add(article)
            db.session.commit()
            return redirect('/')
        else:
            flash("Read your article")
    return render_template('add_article.html')


@article_part.route('/article/delete/<int:article_id>', methods=['GET', 'POST'])
def delete_article(article_id):
    username = None
    if "userLogged" in session:
        username = session["userLogged"]
    if request.method == 'POST':
        article = Article.query.filter(Article.id==article_id).first()
        if article:
            db.session.delete(article)
            db.session.commit()
        return redirect(url_for("author_part.profile", username=session["userLogged"]))
    return render_template('delete_article.html',
                           username=username,
                           article_id=article_id)



@article_part.route('/article/update/<int:article_id>', methods=['GET', 'POST'])
def update_article(article_id):
    username = None
    if "userLogged" in session:
        username = session["userLogged"]
    article = db.session.query(Article).filter(Article.id == article_id).first()
    if request.method == 'POST':
        content = request.files['content']
        text = request.form['text']
        file_path = None
        if content:
            file_path = save_file(content)
        article.text = text
        article.content = file_path
        db.session.commit()
        return redirect(url_for("author_part.profile", username=session["userLogged"]))
    return render_template('update_article.html', username=username, article=article)

@article_part.route('/article/<int:article_id>/like', methods=['GET', 'POST'])
def like(article_id):
    username = None
    if "userLogged" in session:
        username = session["userLogged"]

        like = Like.query.filter_by(article_id=article_id, author_name=username).first()
        article = Article.query.filter_by(id=article_id).first()
        if like:
            db.session.delete(like)
            article.like_count = article.like_count - 1
            db.session.commit()
            db.session.close()

        else:
            like = Like(article_id=article_id,
                        author_name=username)
            article.likes.append(like)
            article.like_count = article.like_count + 1
            db.session.add(like)
            db.session.commit()
    return redirect('/')

@article_part.route('/article/<int:article_id>/comment', methods=["GET", "POST"])
def article_comment(article_id):
    username = None
    if "userLogged" in session:
        username = session["userLogged"]

    author = Author.query.filter_by(name=username).first()
    article = Article.query.filter(Article.id == article_id).first()
    comments = article.comments
    authors_list = Author.query.all()
    if request.method == 'POST':
        if "userLogged" not in session or session["userLogged"] != username:
            return redirect(url_for('login_part.login'))

        if len(request.form['comment_text']) < 1:
            flash('Please enter your comment')

        elif 'parent_comment_id' in request.form and request.form['parent_comment_id']:
            parent_comment_id = int(request.form['parent_comment_id'])
            recomment_text = request.form['comment_text']
            recomment = Comment(text=recomment_text,
                                author_id=author.id,
                                article_id=article_id,
                                parent_comment_id=parent_comment_id)
            db.session.add(recomment)
            db.session.commit()
        else:
            comment_text = request.form['comment_text']
            new_comment = Comment(text=comment_text,
                                  author_id=author.id,
                                  article_id=article_id)
            db.session.add(new_comment)
            db.session.commit()
    return render_template("article_comment.html",
                           article=article,
                           authors=authors_list,
                           username=username,
                           comments=comments)

@article_part.route('/comment/delete/<int:comment_id>', methods=['GET', 'POST'])
def delete_comment(comment_id):

    def delete_replies(comment_id):
        replies = db.session.query(Comment).filter(Comment.parent_comment_id == comment_id).all()
        for reply in replies:
            delete_replies(reply.id)
            db.session.delete(reply)

    comment_ = Comment.query.filter(Comment.id == comment_id).first()
    article_id = comment_.article_id
    username = None
    if "userLogged" in session:
        username = session["userLogged"]
    if request.method == 'POST':

        comment = db.session.query(Comment).filter(Comment.id == comment_id).first()
        if comment:
            delete_replies(comment_id)
            db.session.delete(comment)
            db.session.commit()
            return redirect(f"/article/{article_id}/comment")
    return render_template('delete_comment.html',
                           username=username,
                           comment_id=comment_id,
                           article_id=article_id)

