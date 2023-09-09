import shortuuid
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
    class AnswerType(models.IntegerChoices):
        ONE_ANSWER = 0, 'One Answer'
        MULTIPLE_ANSWERS = 1, 'Multiple Answers'
        OPEN_ENDED = 2, 'Open-Ended'

    class DifficultyLevel(models.IntegerChoices):
        EASY = 0, 'Easy'
        MEDIUM = 1, 'Medium'
        HARD = 2, 'Hard'

    category = models.ForeignKey(Category, default=1, on_delete=models.DO_NOTHING)
    text = models.TextField(max_length=200)
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    answer_type = models.IntegerField(choices=AnswerType.choices, default=AnswerType.ONE_ANSWER)
    difficulty = models.IntegerField(choices=DifficultyLevel.choices, default=DifficultyLevel.EASY)
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
    time_limit = models.DurationField()
    unique_link = models.CharField(max_length=50, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.unique_link:
            self.unique_link = shortuuid.uuid()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')
        ordering = ['id']

    def __str__(self):
        return self.title


class QuestionScore(models.Model):
    """
        Model for storing scores of each question for specific quiz.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Quiz: {self.quiz.title} - Question: {self.question.id} - Score: {self.score}"


class Result(models.Model):
    """
        Model for storing submitted results along with score, time taken and feedback.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.PROTECT)
    score = models.FloatField(default=0)
    time_taken = models.DurationField()
    feedback = models.TextField(default='')
    submission_time = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'submission_time', 'quiz')

    def __str__(self):
        return f"User: {self.user.username} - Quiz: {self.quiz.title} - Date: {self.submission_time.isoformat()}"


class SubmittedAnswer(models.Model):
    """
        Model for storing each questions answer for submitted quiz result.
    """
    quiz_result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answers = models.ManyToManyField(Answer, related_name='selected_answers', blank=True)


class OpenEndedAnswer(models.Model):
    """
        Model for storing open-ended answers and their scores for quiz.
    """
    submitted_answer = models.OneToOneField(SubmittedAnswer, on_delete=models.CASCADE, related_name='open_ended_answer')
    answer_text = models.TextField(blank=True, null=True)
    score = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.answer_text
