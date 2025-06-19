from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100))
    content = db.Column(db.Text)
    telegram_id = db.Column(db.String(50), nullable=True)

# ✅ Создание таблиц при любом запуске
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "Приложение работает!"

@app.route('/topic/<topic>', methods=['GET', 'POST'])
def topic_page(topic):
    if request.method == 'POST':
        content = request.form.get('comment', '').strip()
        if content:
            db.session.add(Comment(topic=topic, content=content))
            db.session.commit()
        return redirect(url_for('topic_page', topic=topic))

    comments = Comment.query.filter_by(topic=topic).all()
    return render_template('topic.html', topic=topic, comments=comments)




