from quizzes.models import Answer, QuestionScore


def calculate_score(quiz, user_answers):
    total_score = 0
    total_max_score = 0

    for answer_data in user_answers:
        question_total_score = 0
        question = answer_data['question']
        answer_type = answer_data['answer_type']

        if answer_type in [0, 1]:
            selected_answers = answer_data['selected_answers']
            correct_answer_ids = Answer.objects.filter(question=question, is_correct=True).values_list('id', flat=True)
            user_selected_ids = [answer.id for answer in selected_answers]
            correct_selected_ids = set(correct_answer_ids) & set(user_selected_ids)
            incorrect_selected_ids = set(user_selected_ids) - set(correct_answer_ids)

            question_max_score = QuestionScore.objects.get(quiz=quiz, question=question).score
            total_max_score += question_max_score
            correct_answer_count = len(correct_selected_ids)
            incorrect_answer_count = len(incorrect_selected_ids)

            if correct_answer_count > 0:
                partial_score = (correct_answer_count / len(correct_answer_ids)) * question_max_score
                question_total_score += partial_score

            if incorrect_answer_count > 0:
                question_total_score -= (0.5 * incorrect_answer_count * question_max_score)
                question_total_score = max(question_total_score, 0)

            if question_total_score > 0:
                total_score += question_total_score

    return {'total_score': total_score, 'total_max_score': total_max_score}
