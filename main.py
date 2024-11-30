import smtplib
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv("C:/Python/Environmental variables/.env")

my_mail = "sampleforpythonmail@gmail.com"
password = os.getenv("smtp_app_password")


'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
CKEditor(app)
Bootstrap5(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


class NewPostForm(FlaskForm):
    title = StringField('Title',[DataRequired()])
    sub_title = StringField('Sub Title',[DataRequired()])
    author = StringField('Name',[DataRequired()])
    img_url = StringField('Blog Background Img Url',[URL()])
    body = CKEditorField('Blog Content',[DataRequired()])
    submit = SubmitField('Submit')


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    all_posts = db.session.execute(db.select(BlogPost)).scalars().all()
    return render_template("index.html", all_posts=all_posts)


@app.route('/<post_id>')
def show_post(post_id):
    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalars().all()[0]
    # Another way to retrieve data using post id
    #requested_post = db.get_or_404(BlogPost, post_id)
    return render_template("post.html", post=requested_post)



@app.route("/new-post",methods=["POST","GET"])
def add_new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title = form.title.data,
            subtitle = form.sub_title.data,
            author = form.author.data,
            date = datetime.today().strftime("%B %d, %Y"),
            body = form.body.data,
            img_url = form.img_url.data
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html",form=form)



@app.route("/edit-post/<post_id>",methods = ["POST","GET"])
def edit_post(post_id):
    query_post = db.session.execute(db.select(BlogPost).where(BlogPost.id==post_id)).scalars().all()[0]
    edit_form = NewPostForm(
            title=query_post.title,
            sub_title=query_post.subtitle,
            author=query_post.author,
            body=query_post.body,
            img_url=query_post.img_url,
        )
    if edit_form.validate_on_submit():
        query_post.title = edit_form.title.data
        query_post.subtitle = edit_form.sub_title.data
        query_post.author =edit_form.author.data
        query_post.body =edit_form.body.data
        query_post.img_url = edit_form.img_url.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=query_post.id))
    return render_template("make-post.html",edit_form=edit_form)



@app.route("/delete/<post_id>")
def delete_post(post_id):
    ## another way of selecting a specific row(post) --------------
    query_post =db.get_or_404(BlogPost, post_id)
    ##--------------------------------------------------------------
    db.session.delete(query_post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))

@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/contact',methods=["POST","GET"])
def contact():
    if request.method == "GET":
        return render_template("contact.html")
    if request.method == "POST":
        data = request.form
        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(my_mail, password=password)
            connection.sendmail(from_addr=my_mail,
                                to_addrs=my_mail,
                                msg=f"Subject:Message from Blog\n\n"
                                    f"Name : {data['name']}\n"
                                    f"Email : {data['email']}\n"
                                    f"Phone : {data['phone']}\n"
                                    f"Message : {data['message']}")
        return render_template("contact.html",submitted = True)



if __name__ == "__main__":
    app.run(debug=True, port=5003)
