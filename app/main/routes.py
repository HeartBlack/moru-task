from datetime import datetime

from flask import jsonify, request

from app.auth.roles import admin_required
from app.extensions import bcrypt, db
from app.filter import (
    filter_questions_by_text,
    filter_quizzes_by_answer,
    filter_quizzes_by_category,
)
from app.jwt_set_up.jwt_token import make_access_token, token_required
from app.main import bp
from app.models.models import Answer, Category, Question, Quiz, Role, Score, User, UserResponse


@bp.route("/")
def index():
    return {
        "message": "Index route accessed successfully",
    }


@bp.route("/register/", methods=["POST"])
def register_user():
    username = request.json.get("username")
    password = request.json.get("password")
    user_type = request.json.get("user_type")
    print("user_type", user_type)

    role = None  # Initialize role variable

    if user_type is not None:
        if user_type == Role.ADMIN.value:
            role = Role.ADMIN
        else:
            role = Role.NORMAL
    else:
        role = Role.NORMAL

    print("role", role)

    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400

    try:
        existing_user = User.query.filter_by(username=username).first()
    except:
        existing_user = None

    if existing_user:
        return jsonify({"message": "Username already exists."}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(username=username, password=hashed_password, user_type=role)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully."}), 201


@bp.route("/login/", methods=["POST"])
def login_user():
    username = request.json.get("username")
    password = request.json.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid username or password."}), 401

    access_token = make_access_token(user)

    return jsonify({"access_token": access_token}), 200


######### Category Endpoints ##########


@bp.route("/categories/", methods=["GET"])
@token_required
def get_categories():
    # try:
    search = request.args.get("search")
    if search:
        categories = Category.query.filter(Category.name.ilike(f"%{search}%")).all()
    else:
        categories = Category.query.all()

    category_list = []
    for category in categories:
        category_data = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
        }
        category_list.append(category_data)

    if category_list:
        return jsonify({"categories": category_list}), 200
    else:
        return jsonify({"message": "No categories found"}), 404

    # except Exception as e:
    #     return jsonify({"message": "An error occurred", "error": str(e)}), 500


@bp.route("/categories/", methods=["POST"])
@token_required
@admin_required
def create_category():
    name = request.json.get("name")
    description = request.json.get("description")
    if name and description:
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        data = {"id": category.id, "name": name, "description": description}
        return jsonify({"message": data}), 200
    return jsonify({"message": "Please give name and description"}), 400


@bp.route("/categories/<id>/", methods=["PUT"])
@token_required
@admin_required
def update_category(id):
    categories = Category.query.get(id)
    name = request.json.get("name")
    description = request.json.get("description")
    if name and description:
        categories.name = name
        categories.description = description
        db.session.commit()
        return jsonify({"message": "Category updated successfully"}), 200
    return jsonify({"message": "Please give name and description"}), 400


@bp.route("/categories/<id>/", methods=["DELETE"])
@token_required
@admin_required
def delete_category(id):
    categories = Category.query.get(id)
    db.session.delete(categories)
    db.session.commit()
    return jsonify({"message": "DELETE request processed successfully"}), 200


############### Questions Endpoint ##################3


@bp.route("/questions/", methods=["GET"])
@token_required
def get_questions():
    try:
        search = request.args.get("search")
        if search:
            questions = Question.query.filter(Question.question_text.ilike(f"%{search}%")).all()
        else:
            questions = Question.query.all()

        question_list = []
        for question in questions:
            question_data = {
                "id": question.id,
                "question": question.question_text,
                "category": question.category_id,
            }
            question_list.append(question_data)

        if question_list:
            return jsonify({"questions": question_list}), 200
        else:
            return jsonify({"message": "No questions found"}), 404

    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@bp.route("/questions/", methods=["POST"])
@token_required
@admin_required
def create_question():
    question = request.json.get("question")
    category_id = int(request.json.get("category_id"))
    if question and category_id:
        question_data = Question(category_id=category_id, question_text=question)
        db.session.add(question_data)
        db.session.commit()
        data = {"id": question_data.id, "category": category_id, "question": question}
        return jsonify({"message": data}), 200
    return jsonify({"message": "Please give question and category_id"}), 400


