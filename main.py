from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = ''

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    body = db.Column(db.String(225))
    

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['POST', 'GET'])
def index():
    
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        if  blog_title!="" and blog_body!="":
            new_blog = Blog(blog_title,blog_body)
            db.session.add(new_blog)
            db.session.commit()
            blog_id=new_blog.id
            blogs = Blog.query.all()
            return render_template('blogpage.html',blog_id=int(blog_id), blogs=blogs)
        else:
            if blog_title=='' and blog_body!='':
                error='please fill in the title'
            elif blog_title=='' and blog_body=='':
                error='please fill in both the title and the body'
            elif blog_title!='' and blog_body=='':
                error='please fill in the body'
            return redirect('/newpost?error='+error)
        
    else:
        blogs = Blog.query.all()
        blog_id=request.args.get('id')
        if blog_id!=None:
            return render_template('blogpage.html',blog_id=int(blog_id), blogs=blogs)
        return render_template('blog.html',title="Build A Blog", blogs=blogs)

@app.route('/newpost')
def add_blog():
    blog_error=request.args.get('error')
    blog_error=str(blog_error)
    if blog_error=='please fill in the title':
        return render_template('newpost.html',error_title=blog_error)
    elif blog_error=='please fill in the body':
        return render_template('newpost.html',error_body=blog_error)
    elif blog_error=='please fill in both the title and the body':
        error_title='please fill in the title'
        error_body='please fill in the body'
        return render_template('newpost.html',error_title=error_title,error_body=error_body)

    return render_template('newpost.html',title="Add Blog Entry") 

if __name__ == '__main__':
    app.run()