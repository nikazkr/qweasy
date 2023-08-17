from django.urls import path

from .views import QuestionSelectView, QuestionCreateView, QuestionFavoriteView, QuestionUpdateDeleteView, \
    QuizCreateView

urlpatterns = [
    path('create/', QuestionCreateView.as_view(), name='question-create'),
    path('select/', QuestionSelectView.as_view(), name='question-select'),
    path('<int:pk>/', QuestionUpdateDeleteView.as_view(), name='question-update-delete'),
    path('<int:pk>/favorite/', QuestionFavoriteView.as_view(), name='question-favorite'),
    path('create-quiz/', QuizCreateView.as_view(), name='quiz-creation'),
]
