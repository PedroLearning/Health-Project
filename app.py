from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from dbqueries import get_questions_en, get_count_questions_en, get_role_current_user, update_question_votes, get_user_by_username, get_user_by_email, get_user_by_id, register_user
import sqlite3
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

    #For Questions
    category_id = request.args.get('category', type=int)
    current_page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort', 'newest')
    search_query = request.args.get('q', default='')

    total_questions = get_count_questions_en(category_id=category_id, search_query=search_query)
    total_pages = math.ceil(total_questions / per_page)
    questions = get_questions_en(per_page=per_page, current_page=current_page,
                                    category_id=category_id, sort_by=sort_by, search_query=search_query)
    
    #For dynamic NavBar
    if current_user.is_authenticated: 
        user_id = current_user.id
        role_data = get_role_current_user(user_id)
        role = role_data[0] if role_data else 2
    else:
        role = 2

    return render_template('home.html',questions=questions,
                            total_pages=total_pages,
                            current_page=current_page,
                            selected_category=category_id,
                            per_page=per_page,
                            sort_by=sort_by, 
                            search_query=search_query,
                            role=role)
    
@app.route('/search_autocomplete', methods=['GET'])
def search_autocomplete():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])

    from dbqueries import get_questions_en
    # Busca os dados no banco de dados baseados no termo digitado
    matching_questions = get_questions_en(per_page=5, current_page=1, search_query=query)
    
    # IMPORTANTE: q[1] é a pergunta em texto (ex: "What is anxiety?"). q[0] é apenas o ID numérico.
    results = [{'id': q[0], 'question': q[1]} for q in matching_questions]
    return jsonify(results)

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
            flash('Invalid username/email')
            flash('Try again!')

        if userData[3] == 2:
            flash('Deactivated account')
            flash('Contact our support!')
            return redirect(url_for('login_page'))

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

@app.route('/menu_users', methods=['GET', 'POST'])
@login_required
def menu_users():

    def get_users_for_edit():    
        with sqlite3.connect('FAQHealth.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT id_user, username, email, r.id_role, u.id_status, s.status_name 
            FROM users u
            JOIN status s ON s.id_status = u.id_status
            JOIN roles r ON r.id_role = u.id_role''')
            return cursor.fetchall()

    users = get_users_for_edit()

    return render_template('menu_users.html', users=users)

#Change Status
@app.route('/admin/change_status', methods=['POST'])
@login_required
def change_status():
    data = request.get_json()
    user_id = data.get('user_id')
    target_status = data.get('target_status') # 1 or 2
    
    if target_status not in [1, 2]:
        return jsonify({'status': 'error', 'message': 'Invalid status choice'}), 400
        
    try:
        import sqlite3
        with sqlite3.connect('FAQHealth.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET id_status = ? 
                WHERE id_user = ?
            ''', (target_status, user_id))
            conn.commit()
            
        # Define structural text and rules for the next click cycle
        # Status 1 = Active, Status 2 = Inactive (as defined in your status table)
        status_name = "Active" if target_status == 1 else "Inactive"
        next_status = 2 if target_status == 1 else 1
        
        return jsonify({
            'status': 'success',
            'current_status': target_status,
            'next_status': next_status,
            'status_name': status_name
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/update_user', methods=['GET', 'POST'])
@login_required
def update_user():
    if request.method == 'POST':
        user_id = request.form.get('id')
        username = request.form.get('username')
        email = request.form.get('email')
        role_id = request.form.get('role') # Extract numeric index from select dropdown string

        # Security Fallback: If role_id was disabled by JS (e.g. for user 1 or 2), 
        # standard forms won't submit it. We verify or preserve its active database layout
        if not role_id and (user_id == "1" or user_id == "2"):
            role_id = 1 # Force retention of Admin privileges on crucial core accounts

        try:
            with sqlite3.connect('FAQHealth.db') as conn:
                cursor = conn.cursor()
                # Run complete parameter tuple array assignment sequencing matching your DB columns
                cursor.execute('''
                    UPDATE users
                    SET username = ?, email = ?, id_role = ?
                    WHERE id_user = ?
                ''', (username, email, role_id, user_id))
                conn.commit()
                flash('User updated successfully!')
        except Exception as e:
            flash(f'Error updating user: {e}')
            print(f'Database update exception: {e}')
        
        # Standard loopback redirect to refresh UI views safely
        return redirect(url_for('menu_users'))
        
    return redirect(url_for('menu_users'))

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