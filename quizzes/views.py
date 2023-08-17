from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.permissions import IsMasterOrReadOnly
from .models import Question, Favorite, Score, Quiz
# from .models import Quiz
from .serializers import QuestionSelectSerializer, QuestionSerializer, QuizSerializer


# from .serializers import QuizCreationSerializer


class QuestionCreateView(APIView):
    permission_classes = [IsAuthenticated, IsMasterOrReadOnly]

    @extend_schema(
        request=QuestionSerializer,  # Replace with your Question serializer
        responses={status.HTTP_201_CREATED: QuestionSerializer},
        examples=[
            OpenApiExample(
                'Example',
                value={
                    'category': 1,
                    'text': 'What is your favorite color?',
                    'type': 2,
                    'difficulty': 1,
                    'answers': [
                        {'text': 'Blue', 'is_correct': True},
                        {'text': 'Red', 'is_correct': False},
                    ]
                },

            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = QuestionSerializer(data=request.data)

        if serializer.is_valid():
            question = serializer.save()
            return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionSelectView(APIView):
    permission_classes = [IsAuthenticated, IsMasterOrReadOnly]

    @extend_schema(
        request=QuestionSelectSerializer,  # Define your request serializer here
        # responses={status.HTTP_200_OK: None}  # Define your response serializers here
    )
    def post(self, request, *args, **kwargs):
        serializer = QuestionSelectSerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.validated_data.get('category')
            difficulty = serializer.validated_data.get('difficulty')
            type = serializer.validated_data.get('type')
            quantity = serializer.validated_data.get('quantity')

            # Apply filters based on the inputs
            questions = Question.objects.all()
            if category:
                questions = questions.filter(category=category)
            if type:
                questions = questions.filter(type=type)
            if difficulty:
                questions = questions.filter(difficulty=difficulty)

            # Get the specified quantity of questions
            selected_questions = questions[:quantity]
            question_serializer = QuestionSerializer(selected_questions, many=True)
            return Response({'questions': question_serializer.data})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsMasterOrReadOnly]

    @extend_schema(
        request=QuestionSerializer,  # Replace with your Question serializer
        responses={status.HTTP_200_OK: QuestionSerializer},
    )
    def put(self, request, pk, *args, **kwargs):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={status.HTTP_204_NO_CONTENT: None},
    )
    def delete(self, request, pk, *args, **kwargs):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class QuestionFavoriteView(APIView):
    permission_classes = [IsAuthenticated, IsMasterOrReadOnly]

    def post(self, request, pk):
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        favorite, created = Favorite.objects.get_or_create(user=user, question=question)

        if not created:
            favorite.delete()  # Unfavorite if already marked as favorite
            return Response({"message": "Question removed from favorites"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Question marked as favorite"}, status=status.HTTP_200_OK)


class QuizCreateView(generics.CreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

# class QuizCreationView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = QuizCreationSerializer(data=request.data)
#         if serializer.is_valid():
#             quiz_name = serializer.validated_data.get('quiz_name')
#             quiz_time = serializer.validated_data.get('quiz_time')
#             favorited_questions = serializer.validated_data.get('favorited_questions', [])
#
#             # Create a new quiz instance
#             quiz = Quiz.objects.create(name=quiz_name, time=quiz_time)
#             quiz.questions.set(favorited_questions)
#
#             # Serialize the created quiz
#             quiz_serializer = QuizCreationSerializer(quiz)
#
#             return Response({'quiz': quiz_serializer.data})
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
