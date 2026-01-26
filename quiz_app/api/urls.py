from django.urls import path
from .views import CreateQuizView, QuizListView, QuizzDetailView


urlpatterns = [
    path('createQuiz/', CreateQuizView.as_view(), name='createQuiz'),
    path('quizzes/', QuizListView.as_view(), name='listquizzes'),
    path('quizzes/<int:pk>/', QuizzDetailView.as_view(), name='listquizzes'),
]