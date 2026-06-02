from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from dbqueries import get_questions_en, get_count_questions_en, get_user_by_username, get_user_by_id
import math

app = Flask(__name__)

app.secret_key = '0d23c6d3a41630ee92f7ba1a7dddaaacb029183c882778ef'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_page"

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    userData = get_user_by_id(int(user_id))
    if userData:
        return User(id=userData[0], username=userData[1])
    return None


@app.route('/', methods=['GET', 'POST'])
def home():
    questions = get_questions_en()
    if request.method == 'POST':
        pass
    if request.method == 'GET': 

        per_page = 25
        total_questions = get_count_questions_en()
        total_pages = math.ceil(total_questions / per_page)
        current_page = int(request.args.get('page', 1))
        questions = get_questions_en(per_page=per_page, current_page=current_page)

        return render_template('home.html', questions=questions, total_pages=total_pages, current_page=current_page)
    
@app.route('/login', methods=['GET', 'POST'])
def login_page():

    username = ""
    password = ""

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        userData = get_user_by_username(username)

        if userData and check_password_hash(userData[2], password):
            user_obj = User(id=userData[0], username=userData[1])
            login_user(user_obj)
            flash('Logged in successfully.')
            return redirect(url_for('home'))
        
        else:
            flash('Invalid username or password.')

    if request.method == 'GET':
        pass

    return render_template('loginpage.html', username=username, password=password)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)