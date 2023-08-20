import shortuuid
from rest_framework import serializers

from quizzes.models import Question, Answer, Quiz, QuestionScore, Result, UserAnswer
from users.models import CustomUser


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = '__all__'

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
        fields = ('title', 'category', 'questions', 'time_limit', 'scores')

    def create(self, validated_data):
        scores_data = validated_data.pop('scores')
        questions_data = validated_data.pop('questions')

        unique_link = shortuuid.uuid()

        validated_data['unique_link'] = unique_link

        quiz = Quiz.objects.create(**validated_data)

        for score_data in scores_data:
            question_id = score_data['question'].id
            score_value = score_data['score']
            QuestionScore.objects.create(quiz=quiz, question_id=question_id, score=score_value)

        quiz.questions.set(questions_data)

        return quiz


class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ('title', 'category', 'questions', 'time_limit', 'unique_link')

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        question_ids = [question_data['id'] for question_data in representation['questions']]
        scores = QuestionScore.objects.filter(quiz=instance, question_id__in=question_ids)
        score_data = QuestionScoreSerializer(scores, many=True).data

        for question_data in representation['questions']:
            question_id = question_data['id']
            related_scores = [score for score in score_data if score['question'] == question_id]
            question_data['scores'] = related_scores

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
    total_score = serializers.IntegerField(required=True)

    def validate(self, data):
        for answer_data in data['answers']:
            answer_type = answer_data['answer_type']

            if answer_type == 2 and not answer_data.get('open_ended_answer'):
                raise serializers.ValidationError("Open-ended answer is required for this question type.")
            elif answer_type in [0, 1] and not answer_data.get('selected_answers'):
                raise serializers.ValidationError("Selected answers are required for this question type.")

        return data


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = '__all__'


class ResultWithAnswersSerializer(serializers.ModelSerializer):
    user_answers = UserAnswerSerializer(source='answers', many=True)

    class Meta:
        model = Result
        fields = '__all__'
        depth = 1


class QuizEmailSendSerializer(serializers.Serializer):
    quiz_id = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all())
    recipient_emails = serializers.ListField(child=serializers.EmailField())
