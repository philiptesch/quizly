from rest_framework import serializers
from rest_framework.views import APIView
from .seralizers import QuestionSeralizer, QuizSerializer, QuizListSeralizer
from quiz_app.models import Quiz, Question
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
    """
    Create a quiz from a video URL.

    Permissions:
        - User must be authenticated.

    Behavior:
        - POST: 
            1. Receives a video URL.
            2. Downloads the video audio.
            3. Transcribes audio to text.
            4. Generates quiz data using Gemini API.
            5. Saves the quiz and related questions to the database.
            6. Returns the created quiz with its questions.
    """
    serializer_class=QuizSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request):
        url = request.data.get('url')

        if url is None:
             return Response({'detail': "url is missing"}, status=status.HTTP_400_BAD_REQUEST )

        if not url.startswith('https://www.youtube.com/watch?v='):
           return Response({'detail': "The entered URL is incorrect. The URL must begin with https://www.youtube.com/watch?v="}, status=status.HTTP_400_BAD_REQUEST )
    
        audio_data = video_download(str(url))
        if audio_data:
            transcripted_text = transcripts_Audio_to_Text(audio_data)
        else:
          return Response({"Download failed"}, status=status.HTTP_400_BAD_REQUEST)

        quiz_json = create_Quiz_with_GeminiAPI(transcripted_text)
        serializer = QuizSerializer(data=quiz_json)
        serializer.is_valid(raise_exception=True)
        quiz_instance = serializer.save(video_url=url, user=request.user)

        for q in quiz_json.get("questions", []):
            Question.objects.create(
                quizz=quiz_instance,
                question_title=q["question_title"],
                question_options=q["question_options"],
                answer=q["answer"])
        serializer_with_questions = QuizSerializer(quiz_instance)
        return Response(serializer_with_questions.data,status=status.HTTP_201_CREATED)

class QuizListView(ListAPIView):
    """
    List all quizzes created by the authenticated user.

    Permissions:
        - User must be authenticated.

    Behavior:
        - GET: Returns a list of quizzes that belong only to the current user.
    """
    serializer_class = QuizListSeralizer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user

        queryset = Quiz.objects.filter(user=user)
        serializer = QuizListSeralizer(queryset, many=True)
        return Response(serializer.data)
    
class QuizDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific quiz.

    Permissions:
        - User must be authenticated.
        - User must be the owner of the quiz.

    Behavior:
        - GET: Retrieve quiz details.
        - PUT/PATCH: Update quiz data.
        - DELETE: Delete the quiz.
    """

    serializer_class = QuizListSeralizer    
    permission_classes = [IsAuthenticated, isOwnerFromTheQuiz]

    def get_object(self):
        pk = self.kwargs.get('pk')
        obj = get_object_or_404(Quiz, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj
    
    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        user = request.user
        obj = get_object_or_404(Quiz, pk=pk)
        self.perform_destroy(obj)
        return Response({"detail": "delete successfully"},status=status.HTTP_204_NO_CONTENT)