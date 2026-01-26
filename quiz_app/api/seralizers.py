from django.contrib.auth.models import User
from rest_framework import serializers
from quiz_app.models import Quiz, Question


class QuestionSeralizer(serializers.ModelSerializer):
    """
    Serializer for detailed Question representation.

    Fields:
        - id: Unique identifier (read-only)
        - question_title: The text of the question
        - question_options: List of possible answer options
        - answer: The correct answer (must be one of the options)
        - created_at: Timestamp when the question was created
        - updated_at: Timestamp when the question was last updated

    Validation:
        - Ensures that the provided answer exists in the question_options list.
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']

    def validate(self, attrs):
        question_options = attrs.get("question_options")
        answer = attrs.get("answer")
        print(answer)

        if answer not in question_options:
            raise serializers.ValidationError("Answer must be one of the question options")
        return attrs
    
class QuestionListSeralizer(serializers.ModelSerializer):
    """
    Serializer for listing Question objects in a simplified form.

    Fields:
        - id: Unique identifier (read-only)
        - question_title: The text of the question
        - question_options: List of possible answer options
        - answer: The correct answer

    Validation:
        - Ensures that the provided answer exists in the question_options list.
    """

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer']

        def validate(self, attrs):
            question_options = attrs.get("question_options")
            answer = attrs.get("answer")
            print(answer)

            if answer not in question_options:
                raise serializers.ValidationError("Answer must be one of the question options")
            return attrs


class QuizSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Quiz representation.

    Fields:
        - id: Unique identifier (read-only)
        - title: Title of the quiz (read-only, auto-generated)
        - description: Quiz description (read-only, auto-generated)
        - created_at: Creation timestamp (read-only)
        - updated_at: Last update timestamp (read-only)
        - video_url: Source video URL used to generate the quiz
        - questions: Nested list of full Question objects related to the quiz

    Behavior:
        - Questions are included as nested read-only objects.
        - Title and description are not editable via API.
    """
    id = serializers.IntegerField(read_only=True)
    questions = QuestionSeralizer(many=True,read_only=True)

    class Meta:
        model=Quiz
        fields=['id','title','description','created_at','updated_at','video_url','questions']
    read_only_fields = ['title','description','created_at','updated_at']



class QuizListSeralizer(serializers.ModelSerializer):
    """
    Serializer for listing quizzes in a lightweight form.

    Fields:
        - id: Unique identifier (read-only)
        - title: Title of the quiz
        - description: Quiz description
        - created_at: Creation timestamp
        - updated_at: Last update timestamp
        - video_url: Source video URL
        - questions: Nested simplified question list

    Behavior:
        - Uses a simplified Question serializer for listing efficiency.
        - Title and description are read-only.
    """

    id = serializers.IntegerField(read_only=True)
    questions = QuestionListSeralizer(many=True,read_only=True)

    class Meta:
        model=Quiz
        fields=['id','title','description','created_at','updated_at','video_url','questions']
    read_only_fields = ['title','description','created_at','updated_at']