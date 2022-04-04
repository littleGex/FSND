import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    formatted_questions = questions[start:end]

    return formatted_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app)

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow_Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow_Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        formatted_categories = [category.format() for category in categories]
        return jsonify({
          'success': True,
          'categories': formatted_categories,
          'total_categories': len(formatted_categories),
        })

    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
    
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/question')
    def get_questions():
        questions = Question.query.all()
        categories = Category.query.all()

        formatted_questions = paginate_questions(request, questions)
        formatted_categories = [category.format() for category in categories]
        category_items = [(category.id, category.type) for category in categories]

        if len(formatted_questions) == 0:
            abort(404)

        return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': len(formatted_questions),
          'categories': formatted_categories,
          'current_category': list(set([question['category'] for question in formatted_questions])),
        })

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
    
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selection)

            return jsonify({
              'success': True,
              'deleted': question_id,
              'questions': current_question,
              'total_questions': len(Question.query.all()),
            })
        except Exception:
            abort(422)

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
    
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)

        try:
            question = Question(question=new_question,
                                answer=new_answer,
                                category=new_category,
                                difficulty=new_difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
              'success': True,
              'created': question.id,
              'questions': current_questions,
              'total_questions': len(Question.query.all())
            })
        except Exception:
            abort(422)

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
    
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    @app.route('/questions_search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search = body.get('searchTerm', None)

        try:
            if search:
                questions = Question.query.order_by(Question.id).filter(
                  Question.question.ilike("%{}%".format(search))
                )

                current_questions = paginate_questions(request, questions)

                return jsonify({
                  'success': True,
                  'questions': current_questions,
                  'total_questions': len(questions),
                })
        except Exception:
          abort(400)

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
    
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/questions/<int:category_id>/questions')
    def questions_by_category(category_id):
        try:
            questions = Question.query.filter_by(category=str(category_id)).all()
            current_questions = paginate_questions(request, questions)
            
            return jsonify({
              'success': True,
              'questions': current_questions,
              'total_questions': len(questions),
            })
        except Exception:
          abort(422)

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
    
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        body = request.get_json()

        previous_questions = body['previous_questions']
        quiz_category = body['quiz_category']

        questions = None
        if quiz_category['type'] == "click":
            questions = Question.query.all()
        else:
            questions = Question.query.filter_by(category=quiz_category['id']).all()

        formatted_questions = [question.format() for question in questions]
        possible_questions = []

        for qu in formatted_questions:
            if qu['id'] not in previous_questions:
                possible_questions.append(qu)

        next_question = None
        if len(possible_questions) > 0:
            next_question = random.choice(possible_questions)

        return jsonify({
          'success': True,
          'question': next_question,
        })

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
          'success': False,
          'error': 400,
          'message': 'Bad request',
        }), 400

    @app.errorhandler(404)
    def bad_request(error):
      return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource not found',
      }), 404

    @app.errorhandler(422)
    def bad_request(error):
      return jsonify({
        'success': False,
        'error': 422,
        'message': 'Unprocessable',
      }), 422

    return app

