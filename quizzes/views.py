from json import JSONDecodeError

from django.core.serializers.base import DeserializationError
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import CustomUser
from utils.mail import send_quiz_link_to_students
from utils.permissions import IsExaminer
from .models import Question, Favorite, Quiz, Result, UserAnswer
from .serializers import QuestionSerializer, QuizCreateSerializer, QuizDetailSerializer, \
    ResultSubmitSerializer, ResultWithAnswersSerializer, QuizEmailSendSerializer


class QuestionCreateView(APIView):
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

        try:
            serializer.is_valid(raise_exception=True)
            question = serializer.save()
            return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'error': 'Integrity error occurred'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValidationError, DeserializationError):
            return Response({'error': 'Validation error occurred'}, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return Response({'error': 'JSON decoding error occurred'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsExaminer]


class QuestionSelectView(APIView):
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
        try:
            category = request.query_params.get('category')
            difficulty = request.query_params.get('difficulty')
            answer_type = request.query_params.get('answer_type')
            quantity = int(request.query_params.get('quantity', 10))  # Default to 10 if not provided
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

            selected_questions = questions[:quantity]
            question_serializer = QuestionSerializer(selected_questions, many=True)
            return Response({'questions': question_serializer.data})

        except ValueError:
            return Response({'error': 'Invalid quantity parameter'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuestionFavoriteView(APIView):
    permission_classes = [IsAuthenticated, IsExaminer]

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
    serializer_class = QuizCreateSerializer
    permission_classes = [IsAuthenticated, IsExaminer]


class QuizListView(generics.ListAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizDetailSerializer
    permission_classes = [IsAuthenticated, IsExaminer]


class QuizDetailView(APIView):
    serializer_class = QuizDetailSerializer
    permission_classes = [IsAuthenticated, IsExaminer]

    @method_decorator(cache_page(60))
    def get(self, request, quiz_unique_link):
        try:
            quiz = Quiz.objects.get(unique_link=quiz_unique_link)
            serializer = self.serializer_class(quiz)
            return Response(serializer.data)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)


class QuizUpdateDeleteView(generics.UpdateAPIView,
                           generics.mixins.DestroyModelMixin):
    queryset = Quiz.objects.all()
    serializer_class = QuizDetailSerializer
    permission_classes = [IsAuthenticated, IsExaminer]

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ResultSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ResultSubmitSerializer)
    def post(self, request, *args, **kwargs):
        serializer = ResultSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        quiz = serializer.validated_data['quiz']
        answers = serializer.validated_data['answers']
        time_taken = serializer.validated_data['time_taken']
        score = serializer.validated_data['score']

        try:
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
                    answer_type = answer_data['answer_type']
                    selected_answers = answer_data.get('selected_answers')
                    open_ended_answer = answer_data.get('open_ended_answer')

                    user_answer = UserAnswer(
                        question=question,
                        open_ended_answer=open_ended_answer,
                        quiz_result=result
                    )

                    user_answer_objects.append(user_answer)

                user_answers = UserAnswer.objects.bulk_create(user_answer_objects)

                for user_answer, answer_data in zip(user_answers, answers):
                    answer_type = answer_data['answer_type']
                    if answer_type != 2 and answer_data['selected_answers']:
                        user_answer.selected_answers.add(*answer_data['selected_answers'])

        except Exception as e:
            if 'user_answers' in locals():
                UserAnswer.objects.filter(pk__in=[ua.pk for ua in user_answers]).delete()
            if 'result' in locals():
                result.delete()
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "User answers submitted successfully."}, status=status.HTTP_200_OK)




class UserResultsWithAnswersView(APIView):
    permission_classes = [IsAuthenticated, IsExaminer]

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=user_id)
            results = Result.objects.filter(user=user)
            serializer = ResultWithAnswersSerializer(results, many=True)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An error occurred', 'details': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendQuizEmailView(APIView):
    # permission_classes = [IsAuthenticated, IsExaminer]

    @extend_schema(request=QuizEmailSendSerializer)
    def post(self, request):
        serializer = QuizEmailSendSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            quiz_id = serializer.validated_data['quiz_id']
            quiz = Quiz.objects.get(pk=quiz_id)
            recipient_emails = serializer.validated_data['recipient_emails']

            send_quiz_link_to_students.delay(recipient_emails, quiz.unique_link)

            return Response({'message': 'Emails sent successfully.'})
        except ValidationError as ve:
            return Response({'error': ve.detail}, status=400)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found'}, status=404)
        except Exception as e:
            return Response({'error': 'An error occurred', 'details': str(e)}, status=500)
