from django.db import models
from auth_app.models import User
# Create your models here.

class Quiz(models.Model):
    """
    Model representing a generated quiz.

    Fields:
        - title: Title of the quiz.
        - description: Short summary of the quiz content.
        - created_at: Timestamp when the quiz was created.
        - updated_at: Timestamp when the quiz was last updated.
        - video_url: Source video URL used to generate the quiz (optional).
        - user: Reference to the user who created the quiz.

    Relationships:
        - One user can have multiple quizzes.
        - One quiz can have multiple related questions.
    """

    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video_url = models.URLField(blank=True,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')


    def __str__(self):
        return f"Quizz {self.id}, {self.title}  by {self.user.username}"
    

class Question(models.Model):
    """
    Model representing a single quiz question.

    Fields:
        - quizz: Reference to the parent quiz.
        - question_title: The question text.
        - question_options: List of possible answer options (stored as JSON).
        - answer: The correct answer (must match one of the options).
        - created_at: Timestamp when the question was created.
        - updated_at: Timestamp when the question was last updated.

    Relationships:
        - Each question belongs to one quiz.
        - A quiz can contain multiple questions.
    """
    
    quizz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_title = models.CharField(max_length=200)
    question_options = models.JSONField()
    answer=models.CharField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Quizz  {self.quizz.title} - {self.question_title}"