@bp.route("/questions/<id>/", methods=["PUT"])
@token_required
@admin_required
def update_question(id):
    question = Question.query.get(id)
    question_text = request.json.get("question")
    category_id = int(request.json.get("category_id"))

    if question:
        question.question_text = question_text
        question.category_id = int(category_id)
        db.session.commit()
        data = {"id": question.id, "category": category_id, "question": question_text}
        return jsonify({"message": data}), 200
    return jsonify({"message": "Please give name and description"}), 400


@bp.route("/questions/<id>/", methods=["DELETE"])
@token_required
@admin_required
def delete_questions(id):
    question = Question.query.get(id)
    db.session.delete(question)
    db.session.commit()
    return jsonify({"message": "DELETE request processed successfully"}), 200


####### Answer Endpoints ######


@bp.route("/answers/", methods=["GET"])
@token_required
def get_answers():
    try:
        search = request.args.get("search")
        if search:
            answers = Answer.query.filter(Answer.answer.ilike(f"%{search}%")).all()
        else:
            answers = Answer.query.all()

        answers_list = []
        for answer in answers:
            answers_data = {"id": answer.id, "answer": answer.answer}
            answers_list.append(answers_data)

        if answers_list:
            return jsonify({"answers": answers_list}), 200
        else:
            return jsonify({"message": "No answers found"}), 404

    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@bp.route("/answers/", methods=["POST"])
@token_required
@admin_required
def create_answer():
    answer = request.json.get("answer")
    if answer:
        answer_data = Answer(answer=answer)
        db.session.add(answer_data)
        db.session.commit()
        data = {"id": answer_data.id, "answer": answer}
        return jsonify({"message": data}), 200
    return jsonify({"message": "Please give name and description"}), 400


@bp.route("/answers/<id>/", methods=["PUT"])
@token_required
@admin_required
def update_answer(id):
    answer = Answer.query.get(id)
    answer_text = request.json.get("answer")

    if answer:
        answer.answer = answer_text
        db.session.commit()
        data = {"id": answer.id, "answer": answer_text}
        return jsonify({"message": data}), 200
    return jsonify({"message": "Please provide valid id"}), 400


@bp.route("/answers/<id>/", methods=["DELETE"])
@token_required
@admin_required
def delete_answers(id):
    answer = Answer.query.get(id)
    if answer:
        db.session.delete(answer)
        db.session.commit()
        return jsonify({"message": "DELETE request processed successfully"}), 200
    return jsonify({"message": "Please provide valid id"})


#### Quizz data ###


@bp.route("/quizs/", methods=["GET"])
@token_required
def get_quiz():
    try:
        question = request.args.get("question")
        answer = request.args.get("answer")
        category = request.args.get("category")
        user_id = request.current_user.get("user_id")

        query = Quiz.query.filter_by(user_id=int(user_id))

        if question:
            query = filter_questions_by_text(query, question)

        if answer:
            query = filter_quizzes_by_answer(query, answer)

        if category:
            query = filter_quizzes_by_category(query, category)

        quizs = query.all()

        quizs_list = []
        for quiz in quizs:
            quizs_data = {
                "id": quiz.id,
                "question": {
                    "question_id": quiz.question_id,
                    "question_text": quiz.get_question_text(),
                },
                "answer": {"answer_id": quiz.answer_id, "answer_text": quiz.get_answer_text()},
                "category": quiz.get_category(),
                "score": quiz.score,
                "user_id": quiz.user_id,
                "start_time": quiz.start_time,
                "end_time": quiz.end_time,
            }
            quizs_list.append(quizs_data)

        if quizs_list:
            return jsonify({"data": quizs_list}), 200
        else:
            return jsonify({"message": "No Quiz found"}), 404

    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@bp.route("/quizs/<id>/", methods=["PUT"])
