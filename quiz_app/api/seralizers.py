from django.contrib.auth.models import User
from rest_framework import serializers
from quiz_app.models import Quizz, Question


class QuestionSeralizer(serializers.ModelSerializer):

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
    id = serializers.IntegerField(read_only=True)
    questions = QuestionSeralizer(many=True,read_only=True)

    class Meta:
        model=Quizz
        fields=['id','title','description','created_at','updated_at','video_url','questions']
    read_only_fields = ['title','description','created_at','updated_at']



class QuizListSeralizer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    questions = QuestionListSeralizer(many=True,read_only=True)

    class Meta:
        model=Quizz
        fields=['id','title','description','created_at','updated_at','video_url','questions']
    read_only_fields = ['title','description','created_at','updated_at']