from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Quiz, Question, Answer
from .serializers import QuizSerializer

class QuizViewSet(viewsets.ModelViewSet):  # Use ModelViewSet instead of ReadOnlyModelViewSet
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        question_id = request.data.get('question_id')
        answer_id = request.data.get('answer_id')

        # Check if the question exists for the given quiz
        try:
            question = Question.objects.get(id=question_id, quiz_id=pk)
        except Question.DoesNotExist:
            return Response({'error': 'Invalid question ID'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the answer exists for the given question
        try:
            answer = question.answers.get(id=answer_id)
        except Answer.DoesNotExist:
            return Response({'error': 'Invalid answer ID'}, status=status.HTTP_400_BAD_REQUEST)

        # Determine if the answer is correct
        if answer.is_correct:
            return Response({'result': 'Correct!'}, status=status.HTTP_200_OK)
        else:
            return Response({'result': 'Incorrect, try again.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def add_question(self, request, pk=None):
        quiz = self.get_object()
        question_text = request.data.get("text")
        answers_data = request.data.get("answers", [])

        if not question_text:
            return Response({"error": "Question text is required."}, status=status.HTTP_400_BAD_REQUEST)

        question = Question.objects.create(quiz=quiz, text=question_text)
        for answer_data in answers_data:
            Answer.objects.create(
                question=question,
                text=answer_data["text"],
                is_correct=answer_data["is_correct"]
            )
        return Response({"message": "Question added successfully!"}, status=status.HTTP_201_CREATED)

