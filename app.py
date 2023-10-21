import os
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.__init__(app)

class Post(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  title = db.Column(db.String)
  body = db.Column(db.String)
  image = db.Column(db.String)
  created_at = db.Column(db.DateTime, server_default=db.func.now())
  updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

  @property
  def get_image_url(self):
    return url_for('static', filename=f'posts/images/{self.image}')
  
  @property
  def get_show_url(self):
    return url_for('posts.show', id=self.id)
  
  @property
  def get_delete_url(self):
    return url_for('posts.delete', id=self.id)

# ************************************************

# Contact
def contact():
  return render_template('information/contact.html')

# About
def about():
  return render_template('information/about.html')

def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Landing
def landing():
  posts = Post.query.all()
  return render_template('posts/index.html', posts=posts)

# Create Post
def create():
  if request.method == 'POST':
    print('Received Data', request.form)
    file = request.files['image']
    if file.filename != '':
      if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        destination = os.path.join('static/posts/images', filename)
        file.save(destination)
    else:
      filename = None
    
    post = Post(title=request.form['title'], body=request.form['body'], image=filename)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('posts.index'))
  return render_template('posts/create.html')

# Get Post
def get_post(id):
  post = Post.query.get_or_404(id)
  if post:
    return render_template('posts/show.html', post=post)
  else:
    return 404
  
# Delete Post
def delete_post(id):
  post = Post.query.get_or_404(id)
  if post:
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('posts.index'))
  else:
    return 404

# Edit Post
def edit_post(id):
  post = Post.query.get_or_404(id)
  if request.method == 'POST':
    post.title = request.form['title']
    post.body = request.form['body']
    file = request.files['image']
    if file.filename != '':
      if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        destination = os.path.join('static/posts/images', filename)
        file.save(destination)
        post.image = filename
    else:
      filename = None
    
    db.session.commit()
    return redirect(post.get_show_url)
  return render_template('posts/edit.html', post=post)

# Error Page
@app.errorhandler(404)
def page_not_found(error):
  print(error)
  return  render_template('errors/page_not_found.html')

# ******************************************************

app.add_url_rule("/contact", view_func=contact, endpoint='contact', methods=['GET'])
app.add_url_rule("/about", view_func=about, endpoint='about', methods=['GET'])
app.add_url_rule("/posts", view_func=landing, endpoint='posts.index', methods=['GET'])
app.add_url_rule("/posts/create", view_func=create, endpoint='posts.create', methods=['GET', 'POST'])
app.add_url_rule("/posts/<int:id>", view_func=get_post, endpoint='posts.show', methods=['GET'])
app.add_url_rule("/posts/<int:id>/delete", view_func=delete_post, endpoint='posts.delete', methods=['GET'])
app.add_url_rule("/posts/<int:id>/edit", view_func=edit_post, endpoint='posts.edit', methods=['GET', 'POST'])

if __name__ == '__main__' :
  app.run(debug=True)