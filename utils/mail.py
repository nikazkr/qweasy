from django.conf import settings
from django.core.mail import send_mail


def send_quiz_link_to_student(student_email, quiz_unique_link):
    complete_quiz_link = f'{settings.FRONTEND_BASE_URL}/quiz/{quiz_unique_link}'

    subject = 'Quiz Link'
    message = f'Hello,\n\nHere is your quiz link:\n\n {complete_quiz_link}\n\nBest regards!'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [student_email]

    send_mail(subject, message, from_email, recipient_list)
