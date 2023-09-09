from django.db import transaction
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import status, generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.mail import send_quiz_link_to_students
from utils.permissions import IsExaminer
from utils.score import calculate_score
from .models import Question, Favorite, Quiz, Result, SubmittedAnswer, OpenEndedAnswer, QuestionScore
from .serializers import QuestionSerializer, QuizDetailSerializer, \
    ResultSubmitSerializer, QuizEmailSendSerializer, QuizCreateSerializer, \
    UserResultListSerializer, UserResultDetailSerializer, OpenEndedReviewSerializer


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

    permission_classes = [IsAuthenticated, IsExaminer]

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
    permission_classes = [IsAuthenticated, IsExaminer]


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

    permission_classes = [IsAuthenticated, IsExaminer]

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
            questions = questions[:quantity]

        question_serializer = QuestionSerializer(questions, many=True)

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
        NotFound: If the question with the given ID is not found or does not exist.

    Permissions:
        - User must be authenticated.
        - User must have examiner privileges.
    """

    permission_classes = [IsAuthenticated, IsExaminer]

    def post(self, request, pk):
        question = Question.objects.filter(pk=pk)
        if not question:
            raise NotFound('Question not found')

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
    permission_classes = [IsAuthenticated, IsExaminer]


class QuizListView(generics.ListAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizDetailSerializer
    permission_classes = [IsAuthenticated, IsExaminer]


class QuizDetailView(APIView):
    serializer_class = QuizDetailSerializer

    permission_classes = [IsAuthenticated, IsExaminer]

    def get(self, request, quiz_unique_link):
        quiz = Quiz.objects.filter(unique_link=quiz_unique_link)
        if not quiz:
            raise NotFound('Quiz not found')

        serializer = self.serializer_class(quiz[0])
        return Response(serializer.data)


class QuizUpdateDeleteView(generics.UpdateAPIView,
                           generics.mixins.DestroyModelMixin):
    queryset = Quiz.objects.all()
    serializer_class = QuizDetailSerializer

    permission_classes = [IsAuthenticated, IsExaminer]

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

    serializer_class = ResultSubmitSerializer

    # permission_classes = [IsAuthenticated]

    @extend_schema(request=ResultSubmitSerializer)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        quiz = serializer.validated_data['quiz']
        answers = serializer.validated_data['answers']
        time_taken = serializer.validated_data['time_taken']
        feedback = serializer.validated_data['feedback']

        score = calculate_score(quiz, answers)

        with transaction.atomic():
            result = Result.objects.create(
                user=user,
                quiz=quiz,
                score=score.get('total_score'),
                time_taken=time_taken,
                feedback=feedback,
                submission_time=timezone.now()
            )

            user_answer_objects = []
            open_ended_answers = []

            for answer_data in answers:
                question = answer_data['question']
                open_ended_answer = answer_data.get('open_ended_answer')

                user_answer = SubmittedAnswer(
                    question=question,
                    quiz_result=result
                )
                user_answer_objects.append(user_answer)

                if question.answer_type == 2:
                    open_ended = OpenEndedAnswer(
                        answer_text=open_ended_answer,
                        submitted_answer=user_answer
                    )
                    open_ended_answers.append(open_ended)

            user_answers = SubmittedAnswer.objects.bulk_create(user_answer_objects)
            OpenEndedAnswer.objects.bulk_create(open_ended_answers)

            for user_answer, answer_data in zip(user_answers, answers):
                answer_type = answer_data['answer_type']
                if answer_type != 2 and answer_data['selected_answers']:
                    user_answer.selected_answers.add(*answer_data['selected_answers'])

            if score.get('total_max_score') > 0:
                percentage = score.get('total_score') / score.get('total_max_score') * 100
            else:
                percentage = 100

            user.overall_percentage = (float(user.overall_percentage) * user.total_tests_taken +
                                       percentage) / (user.total_tests_taken + 1)

            user.total_time_spent += time_taken
            user.total_tests_taken += 1

            # weight = 1 / user.total_tests_taken
            # user.overall_percentage = (1 - weight) * float(user.overall_percentage) + (
            #         weight * percentage)
            user.save()

        return Response({
            'message': 'User answers submitted successfully.',
            'score': score.get('total_score'),
            'max_score': score.get('total_max_score'),
            'percentage': round(percentage, 2)
        }, status=status.HTTP_200_OK)


class SendQuizEmailView(APIView):
    """
    API view to send quiz emails to specified recipients.

    Args:
        request (HttpRequest): The request object containing the list of recipient emails and quiz ID.

    Returns:
        Response: A success message if emails are sent successfully.

    Raises:
        NotFound: If the quiz with the given ID is not found.

    Permissions:
        - User must be authenticated.
        - User must have examiner privileges.
    """

    serializer_class = QuizEmailSendSerializer
    permission_classes = [IsAuthenticated, IsExaminer]

    @extend_schema(request=QuizEmailSendSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz_id = serializer.validated_data['quiz_id']
        quiz = Quiz.objects.filter(pk=quiz_id)
        if not quiz:
            raise NotFound('Quiz not found')
        recipient_emails = serializer.validated_data['recipient_emails']

        send_quiz_link_to_students.delay(recipient_emails, quiz[0].unique_link)

        return Response({'message': 'Emails sent successfully.'})


class UserResultListView(generics.ListAPIView):
    serializer_class = UserResultListSerializer
    permission_classes = [IsAuthenticated, IsExaminer]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Result.objects.filter(user_id=user_id)


class UserResultDetailView(generics.RetrieveAPIView):
    queryset = Result.objects.all()
    permission_classes = [IsAuthenticated, IsExaminer]
    serializer_class = UserResultDetailSerializer
    lookup_field = 'id'


class OpenEndedReview(APIView):
    # permission_classes = [IsAuthenticated, IsExaminer]

    @extend_schema(request=OpenEndedReviewSerializer)
    def post(self, request):
        serializer = OpenEndedReviewSerializer(data=request.data)
        if serializer.is_valid():

            open_ended_answer_id = serializer.validated_data['open_ended_answer_id']
            score = serializer.validated_data['score']

            open_ended_answer = OpenEndedAnswer.objects.filter(id=open_ended_answer_id).first()
            if not open_ended_answer:
                raise NotFound('Answer not found')
            result = open_ended_answer.submitted_answer.quiz_result

            question = open_ended_answer.submitted_answer.question
            quiz = result.quiz

            this_questions_max_score = QuestionScore.objects.filter(quiz=quiz, question=question).first().score

            choices_max_score = QuestionScore.objects.filter(quiz=quiz, question__answer_type=1)
            if choices_max_score:
                choices_max_score = choices_max_score.values('score').first().get('score')
            else:
                choices_max_score = 0

            reviewed_open_ended_max_score = (QuestionScore.objects
                                             .filter(quiz=quiz, question__answer_type=2,
                                                     question__submittedanswer__open_ended_answer__score__isnull=False))
            if reviewed_open_ended_max_score:
                reviewed_open_ended_max_score = reviewed_open_ended_max_score.values('score').first().get('score')
            else:
                reviewed_open_ended_max_score = 0

            old_max = choices_max_score + reviewed_open_ended_max_score

            old_score = result.score

            this_questions_percentage = score / this_questions_max_score * 100

            if old_max > 0:
                old_percentage = old_score / old_max * 100
                new_percentage = (old_percentage + this_questions_percentage) / 2

            else:
                new_percentage = this_questions_percentage
                old_percentage = 100

            user = result.user

            user.overall_percentage = (float(user.overall_percentage) * user.total_tests_taken -
                                       old_percentage + new_percentage) / user.total_tests_taken

            if open_ended_answer.score:
                result.score -= open_ended_answer.score
            result.score += score
            open_ended_answer.score = score

            open_ended_answer.save()
            result.save()
            user.save()

            return Response({'message': 'Score updated successfully'}, status=status.HTTP_200_OK)

        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
