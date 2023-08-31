from django.db import transaction
from django.http import Http404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser
from utils.mail import send_quiz_link_to_students
from utils.permissions import IsExaminer
from .models import Question, Favorite, Quiz, Result, SubmittedAnswer
from .serializers import QuestionSerializer, QuizDetailSerializer, \
    ResultSubmitSerializer, ResultWithAnswersSerializer, QuizEmailSendSerializer, QuizCreateSerializer


class QuestionCreateView(APIView):
    """
    API view for creating a new question.

    Permissions:
        - User must be authenticated.
        - User must have examiner privileges.

    Args:
        request (HttpRequest): The request object containing user authentication and question data.

    Returns:
        Response: Returns the serialized data of the created question.

    Raises:
        ValidationError: If the submitted question data is invalid.

    Notes:
        - This view enables authorized examiners to create new questions with specific attributes.
        - The question data should follow the structure defined in the 'QuestionSerializer'.
        - An example request structure is provided in the OpenAPI specification.
        - Upon successful creation, the question data is returned in the response.
    """
    # permission_classes = [IsAuthenticated, IsExaminer]

    @extend_schema(
        request=QuestionSerializer,
        responses={status.HTTP_201_CREATED: QuestionSerializer},
        examples=[
            OpenApiExample(
                'Example',
                value={
                    'category': 1,
                    'text': 'What is your favorite color?',
                    'answer_type': 2,
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

        serializer.is_valid(raise_exception=True)
        question = serializer.save()

        return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    # permission_classes = [IsAuthenticated, IsExaminer]


class QuestionSelectView(APIView):
    """
    API View for selecting questions based on various filters.

    This view allows users to retrieve a list of questions based on filters
    such as category, difficulty, answer type, quantity, and favorited status.

    Permissions:
        - User must be authenticated.
        - User must have examiner privileges.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        Response: A Response object containing the selected questions.

    Note:
        -This view assumes that the user is authenticated and has the required permissions.
    """
    # permission_classes = [IsAuthenticated, IsExaminer]

    @extend_schema(
        parameters=[
            OpenApiParameter("category", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Filter questions by category."),
            OpenApiParameter("difficulty", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Filter questions by difficulty."),
            OpenApiParameter("answer_type", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Filter questions by answer type."),
            OpenApiParameter("quantity", OpenApiTypes.INT, OpenApiParameter.QUERY,
                             description="Specify the quantity of questions to retrieve."),
            OpenApiParameter("favorited_only", OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                             description="Filter questions to show only favorited ones."),
        ],
        responses={status.HTTP_200_OK: QuestionSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        category = request.query_params.get('category')
        difficulty = request.query_params.get('difficulty')
        answer_type = request.query_params.get('answer_type')
        quantity = request.query_params.get('quantity')
        favorites = request.query_params.get('favorited_only') == 'true'  # Convert string to boolean

        user = request.user

        questions = Question.objects.all()

        if favorites:
            favorite_question_ids = Favorite.objects.filter(user=user).values_list('question_id', flat=True)
            questions = questions.filter(id__in=favorite_question_ids)

        if category:
            questions = questions.filter(category=category)
        if answer_type:
            questions = questions.filter(answer_type=answer_type)
        if difficulty:
            questions = questions.filter(difficulty=difficulty)

        if quantity:
            quantity = int(quantity)
            selected_questions = questions[:quantity]
        else:
            selected_questions = questions

        question_serializer = QuestionSerializer(selected_questions, many=True)

        return Response({'questions': question_serializer.data})


class QuestionFavoriteView(APIView):
    """
    API view for managing favorite questions.

    Args:
        pk (int): The primary key of the question to mark as favorite or remove from favorites.

    Returns:
        Response: Returns a response indicating the status of the favorite operation.
            - If the question was successfully marked as a favorite, returns a message indicating so.
            - If the question was successfully removed from favorites, returns a message indicating so.

    Raises:
        Http404: If the question with the given ID is not found or does not exist.

    Permissions:
        - User must be authenticated.
        - User must have examiner privileges.
    """
    # permission_classes = [IsAuthenticated, IsExaminer]

    def post(self, request, pk):
        question = Question.objects.filter(pk=pk)
        if not question:
            raise Http404('Question not found')

        user = request.user
        favorite, created = Favorite.objects.get_or_create(user=user, question=question[0])

        if not created:
            favorite.delete()  # Unfavorite if already marked as favorite
            return Response({"message": "Question removed from favorites"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Question marked as favorite"}, status=status.HTTP_200_OK)


class QuizCreateView(generics.CreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizCreateSerializer
    # permission_classes = [IsAuthenticated, IsExaminer]


class QuizListView(generics.ListAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizDetailSerializer
    # permission_classes = [IsAuthenticated, IsExaminer]


class QuizDetailView(APIView):
    serializer_class = QuizDetailSerializer
    # permission_classes = [IsAuthenticated, IsExaminer]

    def get(self, request, quiz_unique_link):
        quiz = Quiz.objects.filter(unique_link=quiz_unique_link)
        if not quiz:
            raise Http404('Quiz not found')

        serializer = self.serializer_class(quiz[0])
        return Response(serializer.data)


class QuizUpdateDeleteView(generics.UpdateAPIView,
                           generics.mixins.DestroyModelMixin):
    queryset = Quiz.objects.all()
    serializer_class = QuizDetailSerializer
    # permission_classes = [IsAuthenticated, IsExaminer]

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ResultSubmitView(APIView):
    """
    API view for submitting quiz results.

    Args:
        request (HttpRequest): The request object containing result data.

    Returns:
        Response: Returns a response indicating the successful submission of user answers.

    Raises:
        ValidationError: If the submitted data is invalid.

    Permissions:
        - User must be authenticated.

    Notes:
        - This view processes the submitted quiz result data, including user's selected answers,
          time taken, and final score, and creates corresponding records in the database.
        - A bulk creation of submitted answers is performed within a database transaction.
        - For multiple-choice questions (answer type 1), selected answer choices are associated with
          the submitted answers.
    """
    # permission_classes = [IsAuthenticated]

    @extend_schema(request=ResultSubmitSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ResultSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        quiz = serializer.validated_data['quiz']
        answers = serializer.validated_data['answers']
        time_taken = serializer.validated_data['time_taken']
        score = serializer.validated_data['score']

        with transaction.atomic():
            result = Result.objects.create(
                user=user,
                quiz=quiz,
                score=score,
                time_taken=time_taken,
                submission_time=timezone.now()
            )

            user_answer_objects = []

            for answer_data in answers:
                question = answer_data['question']
                open_ended_answer = answer_data.get('open_ended_answer')

                user_answer = SubmittedAnswer(
                    question=question,
                    open_ended_answer=open_ended_answer,
                    quiz_result=result
                )

                user_answer_objects.append(user_answer)

            user_answers = SubmittedAnswer.objects.bulk_create(user_answer_objects)

            for user_answer, answer_data in zip(user_answers, answers):
                answer_type = answer_data['answer_type']
                if answer_type != 2 and answer_data['selected_answers']:
                    user_answer.selected_answers.add(*answer_data['selected_answers'])

        return Response({"message": "User answers submitted successfully."}, status=status.HTTP_200_OK)


class UserResultsWithAnswersView(APIView):
    """
    API view for retrieving user quiz results with answers.

    Args:
        user_id (int): The ID of the user whose results are being retrieved.

    Returns:
        Response: Returns a response containing the serialized quiz results along with detailed answer information.

    Raises:
        Http404: If the user with the given ID is not found or does not exist.

    Permissions:
        - User must be authenticated.
        - User must have examiner privileges.
    """
    # permission_classes = [IsAuthenticated, IsExaminer]

    def get(self, request, user_id, *args, **kwargs):
        user = CustomUser.objects.filter(id=user_id)
        if not user:
            raise Http404('User not found')
        results = Result.objects.filter(user=user[0])
        if not results:
            raise Http404('Results not found')
        serializer = ResultWithAnswersSerializer(results, many=True)
        return Response(serializer.data)


class SendQuizEmailView(APIView):
    """
    API view to send quiz emails to specified recipients.

    Args:
        request (HttpRequest): The request object containing the list of recipient emails and quiz ID.

    Returns:
        Response: A success message if emails are sent successfully.

    Raises:
        Http404: If the quiz with the given ID is not found.

    Permissions:
        - User must be authenticated.
        - User must have examiner privileges.
    """
    # permission_classes = [IsAuthenticated, IsExaminer]

    @extend_schema(request=QuizEmailSendSerializer)
    def post(self, request):
        serializer = QuizEmailSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz_id = serializer.validated_data['quiz_id']
        quiz = Quiz.objects.filter(pk=quiz_id)
        if not quiz:
            raise Http404('Quiz not found')
        recipient_emails = serializer.validated_data['recipient_emails']

        send_quiz_link_to_students.delay(recipient_emails, quiz[0].unique_link)

        return Response({'message': 'Emails sent successfully.'})
