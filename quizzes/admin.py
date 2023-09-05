from django.contrib import admin

from quizzes.models import (
    Category,
    Question,
    Answer,
    Quiz,
    QuestionScore
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


class QuestionScoreInlineAdmin(admin.TabularInline):
    model = QuestionScore


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title']
    inlines = [QuestionScoreInlineAdmin]


class AnswerInlineAdmin(admin.TabularInline):
    model = Answer
    list_display = ['text', 'is_correct']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text']
    inlines = [AnswerInlineAdmin]
