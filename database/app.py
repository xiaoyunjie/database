# -*- coding:utf-8 -*-

"""
@Author     :   Browser
@file       :   app.py 
@time       :   2019/08/01
@software   :   PyCharm 
@description:   " "
"""

import os
import sys
import click
from flask import Flask,flash,url_for,render_template,redirect,abort
from flask_sqlalchemy import SQLAlchemy
from wtforms import validators
from wtforms import TextAreaField,SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from flask_migrate import Migrate

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


app = Flask(__name__)

app.secret_key = os.getenv('SECRET.KEY','secert string')
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(os.path.dirname(app.root_path),os.getenv('DATABASE_FILE','data.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', prefix + os.path.join(app.root_path, 'data.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app,db)

@app.cli.command()
# @click.option('--drop')

def initdb():
    if  drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized Database!!')


class NewNoteFrom(FlaskForm):
    body = TextAreaField('Body',validators=[DataRequired()])
    submit = SubmitField('save')

class EditNoteForm(NewNoteFrom):
    submit = SubmitField('Update')

class DeleteNoteForm(FlaskForm):
    submit = SubmitField('Delete')

class Note(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(),nullable=True)

    def __repr__(self):
        return '<Note %r>' % self.body


@app.shell_context_processor
def make_shell_context():
    return dict(db=db,Note=Note)

@app.route('/')
def index():
    form = DeleteNoteForm()
    notes = Note.query.all()
    return render_template('index.html',notes=notes,form=form)

@app.route('/new',methods=['GET','POST'])
def new_note():
    form = NewNoteFrom()
    if form.validate_on_submit():
        body = form.body.data
        note = Note(body=body)
        db.session.add(note)
        db.session.commit()
        flash('you note is save')
        return redirect(url_for('index'))
    return render_template('new_note.html',form=form)

@app.route('/edit/<int:note_id>',methods=['GET','POST'])
def edit_note(note_id):
    form = EditNoteForm()
    note = Note.query.get(note_id)
    if  form.validate_on_submit():
        note.body = form.body.data
        db.session.commit()
        flash('you note is updated')
        return redirect(url_for('index'))
    form.body.data = note.body
    return render_template('edit_note.html',form=form)

@app.route('/delete/<int:note_id>',methods=['POST'])
def delete_note(note_id):
    form = DeleteNoteForm()
    if form.validate_on_submit():
        note = Note.query.get(note_id)
        db.session.delete(note)
        db.session.commit()
        flash('you note is deleted')
    else:
        abort(400)
    return redirect(url_for('index'))

# one to many
class Author(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(70),unique=True)
    phone = db.Column(db.String(20))
    articles = db.relationship('Article')

    def __repr__(self):
        return '<Author %r>' % self.name

class Article(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(50),index=True)
    body = db.Column(db.Text)
    author_id = db.Column(db.Integer,db.ForeignKey('author.id'))  ## 表明.字段名, 外键

    def __repr__(self):
        return '<Article %r>' % self.title


# 双向关系
class Writer(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(70),unique=True)
    books = db.relationship('Book', back_populates='writer')

    def __repr__(self):
        return '<Writer %r>' % self.name

class Book(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),index=True)
    writer_id = db.Column(db.Integer,db.ForeignKey('writer.id'))
    writer = db.relationship('Writer', back_populates='books')

    def __repr__(self):
        return '<Book %r>' % self.name

# backref 简化

class Singer(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(70),unique=True)
    songs = db.relationship('Song',backref='singer')

    def __repr__(self):
        return '<Singer %r>' % self.name

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), index=True)
    singer_id = db.Column(db.Integer,db.ForeignKey('singer.id'))

    def __repr__(self):
        return '<Song %r>' % self.name


# many to one

class Citizen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    city_id = db.Column(db.Integer,db.ForeignKey('city.id'))
    city = db.relationship('City')

    def __repr__(self):
        return '<Citizen %r>' % self.name

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)

    def __repr__(self):
        return '<City %r>' % self.name


# one to one

class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    captital = db.relationship('Captital',uselist=False)

    def __repr__(self):
        return '<Country %r>' % self.name

class Captital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    country_id = db.Column(db.Integer,db.ForeignKey('country.id'))
    country = db.relationship('Country')

    def __repr__(self):
        return '<Country %r>' % self.name

# many to many

association_table = db.Table('association',
                             db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                             db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'))
                             )


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    grade = db.Column(db.String(20))
    teachers = db.relationship('Teacher', secondary=association_table, back_populates='students')

    def __repr__(self):
        return '<Student %r>' % self.name

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), unique=True)
    office = db.Column(db.String(20))
    students = db.relationship('Student', secondary=association_table, back_populates='teachers')

    def __repr__(self):
        return '<Teacher %r>' % self.name



