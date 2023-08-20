from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from quizzes.models import Quiz, Category, Question, Result, Favorite

User = get_user_model()


class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.user = User.objects.create_user(username='testuser', password='testpassword', role='examiner')
        self.question = Question.objects.create(text='Test Question')
        self.quiz = Quiz.objects.create(
            title='Test Quiz',
            category=self.category,
            time_limit=30,
            unique_link='test-link'
        )
        self.quiz.questions.add(self.question)
        self.client.force_authenticate(user=self.user)
        self.result = Result.objects.create(user=self.user, quiz=self.quiz, time_taken=30, score=10,
                                            submission_time=timezone.now())


class SendQuizEmailViewTestCase(BaseAPITestCase):
    def test_send_quiz_email_success(self):
        data = {
            "quiz_id": self.quiz.id,
            "recipient_emails": ["test@example.com"]
        }
        response = self.client.post('/quiz/send-email', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Emails sent successfully.'})

    def test_send_quiz_email_unauthenticated(self):
        self.client.logout()

        data = {
            "quiz_id": self.quiz.id,
            "recipient_emails": ["test@example.com"]
        }

        response = self.client.post('/quiz/send-email', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'detail': 'Authentication credentials were not provided.'})

    def test_send_quiz_email_invalid_quiz(self):
        data = {
            "quiz_id": 0,  # Non-existent quiz ID
            "recipient_emails": ["test@example.com"]
        }

        response = self.client.post('/quiz/send-email', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'error': 'Quiz not found'})


class UserResultsWithAnswersViewTestCase(BaseAPITestCase):
    def test_get_user_results_with_answers(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/user-results/{self.user.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)

    def test_get_user_results_with_invalid_user_id(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/user-results/0/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "User not found"})


class QuizListViewTests(BaseAPITestCase):
    def test_get_quiz_list(self):
        self.url = reverse('quiz-list')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class QuizUpdateDeleteViewTests(BaseAPITestCase):
    def test_update_quiz(self):
        self.url = reverse('quiz-update-delete', args=[self.quiz.id])

        data = {'title': 'Updated Quiz Title'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_quiz(self):
        self.result.delete()
        self.url = reverse('quiz-update-delete', args=[self.quiz.id])

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class QuestionDetailViewTests(BaseAPITestCase):
    def test_get_question_detail(self):
        self.url = reverse('question-detail', args=[self.question.id])

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_question(self):
        self.url = reverse('question-detail', args=[self.question.id])

        data = {'text': 'Updated Question Text'}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_question(self):
        self.url = reverse('question-detail', args=[self.question.id])

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class QuizDetailViewTestCase(BaseAPITestCase):
    def test_get_quiz_detail(self):
        url = reverse('quiz-detail', args=[self.quiz.unique_link])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Quiz')

    def test_get_quiz_detail_not_found(self):
        url = reverse('quiz-detail', args=['non-existent-link'])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'error': 'Quiz not found'})

    def test_get_quiz_detail_unauthenticated(self):
        self.client.logout()
        url = reverse('quiz-detail', args=[self.quiz.unique_link])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class QuestionFavoriteViewTestCase(BaseAPITestCase):
    def test_mark_question_as_favorite(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(reverse('question-favorite', args=[self.question.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Question marked as favorite'})

        self.assertTrue(Favorite.objects.filter(user=self.user, question=self.question).exists())

    def test_unmark_question_as_favorite(self):
        self.client.force_authenticate(user=self.user)

        Favorite.objects.create(user=self.user, question=self.question)

        response = self.client.post(reverse('question-favorite', args=[self.question.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'Question removed from favorites'})

        self.assertFalse(Favorite.objects.filter(user=self.user, question=self.question).exists())

    def test_mark_question_as_favorite_unauthenticated(self):
        self.client.logout()
        response = self.client.post(reverse('question-favorite', args=[self.question.pk]))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mark_question_as_favorite_invalid_question(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(reverse('question-favorite', args=[0]))  # Non-existent question ID

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'error': 'Question not found'})

    def test_unmark_question_as_favorite_invalid_question(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(reverse('question-favorite', args=[0]))  # Non-existent question ID

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'error': 'Question not found'})
