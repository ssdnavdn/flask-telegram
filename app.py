from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import threading
import asyncio
from bot import main as run_bot  # импортируем main() из bot.py

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
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


@app.route("/")
def home():
    return "Приложение работает!"


@app.route('/topic/<topic>', methods=['GET', 'POST'])
def topic_page(topic):
    if request.method == 'POST':
        content = request.form['comment']
        db.session.add(Comment(topic=topic, content=content))
        db.session.commit()
        return redirect(url_for('topic_page', topic=topic))

    comments = Comment.query.filter_by(topic=topic).all()
    return render_template('topic.html', topic=topic, comments=comments)


def start_bot():
    asyncio.run(run_bot())


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    # Запуск Telegram-бота в отдельном потоке
    threading.Thread(target=start_bot, daemon=True).start()

    # Запуск Flask-приложения
    app.run(host='0.0.0.0', port=10000)  # Render слушает на порту 10000





