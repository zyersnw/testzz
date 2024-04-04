from datetime import datetime
from flask import Flask, render_template, url_for, request
import os
from flask_sqlalchemy import SQLAlchemy
import requests
from werkzeug.utils import redirect


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    subject = db.Column(db.String, nullable=False)
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 이 post 부분을 앞으로 쓰실 게시글 db의 primary_key 이름을 사용하시면 됩니다.
    # ex) class Question에서 id = primary_key = True라면, post_id --> question_id
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id', ondelete='CASCADE'))
    # Post --> Question
    post = db.relationship('Post', backref=db.backref('answer_set'))
    username = db.Column(db.String, nullable=False)
    content = db.Column(db.Text(), nullable=False)
    create_date = db.Column(db.DateTime(), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    # posts라는 바구니에 Post 테이블에 있는 모든 컬럼들을 저장합니다.
    posts = Post.query.all()
    # 각 데이터의 필드를 따로 분리하여 리스트에 저장
    # html에 보낼 바구니 이름을 정합니다. ex) ids라는 바구니에 id 컬럼을 for문을 돌려 모두 담는다.
    ids = [post.id for post in posts]
    usernames = [post.username for post in posts]
    subjects = [post.subject for post in posts]
    contents = [post.content for post in posts]
    create_dates = [post.create_date for post in posts]
    # index.html 렌더 템플릿으로 필드 리스트를 전달
    # posts라는 바구니 = html에서도 posts라는 이름을 쓰겠다. 이하 동문
    return render_template('index.html', posts=posts, ids=ids, usernames=usernames, subjects=subjects, contents=contents, create_dates=create_dates)


@app.route('/post_add')
def post_add():
    return render_template('post_add.html')


@app.route('/post_add_button', methods=['GET', 'POST'])
def post_add_button():
    # GET 메소드를 사용해서 html에서 input을 사용해서 넣은 값을 receive로 받습니다.
    username_receive = request.args.get("username")
    subject_receive = request.args.get("subject")
    content_receive = request.args.get("content")

    # 현재 시각을 가져오기
    current_datetime = datetime.now()

    # 새로운 게시물 생성
    # new_post라는 리스트에 Post 테이블에서 GET 메소드를 이용해 받아온 값들을 담습니다.
    new_post = Post(username=username_receive, subject=subject_receive,
                    content=content_receive, create_date=current_datetime)
    # db.session.add(new_post)를 사용하여 db에 추가합니다.
    db.session.add(new_post)
    # db.session.commit()으로 추가한 데이터를 저장합니다
    db.session.commit()
    # redirect와 url_for를 사용해서, 저는 메인 페이지로 가도록 했지만, 댓글을 쓰신다면 게시글 페이지로 가도록 하여, 정보가 나오게 하시면 됩니다.
    return redirect(url_for('home'))


@app.route('/comment_add/<int:post_id>')
def comment_add(post_id):
    post = Post.query.get(post_id)
    answer = Answer.query.filter(Answer.post_id == post_id).all()
    return render_template('post.html', post=post, answer=answer)


@app.route('/coment_add_button/<int:post_id>', methods=['GET', 'POST'])
def comment_add_button(post_id):
    username_receive = request.args.get("username")
    content_receive = request.args.get("content")
    post = Post.query.get(post_id)
    current_datetime = datetime.now()
    new_answer = Answer(username=username_receive, post=post,
                        content=content_receive, create_date=current_datetime)
    db.session.add(new_answer)
    db.session.commit()
    return redirect(url_for('comment_add', post_id=post_id))

def search_comments():
    if request.method == 'POST':
        search_option = request.form.get("searchOption")
        search_input = request.form.get("commentSearchInput")
        
        posts = []
        answers = []
        
        if search_option == 'postTitle':
            posts = Post.query.filter(Post.subject.like('%{}%'.format(search_input))).all()
        elif search_option == 'postAuthor':
            posts = Post.query.filter(Post.username.like('%{}%'.format(search_input))).all()
        elif search_option == 'commentContent':
            answers = Answer.query.filter(Answer.content.like('%{}%'.format(search_input))).all()
        elif search_option == 'commentAuthor':
            answers = Answer.query.filter(Answer.username.like('%{}%'.format(search_input))).all()
        
        return render_template('index.html', posts=posts, answers=answers)


if __name__ == "__main__":
    app.run(debug=True)
