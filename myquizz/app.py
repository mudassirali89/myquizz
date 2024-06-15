import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///quizzes.db')
db = SQLAlchemy(app)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    options = db.Column(db.String(500), nullable=False)
    correct_option = db.Column(db.String(200), nullable=False)
    explanation = db.Column(db.String(500), nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        data = request.get_json()
        new_quiz = Quiz(name=data['quiz_name'])
        db.session.add(new_quiz)
        db.session.commit()

        for question in data['questions']:
            new_question = Question(
                quiz_id=new_quiz.id,
                name=question['name'],
                options=question['options'],
                correct_option=question['correct_option'],
                explanation=question['explanation']
            )
            db.session.add(new_question)
        db.session.commit()

        return jsonify({'message': 'Quiz created successfully'}), 201

    return render_template('create_quiz.html')

@app.route('/quizzes')
def get_quizzes():
    quizzes = Quiz.query.all()
    return render_template('quizzes.html', quizzes=quizzes)

@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def participate_quiz(quiz_id):
    if request.method == 'POST':
        quiz = Quiz.query.get(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        score = 0
        total_questions = len(questions)
        user_answers = request.form.to_dict()

        for question in questions:
            if user_answers.get(f'question_{question.id}') == question.correct_option:
                score += 1

        return render_template('results.html', quiz=quiz, score=score, total_questions=total_questions)
    
    quiz = Quiz.query.get(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('participate_quiz.html', quiz=quiz, questions=questions)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
