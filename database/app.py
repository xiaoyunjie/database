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

    def __repr__(self):
        return '<Note %r>' % self.body


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