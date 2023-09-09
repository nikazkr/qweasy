from django.db import transaction
from rest_framework import serializers

from quizzes.models import Question, Answer, Quiz, QuestionScore, Result, SubmittedAnswer, OpenEndedAnswer
from users.models import CustomUser


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'text', 'image')


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = ('id', 'category', 'text', 'image', 'answer_type', 'difficulty', 'answers')

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = Question.objects.create(**validated_data)

        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)

        return question

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.category = validated_data.get('category', instance.category)
        instance.answer_type = validated_data.get('answer_type', instance.answer_type)
        instance.difficulty = validated_data.get('difficulty', instance.difficulty)

        answers_data = validated_data.get('answers')
        if answers_data:
            instance.answers.all().delete()
            for answer_data in answers_data:
                Answer.objects.create(question=instance, **answer_data)

        instance.save()
        return instance


class QuestionScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionScore
        fields = ('question', 'score')


class QuizCreateSerializer(serializers.ModelSerializer):
    scores = QuestionScoreSerializer(many=True, write_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'title', 'category', 'questions', 'time_limit', 'scores')

    def create(self, validated_data):
        scores_data = validated_data.pop('scores')
        question_ids = validated_data.pop('questions', [])

        with transaction.atomic():
            quiz = Quiz.objects.create(**validated_data)
            quiz.questions.set(question_ids)

            scores_objects = []

            for score_data in scores_data:
                question_id = score_data['question'].id
                score_value = score_data['score']
                scores = QuestionScore(quiz=quiz, question_id=question_id, score=score_value)

                scores_objects.append(scores)

            QuestionScore.objects.bulk_create(scores_objects)

        return quiz


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    scores = QuestionScoreSerializer(many=True, write_only=True)

    class Meta:
        model = Quiz
        fields = ('id', 'title', 'category', 'questions', 'time_limit', 'scores')

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        question_ids = [question_data['id'] for question_data in representation['questions']]
        scores = QuestionScore.objects.filter(quiz=instance, question_id__in=question_ids)
        score_data = QuestionScoreSerializer(scores, many=True).data

        for question_data in representation['questions']:
            question_id = question_data['id']
            related_score = [score for score in score_data if score['question'] == question_id][0].get('score')
            question_data['score'] = related_score

        return representation


class ResultSingleSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    selected_answers = serializers.PrimaryKeyRelatedField(queryset=Answer.objects.all(), many=True, required=False)
    open_ended_answer = serializers.CharField(allow_blank=True, required=False)
    answer_type = serializers.IntegerField(required=True)


class ResultSubmitSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all())
    answers = serializers.ListSerializer(child=ResultSingleSerializer())
    time_taken = serializers.DurationField(required=True)
    feedback = serializers.CharField()

    def validate(self, data):
        for answer_data in data['answers']:
            answer_type = answer_data['answer_type']

            if answer_type == 2 and (not answer_data.get('open_ended_answer') or answer_data.get('selected_answers')):
                raise serializers.ValidationError("Only open-ended answer is needed for this question type.")
            elif answer_type in [0, 1] and (
                    not answer_data.get('selected_answers') or answer_data.get('open_ended_answer')):
                raise serializers.ValidationError("Only selected answers are needed for this question type.")

        return data


class QuizEmailSendSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()
    recipient_emails = serializers.ListField(child=serializers.EmailField())


class UserResultListSerializer(serializers.ModelSerializer):
    quiz_id = serializers.SerializerMethodField()
    quiz_name = serializers.SerializerMethodField()

    class Meta:
        model = Result
        fields = ('id', 'quiz_id', 'quiz_name', 'score', 'submission_time')

    def get_quiz_id(self, obj):
        return obj.quiz.id

    def get_quiz_name(self, obj):
        return obj.quiz.title


class OpenEndedAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenEndedAnswer
        fields = ('id', 'answer_text', 'score')


class SubmittedAnswerSerializer(serializers.ModelSerializer):
    selected_answers = AnswerSerializer(many=True)
    open_ended_answer = OpenEndedAnswerSerializer()

    class Meta:
        model = SubmittedAnswer
        fields = ('question', 'selected_answers', 'open_ended_answer')

    def get_selected_answers(self, obj):
        return obj.selected_answers.all()


class UserResultDetailSerializer(serializers.ModelSerializer):
    answers = SubmittedAnswerSerializer(many=True)

    class Meta:
        model = Result
        fields = '__all__'


class OpenEndedReviewSerializer(serializers.Serializer):
    open_ended_answer_id = serializers.IntegerField()
    score = serializers.IntegerField()

    def validate(self, data):
        # Get the maximum score for the associated question

        open_ended = OpenEndedAnswer.objects.filter(id=data.get('open_ended_answer_id')).first()
        quiz = open_ended.submitted_answer.quiz_result.quiz
        max_score = QuestionScore.objects.filter(
            question__submittedanswer__open_ended_answer=data.get('open_ended_answer_id'), quiz=quiz).first().score

        if not (0 <= data.get('score') <= max_score):
            raise serializers.ValidationError(f"Score must be between 0 and {max_score}.")

        return data