@token_required
@admin_required
def update_quiz(id):
    question_id = request.json.get("question_id")
    answer_id = request.json.get("answer_id")
    score = request.json.get("score")
    user_id = request.current_user.get("user_id")

    question = Question.query.filter_by(id=int(question_id)).first()
    answer = Answer.query.filter_by(id=int(answer_id)).first()
    user = User.query.filter_by(id=int(user_id)).first()

    start_time = datetime.now()
    end_time = datetime.now()
    if user.Role.ADMIN != "ADMIN":
        return jsonify({"message": "You do not have permission to perform this action"}), 401

    if question and answer and user and score:
        quiz = Quiz(
            question_id=question.id,
            answer_id=answer.id,
            user_id=user.id,
            score=score,
            start_time=start_time,
            end_time=end_time,
        )
        db.session.add(quiz)
        db.session.commit()
        data = {
            "id": answer.id,
            "question_id": question_id,
            "answer_id": answer_id,
            "user_id": user_id,
            "score": score,
        }
        return jsonify({"message": data}), 200

    return jsonify({"message": "please provide valid Data"}), 400


@bp.route("/quizs/<id>/", methods=["DELETE"])
@token_required
@admin_required
def delete_quizs(id):
    quiz = Quiz.query.get(id)
    if quiz:
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({"message": "DELETE request processed successfully"}), 200
    return jsonify({"message": "Please provide valid id"})


@bp.route("/user-response/", methods=["POST"])
@token_required
def create_user_response():
    user_id = request.current_user.get("user_id")
    user = User.query.filter_by(id=user_id).first()
    question_id = request.json.get("question_id")
    answer_id = request.json.get("answer_id")

    if user:
        if question_id and answer_id:
            question = Question.query.filter_by(id=int(question_id)).first()
            try:
                quiz = Quiz.query.filter_by(question_id=question.id).first()

                if question and quiz:
                    if quiz.answer_id == int(answer_id):
                        is_true = True
                        score = quiz.score
                    else:
                        is_true = False
                        score = 0

                    if quiz.user_id != user.id:
                        return jsonify({"message": "You cannot perform this action"}), 400
                    data_exist = UserResponse.query.filter_by(question_id=question.id).first()
                    if data_exist:
                        data_exist.question_id = question.id
                        data_exist.answer_id = int(answer_id)
                        data_exist.score = score
                        data_exist.is_true = is_true
                        db.session.commit()
                        return jsonify({"data": "Your answer is submitted", "status": is_true}), 200

                    user_response = UserResponse(
                        question_id=question.id,
                        answer_id=int(answer_id),
                        score=score,
                        is_true=is_true,
                        user_id=user.id,
                    )
                    db.session.add(user_response)
                    db.session.commit()

                    score_exist = Score.query.filter_by(user_id=user.id, quiz_id=quiz.id).first()
                    if score_exist:
                        score_exist.score = score
                        db.session.commit()
                    user_score = Score(user_id=user.id, quiz_id=quiz.id, score=score)
                    db.session.add(user_score)
                    db.session.commit()

                    return jsonify({"data": "Your answer is submitted", "status": is_true}), 200
            except Exception as e:
                return jsonify({"data": str(e)}), 400
    return jsonify({"status": "You dont have permission to access this question"}), 400


@bp.route("/user-response/", methods=["GET"])
@token_required
def get_user_respone():
    user_id = request.current_user.get("user_id")
    user = User.query.filter_by(id=user_id).first()
    all_answers = UserResponse.query.filter_by(user_id=user.id).all()

    answer_list = []
    for answers in all_answers:
        data = {
            "id": answers.id,
            "question_id": answers.question_id,
            "answer_id": answers.answer_id,
            "score": answers.score,
            "is_true": answers.is_true,
        }
        answer_list.append(data)
    return jsonify({"data": answer_list}), 200


@bp.route("/user-score-summery/", methods=["GET"])
@token_required
def get_summery():
    user_id = request.current_user.get("user_id")
    user = User.query.filter_by(id=user_id).first()
    quiz_id = request.args.get("quiz_id")
    if user and quiz_id:
        user_status = Score.query.filter_by(user_id=user.id, quiz_id=int(quiz_id)).all()
        total_count = 0
        for score in user_status:
            total_count += score.score
        if total_count > 0:
            return jsonify({"data": total_count, "user": user.username}), 200
        else:
            return jsonify({"data": []}), 200

    return jsonify({"data": "You cant not perform this action"}), 400
