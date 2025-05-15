from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# MySQL Configuration
db_config = {
    'user': 'root',
    'password': 'Sivani09!',
    'host': 'localhost',
    'database': 'blog_db'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM posts ORDER BY created_at DESC LIMIT 3')
    posts = cursor.fetchall()
    for post in posts:
        cursor.execute('SELECT * FROM comments WHERE post_id = %s ORDER BY created_at DESC', (post['id'],))
        post['comments'] = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/archive')
def archive():
    category = request.args.get('category', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if category:
        cursor.execute('SELECT * FROM posts WHERE category = %s ORDER BY created_at DESC', (category,))
    else:
        cursor.execute('SELECT * FROM posts ORDER BY created_at DESC')
    posts = cursor.fetchall()
    cursor.execute('SELECT DISTINCT category FROM posts')
    categories = [row['category'] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template('archive.html', posts=posts, categories=categories, selected_category=category)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            data = request.get_json()
            name = data['name']
            email = data['email']
            message = data['message']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO contact_messages (name, email, message, created_at) VALUES (%s, %s, %s, %s)',
                (name, email, message, datetime.now())
            )
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'status': 'success'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    return render_template('contact.html')

@app.route('/submit-comment', methods=['POST'])
def submit_comment():
    try:
        data = request.get_json()
        post_id = data['post_id']
        name = data['name']
        comment = data['comment']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO comments (post_id, name, comment, created_at) VALUES (%s, %s, %s, %s)',
            (post_id, name, comment, datetime.now())
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)