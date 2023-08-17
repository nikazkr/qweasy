from django.contrib import admin

from quizzes.models import (
    Category,
    Question,
    Answer,
    Quiz
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title']


class AnswerInlineAdmin(admin.TabularInline):
    model = Answer
    list_display = ['text', 'is_correct']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text']
    inlines = [AnswerInlineAdmin]
