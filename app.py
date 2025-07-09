from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    with sqlite3.connect('reviews.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                sentiment TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        conn.commit()

def analyze_sentiment(text):
    text_lower = text.lower()
    positive_keywords = ['хорош', 'люблю', 'отлично', 'замечательно', 'класс']
    negative_keywords = ['плохо', 'ненавиж', 'ужасно', 'отвратительно', 'не нравится']
    
    for word in positive_keywords:
        if word in text_lower:
            return 'positive'
    for word in negative_keywords:
        if word in text_lower:
            return 'negative'
    return 'neutral'

@app.route('/reviews', methods=['POST'])
def add_review():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    sentiment = analyze_sentiment(text)
    created_at = datetime.utcnow().isoformat()
    
    with sqlite3.connect('reviews.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO reviews (text, sentiment, created_at) VALUES (?, ?, ?)',
            (text, sentiment, created_at)
        )
        review_id = cursor.lastrowid
        conn.commit()
    
    return jsonify({
        'id': review_id,
        'text': text,
        'sentiment': sentiment,
        'created_at': created_at
    })

@app.route('/reviews', methods=['GET'])
def get_reviews():
    sentiment_filter = request.args.get('sentiment')
    query = 'SELECT id, text, sentiment, created_at FROM reviews'
    params = ()
    if sentiment_filter:
        query += ' WHERE sentiment = ?'
        params = (sentiment_filter,)
    
    with sqlite3.connect('reviews.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
    
    reviews = [
        {'id': row[0], 'text': row[1], 'sentiment': row[2], 'created_at': row[3]}
        for row in rows
    ]
    return jsonify(reviews)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
