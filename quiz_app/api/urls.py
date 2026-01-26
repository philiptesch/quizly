from django.urls import path
from .views import CreateQuizView, QuizListView, QuizDetailView


urlpatterns = [
    path('createQuiz/', CreateQuizView.as_view(), name='createQuiz'),
    path('quizzes/', QuizListView.as_view(), name='listquizzes'),
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='listquizzes'),
]