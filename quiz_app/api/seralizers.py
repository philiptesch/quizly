from django.contrib.auth.models import User
from rest_framework import serializers
from quiz_app.models import Quiz, Question


class QuestionSeralizer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        Validate that the provided answer exists within the given question options.

        Validation Steps:
        1. Retrieve the list of possible answer options from the request data.
        2. Retrieve the selected correct answer.
        3. Check whether the answer is included in the options list.
        4. Raise a validation error if the answer is not part of the options.
        5. Return the validated data if everything is correct.
        """

        question_options = attrs.get("question_options")
        answer = attrs.get("answer")

        if answer not in question_options:
            raise serializers.ValidationError("Answer must be one of the question options")
        return attrs
    
class QuestionListSeralizer(serializers.ModelSerializer):



    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer']


    def validate(self, attrs):
        """
        Validate that the provided answer exists within the given question options.

        Validation Steps:
        1. Retrieve the list of possible answer options from the request data.
        2. Retrieve the selected correct answer.
        3. Ensure the answer is one of the available options.
        4. Raise a validation error if the validation fails.
        5. Return the validated data if everything is correct.
        """

        question_options = attrs.get("question_options")
        answer = attrs.get("answer")

        if answer not in question_options:
                raise serializers.ValidationError("Answer must be one of the question options")
        return attrs


class QuizSerializer(serializers.ModelSerializer):
 
    id = serializers.IntegerField(read_only=True)
    questions = QuestionSeralizer(many=True,read_only=True)

    class Meta:
        model=Quiz
        fields=['id','title','description','created_at','updated_at','video_url','questions']
    read_only_fields = ['title','description','created_at','updated_at']



class QuizListSeralizer(serializers.ModelSerializer):
   
    id = serializers.IntegerField(read_only=True)
    questions = QuestionListSeralizer(many=True,read_only=True)

    class Meta:
        model=Quiz
        fields=['id','title','description','created_at','updated_at','video_url','questions']
    read_only_fields = ['title','description','created_at','updated_at']