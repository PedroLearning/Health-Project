from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        pass
    if request.method == 'GET': 
        return render_template('home.html')
    
    questions = get_questions_by_category(categoryID)
    return render_template('home.html', questions=questions)
    

if __name__ == "__main__":
    app.run(debug=True)