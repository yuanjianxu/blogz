from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = b'\xc7\x17\x9c\xa1\xd7\xea4x'



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(225))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body,owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30),unique=True)
    password = db.Column(db.String(10))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','list_blogs','index','blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    blog_users = User.query.all()
    return render_template('index.html',title="home", blog_users=blog_users)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                session['username'] = username
                flash(session['username']+" Logged in")
                return render_template('newpost.html',title="newpost")
            else:
                flash("User password incorrect")
                return render_template('login.html')
        else:
            flash('this username does not exist')

    return render_template('login.html',title="login")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("A user with that username already exists")
            return render_template('signup.html')
        elif not username:
            flash("username invalid")
            return render_template('signup.html',username=username,title="signup")
        elif not password:
            flash("password can't empty")
            return render_template('signup.html',username=username,title="signup")
        elif not verify:
            flash("verify password can't empty")
            return render_template('signup.html',username=username,title="signup")
        elif password!=verify:
            flash("verify and password don't mathch")
            return render_template('signup.html',username=username,title="signup")
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return render_template('newpost.html',title="newpost")

    return render_template('signup.html',title="signup")

@app.route('/newpost')
def newpost():
    return render_template('newpost.html',title="newpost")

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')

@app.route('/blog', methods=['GET','POST'])
def blog():
    if request.method == 'POST':
        owner = User.query.filter_by(username=session['username']).first()
        blog_title = request.form['title']
        blog_body = request.form['body']
        if  blog_title!="" and blog_body!="":
            if len(blog_title)<25 and len(blog_body)<300:
                new_blog = Blog(blog_title,blog_body,owner)
                db.session.add(new_blog)
                db.session.commit()
                blog_id=new_blog.id
                blogs = Blog.query.filter_by(id=blog_id).all()
                users = User.query.all()
                return render_template('blogpage.html',title="blogpage", blogs=blogs,users=users)
            else:
                flash('entry title less than 25 and body less than 300!')
                return render_template('newpost.html',title="newpost")

        else:
            flash('we need both a title and a body!')
            return render_template('newpost.html',title="newpost")
        
    else:
        user_id=request.args.get('user_id')
        blog_id=request.args.get('blog_id')
        if user_id:
            blogs = Blog.query.filter_by(owner_id=user_id).all()
            users = User.query.all()
            user = User.query.filter_by(id=user_id).first()
            return render_template('blogs.html',title=user.username+"'blog", blogs=blogs,users=users)
        elif blog_id:
            blogs = Blog.query.filter_by(id=blog_id).all()
            users = User.query.all()
            return render_template('blogpage.html',title="blogpage", blogs=blogs,users=users)

@app.route('/list_blogs', methods=['POST', 'GET'])
def list_blogs():
    blogs = Blog.query.all()
    users = User.query.all()
    return render_template('blogs.html',title="all blogs", blogs=blogs,users=users)

if __name__ == '__main__':
    app.run()