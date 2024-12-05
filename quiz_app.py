import streamlit as st
import requests

# Base URL for the DRF API (update with your actual API URL)
API_BASE_URL = "http://127.0.0.1:8000/api/quizzes/"

# Function to add a new question to the quiz
def add_question(quiz_id, question_text, answers):
    # The API endpoint to add the question
    url = f"{API_BASE_URL}{quiz_id}/add_question/"
    
    # Prepare the data for the new question
    data = {
        "text": question_text,
        "answers": answers
    }
    
    # Send the POST request to the API to add the question
    response = requests.post(url, json=data)
    
    if response.status_code == 201:
        return True  # Successfully added the question
    else:
        return False  # Failed to add the question

# Function to add a new quiz
def add_quiz(title):
    url = API_BASE_URL
    data = {
        "title": title,
    }
    response = requests.post(url, json=data)
    if response.status_code == 201:
        return response.json()  # Return the newly created quiz data
    else:
        return None  # Failed to create a new quiz

# Function to fetch quizzes from the API
def fetch_quizzes():
    response = requests.get(API_BASE_URL)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch quizzes.")
        return []

# Streamlit interface for quiz app
st.title("Welcome to Brokly Quizz Platform")

# Sidebar navigation to choose between adding questions or playing the quiz
mode = st.sidebar.selectbox("Choose Mode", ["Create Quiz", "Add Questions", "Play Quiz"])

### Interface 1: Create Quiz ###
if mode == "Create Quiz":
    st.header("Create a New Quiz")

    # Input fields for new quiz title
    new_quiz_title = st.text_input("Enter quiz title:")

    if st.button("Create Quiz"):
        if new_quiz_title.strip():
            new_quiz = add_quiz(new_quiz_title)
            if new_quiz:
                st.success(f"Quiz '{new_quiz_title}' created successfully!")
                quizzes = fetch_quizzes()  # Re-fetch the quizzes to include the new one
            else:
                st.error("Failed to create the quiz.")
        else:
            st.error("Please provide a title for the quiz.")

### Interface 2: Add Questions ###
elif mode == "Add Questions":
    st.header("Add a New Question to a Quiz")
    
    quizzes = fetch_quizzes()  # Fetch available quizzes
    
    if quizzes:
        quiz_titles = [quiz['title'] for quiz in quizzes]
        selected_quiz_title = st.selectbox("Select a Quiz", quiz_titles)

        if selected_quiz_title:
            selected_quiz = next(quiz for quiz in quizzes if quiz['title'] == selected_quiz_title)

            # Input fields for the new question and answers
            question_text = st.text_input("Enter the question text:")
            answers = []
            
            for i in range(4):
                answer_text = st.text_input(f"Answer {i + 1} Text:", key=f"answer_text_{i}")
                is_correct = st.checkbox(f"Is this the correct answer?", key=f"is_correct_{i}")
                if answer_text.strip():
                    answers.append({"text": answer_text, "is_correct": is_correct})

            # Button to add the question to the selected quiz
            if st.button("Add Question"):
                if question_text.strip() and answers:
                    # Attempt to add the question using the API
                    if add_question(selected_quiz['id'], question_text, answers):
                        st.success("Question added successfully!")
                    else:
                        st.error("Failed to add question.")
                else:
                    st.error("Please provide a question and at least one answer.")
    else:
        st.info("No quizzes available.")
        # Option to add a new quiz if no quizzes are available
        st.subheader("Create a New Quiz")
        new_quiz_title = st.text_input("Enter quiz title:")

        if st.button("Create Quiz"):
            if new_quiz_title.strip():
                new_quiz = add_quiz(new_quiz_title)
                if new_quiz:
                    st.success(f"Quiz '{new_quiz_title}' created successfully!")
                    quizzes = fetch_quizzes()  # Re-fetch the quizzes to include the new one
                else:
                    st.error("Failed to create the quiz.")
            else:
                st.error("Please provide a title for the quiz.")

### Interface 3: Play Quiz ###
elif mode == "Play Quiz":
    st.header("Play a Quiz")

    # Function to fetch questions for the quiz
    def fetch_questions(quiz_id):
        response = requests.get(f"{API_BASE_URL}{quiz_id}/")
        if response.status_code == 200:
            return response.json().get('questions', [])
        else:
            st.error("Failed to fetch questions.")
            return []

    quizzes = fetch_quizzes()
    if quizzes:
        quiz_titles = [quiz['title'] for quiz in quizzes]
        selected_quiz_title = st.selectbox("Select a Quiz to Play", quiz_titles)

        if selected_quiz_title:
            selected_quiz = next(quiz for quiz in quizzes if quiz['title'] == selected_quiz_title)
            questions = fetch_questions(selected_quiz['id'])

            # Loop through questions and show them with radio buttons for answers
            for question in questions:
                st.subheader(question['text'])
                answer_options = {ans['id']: ans['text'] for ans in question['answers']}
                
                selected_answer_id = st.radio(
                    "Choose an answer:",
                    list(answer_options.keys()),
                    format_func=lambda x: answer_options[x],
                    key=question['id']
                )

                # Submit the selected answer
                if st.button("Submit Answer", key=f"submit_{question['id']}"):
                    response = requests.post(
                        f"{API_BASE_URL}{selected_quiz['id']}/submit_answer/",
                        json={"question_id": question['id'], "answer_id": selected_answer_id}
                    )
                    if response.status_code == 200:
                        st.success(response.json().get('result', 'No result received'))
                    else:
                        st.error("Failed to submit answer.")
    else:
        st.info("No quizzes available.")
