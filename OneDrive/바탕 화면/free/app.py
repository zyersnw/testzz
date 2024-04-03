from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


# SQLite 데이터베이스 연결
def get_db_connection():
    conn = sqlite3.connect('alphaDB.db')
    conn.row_factory = sqlite3.Row
    return conn

# 게시글 목록 조회

@app.route('/post_add')
def post_add():
    # 함수 구현
    return render_template('post_add.html')


@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

# 게시글 작성


@app.route('/post', methods=['POST'])
def add_post():
    title = request.form['title']
    content = request.form['content']
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
