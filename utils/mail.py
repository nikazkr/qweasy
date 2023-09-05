import time

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(serializer='json', name="send_mail")
def send_quiz_link_to_students(recipient_emails, quiz_unique_link):
    complete_quiz_link = f'https://odesmenamdvilidomeini.com/quiz/{quiz_unique_link}'
    subject = 'Quiz Link'
    message = f'Hello,\n\nHere is your quiz link:\n\n {complete_quiz_link}\n\nBest regards!'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = recipient_emails

    send_mail(subject, message, from_email, recipient_list)
