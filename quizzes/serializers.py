from rest_framework import serializers

from quizzes.models import Question, Answer, Quiz, Score


class QuestionSelectSerializer(serializers.Serializer):
    category = serializers.IntegerField(required=False)
    difficulty = serializers.IntegerField(required=False)
    type = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(min_value=1, max_value=100, required=True)


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
        answers_data = validated_data.pop('answers')  # Extract answers data
        question = Question.objects.create(**validated_data)

        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)

        return question

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.category = validated_data.get('category', instance.category)
        instance.type = validated_data.get('type', instance.type)
        instance.difficulty = validated_data.get('difficulty', instance.difficulty)

        answers_data = validated_data.get('answers')
        if answers_data:
            instance.answers.all().delete()
            for answer_data in answers_data:
                Answer.objects.create(question=instance, **answer_data)

        instance.save()
        return instance


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ('question', 'score')


class QuizSerializer(serializers.ModelSerializer):
    scores = ScoreSerializer(many=True, write_only=True)  # Nested field for scores

    class Meta:
        model = Quiz
        fields = ('title', 'category', 'questions', 'time_limit', 'scores')

    def create(self, validated_data):
        scores_data = validated_data.pop('scores')  # Extract scores data
        questions_data = validated_data.pop('questions')  # Extract questions data

        quiz = Quiz.objects.create(**validated_data)

        for score_data in scores_data:
            question_id = score_data['question'].id
            score_value = score_data['score']
            Score.objects.create(quiz=quiz, question_id=question_id, score=score_value)

        # Add related questions using the set() method
        quiz.questions.set(questions_data)

        return quiz
