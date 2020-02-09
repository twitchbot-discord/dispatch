from flask import Flask, g, redirect, render_template, send_from_directory
from flask_login import current_user, login_user, login_required, logout_user
from rethinkdb import RethinkDB
from ..utils import forms
from ..utils.login import User

r = RethinkDB()


def setup(app: Flask) -> None:

    @app.route('/assets/<fname>')
    def get_asset(fname):
        return send_from_directory('assets', fname)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect('/')

        form = forms.LoginForm()
        if form.validate_on_submit():
            user = User.get(form.username.data)
            if user is None or not user.check_pass(form.password.data):
                return redirect('/login?e=invalid_login')
            login_user(user)
            return redirect('/')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect('/login')

    @app.route('/')
    @login_required
    def index():
        return render_template('index.html')

    @app.route('/logs')
    @login_required
    def logs():
        logs = r.table('logs') \
            .order_by(index=r.desc('ts')) \
            .limit(100) \
            .run(g.rethinkdb)
        return render_template('logs.html', logs=logs)

    @app.route('/channels')
    @login_required
    def channels():
        return render_template('channels.html')

    @app.route('/sources')
    @login_required
    def sources():
        return render_template('sources.html')

    @app.route('/users')
    @login_required
    def users():
        users = r.table('users').run(g.rethinkdb)
        return render_template('users.html', users=users)
