from flask import Blueprint, render_template
from flask import render_template, redirect
from flask import request, session, url_for, flash 
from models import db, Author, Messages
from sqlalchemy import or_

chat_part = Blueprint('chat_part', __name__,
                        template_folder='templates')

@chat_part.route('/profile/chat/<author_name>', methods=['GET', 'POST'])
def chat(author_name):
    username = None
    if "userLogged" in session:
        username = session["userLogged"]
    if "userLogged" not in session or session["userLogged"] != username:
            return redirect(url_for('login'))
    
    authors_list = Author.query.all()
    receiver = Author.query.filter_by(name=username).first()
    author = Author.query.filter_by(name=author_name).first()
    massages_for_me = Messages.query.filter(Messages.author_id == author.id, Messages.receiver_id == receiver.id).all()
    my_massages = Messages.query.filter(Messages.author_id == receiver.id, Messages.receiver_id == author.id).all() 

    all_messages = massages_for_me + my_massages
    messages = sorted(all_messages, key=lambda x: x.date)

    if request.method == 'POST':
        if 'message_id' in request.form and request.form['message_id']:
            message_id = request.form['message_id']
            new_text = request.form['text']
            message = Messages.query.get(message_id)
            if len(new_text) < 1:
                flash('Please enter your massage')
            else:
                message.text = new_text
                db.session.commit()
                return redirect(url_for('chat_part.chat', author_name=author_name))  
        elif len(request.form['text']) < 1:
            flash('Please enter your massage')
        else:
            my_massage = Messages(text=request.form.get('text'),
                                author_id=receiver.id,
                                receiver_id=author.id) 
            db.session.add(my_massage)
            db.session.commit()
            return redirect(url_for('chat_part.chat', author_name=author_name))
    return render_template('chat_author.html',
                           authors=authors_list,
                           username=username,
                           author=author,
                           massages=messages)


@chat_part.route('/profile/<username>/messages', methods=['GET', 'POST'])
def massages(username):
    username = None
    if "userLogged" in session:
        username = session["userLogged"]
    if "userLogged" not in session or session["userLogged"] != username:
            return redirect(url_for('login'))
    authors_list = Author.query.all()
    receiver = Author.query.filter_by(name=username).first()
    messages = Messages.query.filter(or_(Messages.receiver_id == receiver.id, Messages.author_id == receiver.id)).all()
    authors = []
    for author in messages:
        sender = Author.query.filter(Author.id == author.receiver_id).first()
        if sender.id != receiver.id:
            authors.append(sender)
    for author in messages:
        sender = Author.query.filter(Author.id == author.author_id).first()
        if sender.id != receiver.id:
            authors.append(sender)
    chats = list(set(authors))
    return render_template('messages.html',
                           username=username,
                           author=receiver,
                           authors=authors_list,
                           chats=chats)

@chat_part.route('/profile/delete/<message_id>', methods=['GET', 'POST'])
def delete_message(message_id):
    username = None
    if "userLogged" in session:
        username = session["userLogged"]
    if "userLogged" not in session or session["userLogged"] != username:
            return redirect(url_for('login'))
    message = db.session.query(Messages).filter(Messages.id == message_id).first()
    author = Author.query.filter(Author.id == message.receiver_id).first()
    if request.method == 'POST':
        if message:  
            db.session.delete(message)   
            db.session.commit()
            return redirect(f'/profile/chat/{author.name}')
    return render_template('delete_message.html',
                           message_id=message_id)

