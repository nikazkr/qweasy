from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = _('Categories')
        ordering = ['name']

    def __str__(self):
        return self.name


class Question(models.Model):
    TYPE = (
        (0, 'One Answer'),
        (1, 'Multiple Answers'),
        (2, 'Open-Ended'),
    )
    LEVEL = (
        (0, 'Easy'),
        (1, 'Medium'),
        (2, 'Hard'),
    )
    category = models.ForeignKey(Category, default=1, on_delete=models.DO_NOTHING)
    text = models.TextField(max_length=200)
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    answer_type = models.IntegerField(choices=TYPE, default=0)
    difficulty = models.IntegerField(choices=LEVEL, default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='answer_images/', blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text or "No answer specified"


class Favorite(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')


class Quiz(models.Model):
    title = models.CharField(max_length=100)
    questions = models.ManyToManyField(Question, related_name='quiz')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    time_limit = models.IntegerField(default=0)  # in munutes
    unique_link = models.CharField(max_length=50, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')
        ordering = ['id']

    def __str__(self):
        return self.title


class QuestionScore(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Quiz: {self.quiz.title} - Question: {self.question.id} - Score: {self.score}"


class Result(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    score = models.PositiveIntegerField(default=0)
    time_taken = models.IntegerField(default=0)  # in minutes
    submission_time = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'submission_time', 'quiz')

    def __str__(self):
        return f"User: {self.user.username} - Quiz: {self.quiz.title} - Date: {self.submission_time.isoformat()}"


class UserAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    quiz_result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='answers')
    selected_answers = models.ManyToManyField(Answer, related_name='selected_answers', blank=True)
    open_ended_answer = models.TextField(blank=True, null=True)
    reviewed = models.BooleanField(default=False)

# class QuestionFeedback(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     like = models.BooleanField()
#
#     def __str__(self):
#         return f"{self.user.first_name} - Question: {self.question.text} - Like: {self.like}"


# class QuizFeedback(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
#     rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
#     comment = models.TextField(blank=True)
#
#     def __str__(self):
#         return f"{self.user.first_name} - Quiz: {self.quiz.name} - Rating: {self.rating}"
