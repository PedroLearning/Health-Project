from flask import Flask, render_template, request 
from dbqueries import get_questions_en

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    questions = get_questions_en()
    if request.method == 'POST':
        pass
    if request.method == 'GET': 
        return render_template('home.html', questions=questions)

if __name__ == "__main__":
    app.run(debug=True)