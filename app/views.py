from flask import render_template, flash, redirect, request, url_for, g
from flask.ext.login import login_required, login_user, logout_user, current_user
from app import app, login_manager,db
from forms import LoginForm, RegistrationForm, EditForm, PostForm, SearchForm
from models import User, Post
from datetime import datetime
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS
from emails import follower_notification

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.search_form = SearchForm()

@app.route('/', methods=['GET','POST'])
@app.route('/<int:page>', methods=['GET','POST'])
@login_required
def show_entries(page=1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body = form.post.data, timestamp = datetime.utcnow(), author = g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('show_entries'))
    return render_template('show_entries.html', posts=Post.query.order_by(Post.timestamp.desc()).paginate(page,POSTS_PER_PAGE, False), user=current_user, form=form)

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
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('show_entries'))
    return render_template('user.html',
            user = user,
            posts =Post.query.order_by(Post.timestamp.desc()).paginate(page,POSTS_PER_PAGE, False))

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

@app.route('/follow/<nickname>')
def follow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname = nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname = nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    follower_notification(user, g.user)
    return redirect(url_for('user', nickname = nickname))

@app.route('/unfollow/<nickname>')
def unfollow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname = nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname = nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname = nickname))

@app.route('/followed_post')
def followed_post():
    form = PostForm()
    return render_template('followed_post.html', posts=g.user.followed_posts().all(), form=form, user=current_user)

@app.route('/search', methods = ['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('show_entries'))
    return redirect(url_for('search_results', query = g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
        query = query,
        results = results)
