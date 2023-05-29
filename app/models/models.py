from enum import Enum

from sqlalchemy.orm import joinedload

from app.extensions import bcrypt, db


class Role(Enum):
    ADMIN = "admin"
    NORMAL = "normal"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.Enum(Role, name="role"), nullable=True)

    def __init__(self, username, password, user_type):
        self.username = username
        self.password = password
        self.user_type = user_type

    def check_password(self, hash_password):
        return bcrypt.check_password_hash(self.password, hash_password)


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    question_text = db.Column(db.String(255), nullable=False)
    category = db.relationship("Category", backref=db.backref("questions", lazy=True))


class Answer(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer, primary_key=True)
    answer = db.Column(db.String(100), nullable=False)


class Quiz(db.Model):
    __tablename__ = "quizzes"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey("answers.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)

    question = db.relationship("Question", backref="quizzes", lazy=True)
    answer = db.relationship("Answer", backref="quizzes", lazy=True)
    user = db.relationship("User", backref="quizzes", lazy=True)

    def get_question_text(self):
        return self.question.question_text

    def get_answer_text(self):
        return self.answer.answer

    def get_category(self):
        try:
            category = Category.query.join(Question).filter(Question.id == self.question_id).first()
        except:
            category = None
        if category:
            return {"id": category.id, "category": category.name}

        return None

    @classmethod
    def eager_load_question_answer(cls, quiz_id):
        return cls.query.options(joinedload(cls.question), joinedload(cls.answer)).get(quiz_id)


class UserResponse(db.Model):
    __tablename__ = "user_responses"
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey("answers.id"), nullable=False)
    is_true = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    question = db.relationship("Question", backref=db.backref("user_responses", lazy=True))
    user = db.relationship("User", backref=db.backref("user_responses", lazy=True))
    answer = db.relationship("Answer", backref=db.backref("user_responses", lazy=True))


class Score(db.Model):
    __tablename__ = "scores"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quizzes.id"), nullable=False)
    score = db.Column(db.Float, nullable=False)

    user = db.relationship("User", backref=db.backref("scores", lazy=True))
    quiz = db.relationship("Quiz", backref=db.backref("scores", lazy=True))
