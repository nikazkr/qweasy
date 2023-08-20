# Qweasy: Quiz Management App

Qweasy is a Python Django DRF-based application designed to streamline the process of creating and managing quizzes
within organizations. It empowers employers, educators, or examiners to efficiently assess their employees, interns, or
participants through well-structured quizzes. Qweasy simplifies the quiz creation process, offers diverse question
types, allows for effective filtering, and ensures a seamless user experience for test-takers.

## App Purpose

Qweasy serves as a comprehensive quiz management solution tailored for organizational use. Its primary purpose is to
provide a user-friendly platform where administrators can design quizzes, while participants can take tests with ease.
The application aims to bridge the gap between examiners and examinees, enabling efficient assessment and evaluation
within an organization.

## How Qweasy Works

1. **Question Creation**:
   Examiners can create a variety of questions, including single-choice, multiple-choice, and open-ended questions. Each
   question can have one or more correct answers.

2. **Question Management**:
   Examiners can categorize questions by difficulty, category, and type. They can also mark questions as favorites for
   quick access.

3. **Quiz Generation**:
   Examiners can create quizzes by selecting questions from their repository. This allows for customization based on
   desired difficulty, category, and question type.

4. **Test Distribution**:
   Upon quiz creation, a unique link is generated. Examiners can share this link with participants by email, enabling
   them to take the test.

5. **Test Submission and Review**:
   After participants complete the quiz and submit their answers, the responses are saved for later review and
   assessment.

## Technologies Used

Qweasy is built using a combination of cutting-edge technologies to provide a robust and seamless experience:

- **Python Django and Django REST Framework** for backend development
- **JWT tokens** for secure authentication and authorization
- **Google OAuth2** for streamlined user authentication
- **Docker** for containerization and deployment
- **Git** for version control and collaboration

Furthermore, Qweasy takes advantage of Google Cloud's powerful services, enhancing its capabilities and reliability. The
app is deployed on Google Cloud Platform (GCP), utilizing its scalable infrastructure and efficient cloud environment.
This integration with Google Cloud services ensures that Qweasy delivers a seamless user experience with improved
performance, availability, and security.

## Getting Started

To run Qweasy on your local environment using Docker, follow these steps:

### Installation:

- Open your terminal and execute the following command to Clone
  the repository from Github.

   ```bash
   git clone https://github.com/your-username/qweasy.git

- Set up environment variables:

  Create a .env file in the project root directory and define the following variables:

  ```bash
  SECRET_KEY=
  
  DEBUG=True
  
  POSTGRES_USER=
  POSTGRES_DB=
  POSTGRES_PASSWORD=
  POSTGRES_HOST=
  POSTGRES_PORT=
  
  CALLBACK_URL=
  CLIENT_ID=
  CLIENT_SECRET=
  
  EMAIL_USE_TLS=
  EMAIL_PORT=
  EMAIL_HOST_USER=
  EMAIL_HOST_PASSWORD=
  ```
  These variables are also available in *.env.sample* file, located in projects main folder

### Running the App:

- Build and start the Docker containers:

   ```bash
   docker-compose up --build

- Access the application in your web browser:

   ```bash
   http://localhost:8000/

### Stopping the App:

- To stop the Docker containers:

   ```bash
   docker-compose down

## API Documentation

Qweasy provides a comprehensive API for managing quizzes and users. Here's a brief overview of the available API
endpoints:

### Quizzes

- **Create Question**: `POST /question/create/`
- **Select Question**: `GET /question/`
- **Retrieve Question Detail**: `GET /question/<int:pk>/`
- **Favorite Question**: `POST /question/<int:pk>/favorite/`
- **Create Quiz**: `POST /quiz/create/`
- **Retrieve Quiz Detail by Unique Link**: `GET /quiz/<str:quiz_unique_link>/`
- **Update/Delete Quiz**: `PUT/PATCH/DELETE /quiz/<int:pk>`
- **List Quizzes**: `GET /quiz/`
- **Submit Quiz Results**: `POST /quiz/submit`
- **Retrieve User Results with Answers**: `GET /user-results/<int:user_id>/`
- **Send Quiz URL by Email to the Participants**: `POST /quiz/send-email/`

### Users

- **Obtain Token**: `POST /users/token/`
- **Refresh Token**: `POST /users/token/refresh/`
- **Login with Google**: `POST /users/login/google/`
- **Register User**: `POST /users/register/`
- **Login User**: `POST /users/login/`
- **Logout User**: `POST /users/logout/`
- **Get/Update User**: `GET/PUT/PATCH /users/user/`
- **Change Password**: `POST /user/password/change/`

For detailed information about each API endpoint, request/response formats, and authentication, please refer to
the [Ararsebuli Linki](link-to-api-documentation).

## Contact Information

If you have any questions or need assistance, you can reach out to me at:

- Email: nika.zakariashvili@makingscience.com
- GitHub: [@nikazkr](https://github.com/nikazkr)

## Credits

I would like to extend my gratitude to the following resources and libraries that have been instrumental in the
development of Qweasy:

- Django: [https://www.djangoproject.com/](https://www.djangoproject.com/)
- Django REST framework: [https://www.django-rest-framework.org/](https://www.django-rest-framework.org/)
- Docker: [https://www.docker.com/](https://www.docker.com/)
- Chat-GPT [https://chat.openai.com/](https://chat.openai.com/)

Special thanks to the open-source community for their valuable contributions.

---

**Qweasy** is released under the [MIT License](LICENSE).