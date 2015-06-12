from flask import render_template, flash, redirect, request, url_for, g
from flask.ext.login import login_required, login_user, logout_user, current_user
from app import app, login_manager,db
from forms import LoginForm, RegistrationForm, EditForm, PostForm
from models import User, Post
from datetime import datetime

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/', methods=['GET','POST'])
@login_required
def show_entries():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body = form.post.data, timestamp = datetime.utcnow(), author = g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('show_entries'))
    return render_template('show_entries.html', posts=Post.query.order_by(Post.timestamp.desc()).all(), user=current_user, form=form)

@app.route('/test')
@login_required
def test():
    return 'test'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('show_entries'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.name.data).first()
        if user is not None and user.password == form.password.data:
            login_user(user)
            flash('You were logged in')
            return redirect(request.args.get('next') or url_for('show_entries'))
        flash('Invalid username of password.')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/signup', methods=['GET','POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(nickname=form.name.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You can now login.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#personal profile
@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('show_entries'))
    return render_template('user.html',
            user = user,
            posts =Post.query.order_by(Post.timestamp.desc()).all())

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html',
        form = form)
