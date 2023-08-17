from django.urls import path

from .views import QuestionSelectView, QuestionCreateView, QuestionFavoriteView, QuestionUpdateDeleteView, \
    QuizCreateView, QuizDetailView, QuizUpdateView, QuizDeleteView

urlpatterns = [
    path('question/create/', QuestionCreateView.as_view(), name='question-create'),
    path('question/select/', QuestionSelectView.as_view(), name='question-select'),
    path('question/<int:pk>/', QuestionUpdateDeleteView.as_view(), name='question-update-delete'),
    path('question/<int:pk>/favorite/', QuestionFavoriteView.as_view(), name='question-favorite'),
    path('quiz/create/', QuizCreateView.as_view(), name='quiz-creation'),
    path('quiz/<str:quiz_unique_link>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quiz/<int:pk>/update/', QuizUpdateView.as_view(), name='quiz-update'),
    path('quiz/<int:pk>/delete/', QuizDeleteView.as_view(), name='quiz-delete'),
]
