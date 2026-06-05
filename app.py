from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from dbqueries import get_questions_en, get_count_questions_en, update_question_votes, get_user_by_username, get_user_by_email, get_user_by_id, register_user
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


@app.route('/', methods=['GET'])
def home():
    category_id = request.args.get('category', type=int)
    current_page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort', 'newest')
    search_query = request.args.get('q', default='')

    total_questions = get_count_questions_en(category_id=category_id, search_query=search_query)
    total_pages = math.ceil(total_questions / per_page)
    questions = get_questions_en(per_page=per_page, current_page=current_page,
                                 category_id=category_id, sort_by=sort_by, search_query=search_query)

    return render_template('home.html',questions=questions,
                           total_pages=total_pages,
                           current_page=current_page,
                           selected_category=category_id,
                           per_page=per_page,
                           sort_by=sort_by, 
                           search_query=search_query)
    
@app.route('/search_autocomplete', methods=['GET'])
def search_autocomplete():
    query = request.args.get('q', '')
    if len(query) < 2: # Não pesquisa textos muito curtos
        return jsonify([])
    
    # Procura os 15 primeiros resultados correspondentes
    results = get_questions_en(per_page=15, current_page=1, search_query=query)
    
    # r[1] é o texto da pergunta (visto que o r[0] passou a ser o id_question)
    dropdown_items = [{"question": r[1]} for r in results]
    return jsonify(dropdown_items)

@app.route('/login', methods=['GET', 'POST'])
def login_page():

    username = ""
    password = ""

    if request.method == 'POST':
        username_email = request.form.get('username_email')
        password = request.form.get('password')
        if get_user_by_username(username_email):
            userData = get_user_by_username(username_email)
        elif get_user_by_email(username_email):
            userData = get_user_by_email(username_email)
        else:
            userData = None
            redirect(url_for('login_page'))
            flash('Invalid username or password.')
            flash('Try again!')

        if userData and check_password_hash(userData[2], password):
            user_obj = User(id=userData[0], username=userData[1])
            login_user(user_obj)
            flash('Logged in successfully.')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.')
            redirect(url_for('login_page'))

    if request.method == 'GET':
        pass

    return render_template('loginpage.html', username_email=username, password=password)

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if get_user_by_username(username) or get_user_by_email(email):   
            flash('Username or email already exists. Please choose a different one.')
            return render_template('registerpage.html', username=username, email=email, password=password)
        else:
            register_user(username, email, password)
            userData = get_user_by_username(username)
        if userData:
            flash('User registered successfully.')
            user_obj = User(id=userData[0], username=userData[1])
            login_user(user_obj)
            return redirect(url_for('home'))
        else: 
            flash('Registration failed. Please try again.')
    
    if request.method == 'GET':
        username = ""
        email = ""
        password = ""  

    return render_template('registerpage.html', username=username, email=email, password=password)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('home'))

@app.route('/vote', methods=['POST'])
def vote():
    data = request.get_json()
    if not data or 'question_id' not in data:
        return jsonify({'status': 'error', 'message': 'ID da pergunta inválido'}), 400

    question_id = int(data['question_id'])

    # 1. CRIA UMA CHAVE DE SESSÃO ÚNICA PARA CADA UTILIZADOR (OU ANÓNIMO)
    if current_user.is_authenticated:
        session_key = f"liked_questions_{current_user.id}"
    else:
        session_key = "liked_questions_anonymous"

    # Inicializa a lista se não existir na sessão
    if session_key not in session:
        session[session_key] = []

    # Cria uma cópia da lista para o Flask detetar a mutação corretamente
    liked_questions = list(session[session_key])

    if question_id in liked_questions:
        liked_questions.remove(question_id)
        action = 'unliked'
        amount = -1
    else:
        liked_questions.append(question_id)
        action = 'liked'
        amount = 1

    session[session_key] = liked_questions  # Guarda de volta na sessão única
    session.modified = True  # Força o Flask a atualizar o cookie no navegador

    # Atualiza o banco de dados
    try:
        update_question_votes(amount=amount, question_id=question_id)
    except TypeError:
        try:
            update_question_votes(question_id, amount)
        except TypeError:
            update_question_votes(amount, question_id)

    return jsonify({'status': 'success', 'action': action})

if __name__ == "__main__":
    app.run(debug=True)