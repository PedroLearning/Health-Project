from flask import Flask, render_template, request 
from dbqueries import get_questions_en, get_count_questions_en
import math

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True)