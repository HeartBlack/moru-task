from app.models.models import *


def filter_questions_by_text(query, question_text):
    questions = Question.query.filter(Question.question_text.ilike(f"%{question_text}%")).all()
    question_ids = [q.id for q in questions]
    return query.filter(Quiz.question_id.in_(question_ids))


def filter_quizzes_by_answer(query, answer_text):
    answers = Answer.query.filter(Answer.answer.ilike(f"%{answer_text}%")).all()
    answer_ids = [a.id for a in answers]
    return query.filter(Quiz.answer_id.in_(answer_ids))


def filter_quizzes_by_category(query, category_name):
    categories = Category.query.filter(Category.name.ilike(f"%{category_name}%")).all()
    category_ids = [c.id for c in categories]

    question_ids = Question.query.filter(Question.category_id.in_(category_ids)).all()
    q_ids = [q.id for q in question_ids]

    return query.filter(Quiz.question_id.in_(q_ids))
