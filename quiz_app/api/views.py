from rest_framework import serializers
from rest_framework.views import APIView
from .seralizers import QuestionSeralizer, QuizSerializer, QuizListSeralizer
from quiz_app.models import Quizz, Question
from rest_framework.response import Response
from .helper import video_download, transcripts_Audio_to_Text, create_Quiz_with_GeminiAPI
from rest_framework import status
from pathlib import Path
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import generics,viewsets,filters,status
from django.shortcuts import get_object_or_404
from .permission import isOwnerFromTheQuiz
class CreateQuizView(APIView):
    serializer_class=QuizSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request):
        url = request.data.get('url')

        if url is None:
            Response({'detail': "url is missing"}, status=status.HTTP_400_BAD_REQUEST )

        audio_data = video_download(str(url))
        if audio_data:
            transcripted_text = transcripts_Audio_to_Text(audio_data)
        else:
            Response({"Download failed"}, status=status.HTTP_400_BAD_REQUEST)

        quiz_json = create_Quiz_with_GeminiAPI(transcripted_text)
        print(quiz_json)

        serializer = QuizSerializer(data=quiz_json)
        print(serializer)
        serializer.is_valid(raise_exception=True)
        quiz_instance = serializer.save(video_url=url, user=request.user)

        for q in quiz_json.get("questions", []):
            Question.objects.create(
                quizz=quiz_instance,
                question_title=q["question_title"],
                question_options=q["question_options"],
                answer=q["answer"]
            )
        serializer_with_questions = QuizSerializer(quiz_instance)

        return Response(serializer_with_questions.data,status=status.HTTP_201_CREATED)

class QuizListView(ListAPIView):
    serializer_class = QuizListSeralizer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user

        queryset = Quizz.objects.filter(user=user)
        serializer = QuizListSeralizer(queryset, many=True)
        return Response(serializer.data)
    
class QuizzDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = QuizListSeralizer    
    permission_classes = [IsAuthenticated, isOwnerFromTheQuiz]

 
    def get_object(self):
        pk = self.kwargs.get('pk')
        obj = get_object_or_404(Quizz, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj
    
    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        user = request.user
        obj = get_object_or_404(Quizz, pk=pk)
        self.perform_destroy(obj)
        return Response({"detail": "delete successfully"},status=status.HTTP_204_NO_CONTENT)