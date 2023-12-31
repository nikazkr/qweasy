from django.urls import path

from .views import QuestionSelectView, QuestionCreateView, QuestionFavoriteView, ResultSubmitView, QuestionDetailView, \
    QuizCreateView, QuizDetailView, QuizUpdateDeleteView, QuizListView, SendQuizEmailView, \
    UserResultListView, UserResultDetailView, OpenEndedReview, CategoryListCreateView, CategoryDetailView

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('question/create/', QuestionCreateView.as_view(), name='question-create'),
    path('question/', QuestionSelectView.as_view(), name='question-select'),
    path('question/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('question/<int:pk>/favorite/', QuestionFavoriteView.as_view(), name='question-favorite'),
    path('quiz/create/', QuizCreateView.as_view(), name='quiz-create'),
    path('quiz/<str:quiz_unique_link>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quiz/<int:pk>', QuizUpdateDeleteView.as_view(), name='quiz-update-delete'),
    path('quiz/', QuizListView.as_view(), name='quiz-list'),
    path('quiz/send-email', SendQuizEmailView.as_view(), name='send-quiz-email'),
    path('quiz/submit', ResultSubmitView.as_view(), name='quiz-submit'),
    path('quiz/open-ended-review', OpenEndedReview.as_view(), name='open-ended-review'),
    path('quiz/user-results/<int:user_id>/', UserResultListView.as_view(), name='user-results'),
    path('quiz/user-result/<int:id>/', UserResultDetailView.as_view(), name='user-result-detail'),
]
