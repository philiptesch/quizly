from rest_framework.views import APIView
from .seralizers import  QuizSerializer, QuizListSeralizer
from quiz_app.models import Quiz, Question
from rest_framework.response import Response
from .helper import video_download, transcripts_Audio_to_Text, create_Quiz_with_GeminiAPI, check_url_format
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import  ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .permission import isOwnerFromTheQuiz
from rest_framework.exceptions import ValidationError

class CreateQuizView(APIView):
    """
    API view to create a quiz from a YouTube video URL.

    Permissions:
        - User must be authenticated.
    """
    serializer_class=QuizSerializer
    permission_classes = [IsAuthenticated]


    def post(self, request):
        """
        Handle POST request to create a quiz:
        
        Steps:
            1. Validate the provided YouTube URL.
            2. Download the video's audio.
            3. Transcribe audio to text.
            4. Generate quiz data using the Gemini API.
            5. Save the quiz and related questions to the database.
            6. Return the created quiz along with its questions.

        Request Data:
            - url (str): YouTube video URL (must start with 'https://www.youtube.com/watch?v=')

        Responses:
            - 201 Created: Quiz successfully created with questions.
            - 400 Bad Request: URL missing, invalid URL, or download/transcription failed.
            - 401 UNAUTHORIZED: only a registed user is allowed to create Quizz
        """
        url = request.data.get('url')
        check_url_format(str(url))

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
    API view to list all quizzes created by the authenticated user.
    Only quizzes that belong to the current user are returned.
    """
    serializer_class = QuizListSeralizer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Handle GET request to retrieve a list of quizzes:

        1. Get the currently authenticated user.
        2. Filter quizzes so only those created by this user are included.
        3. Serialize the filtered quiz queryset.
        4. Return the serialized quiz data as a response.
        """
        user = request.user
        queryset = Quiz.objects.filter(user=user)
        serializer = QuizListSeralizer(queryset, many=True)
        return Response(serializer.data)
    
class QuizDetailView(RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete a specific quiz.
    Access is restricted to the authenticated owner of the quiz.
    """

    serializer_class = QuizListSeralizer    
    permission_classes = [IsAuthenticated, isOwnerFromTheQuiz]

    def get_object(self):
        """
        Retrieve the quiz object based on the provided primary key (pk):

        1. Extract the quiz ID from the URL parameters.
        2. Attempt to fetch the quiz from the database.
        3. Check if the requesting user has permission to access this quiz.
        4. Return the quiz object if all checks pass.
        """

        pk = self.kwargs.get('pk')
        obj = get_object_or_404(Quiz, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj
    
    def destroy(self, request, *args, **kwargs):
        """
        Handle DELETE request to remove a quiz:

        1. Extract the quiz ID from the URL parameters.
        2. Retrieve the quiz object from the database.
        3. Delete the quiz instance.
        4. Return a success message confirming deletion.
        """

        pk = self.kwargs.get('pk')
        user = request.user
        obj = get_object_or_404(Quiz, pk=pk)
        self.perform_destroy(obj)
        return Response({"detail": "delete successfully"},status=status.HTTP_204_NO_CONTENT)