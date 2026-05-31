from flask import Flask, render_template, request, redirect, url_for, session
import requests
import html
import random

app = Flask(__name__)
app.secret_key = "smart_quiz_secret"


# USER FUNCTIONS

def register_user(username, password):

    try:

        with open("users.txt", "r") as file:

            for line in file:

                data = line.strip().split("|")

                if len(data) == 2:

                    if data[0] == username:
                        return False

    except FileNotFoundError:
        pass

    with open("users.txt", "a") as file:
        file.write(f"{username}|{password}\n")

    return True


def validate_user(username, password):

    try:

        with open("users.txt", "r") as file:

            for line in file:

                data = line.strip().split("|")

                if len(data) == 2:

                    if data[0] == username and data[1] == password:
                        return True

    except FileNotFoundError:
        return False

    return False


# QUIZ API

def get_questions(category, difficulty, amount):

    url = (
        f"https://opentdb.com/api.php?"
        f"amount={amount}"
        f"&category={category}"
        f"&difficulty={difficulty}"
        f"&type=multiple"
    )

    response = requests.get(url)
    data = response.json()

    questions = []

    for item in data["results"]:

        options = [
            html.unescape(item["correct_answer"])
        ]

        for wrong in item["incorrect_answers"]:
            options.append(
                html.unescape(wrong)
            )

        random.shuffle(options)

        questions.append({
            "question": html.unescape(item["question"]),
            "answer": html.unescape(item["correct_answer"]),
            "options": options,
            "category": item["category"],
            "difficulty": item["difficulty"]
        })

    return questions


# LOGIN

@app.route("/", methods=["GET", "POST"])
def login_page():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if validate_user(username, password):

            session["username"] = username

            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Invalid Username or Password"
        )

    return render_template("login.html")


# REGISTER

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if register_user(username, password):

            return redirect(url_for("login_page"))

        return render_template(
            "register.html",
            error="Username already exists"
        )

    return render_template("register.html")


# LOGOUT

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login_page"))


# HOME

@app.route("/home")
def home():

    if "username" not in session:
        return redirect(url_for("login_page"))

    return render_template(
        "home.html",
        username=session["username"]
    )


# START QUIZ

@app.route("/start", methods=["POST"])
def start_quiz():

    category = session["category"]
    difficulty = session["difficulty"]
    amount = session["amount"]  

    session["questions"] = get_questions(
        category,
        difficulty,
        amount
    )

    session["current"] = 0
    session["score"] = 0
    session["review"] = []

    return redirect(url_for("instructions"))


@app.route("/instructions", methods=["GET", "POST"])
def instructions():

    if request.method == "POST":

        session["category"] = request.form["category"]
        session["difficulty"] = request.form["difficulty"]
        session["amount"] = request.form["amount"]

    return render_template("instructions.html")

# QUIZ PAGE
@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    questions = session.get("questions", [])
    current = session.get("current", 0)

    if current >= len(questions):
        return redirect(url_for("result"))

    question = questions[current]

    # Handle submitted answer
    if request.method == "POST":

        user_answer = request.form.get("user_answer")

        if "review" not in session:
            session["review"] = []

        review = session.get("review", [])

        review.append({
            "question": question["question"],
            "user_answer": user_answer,
            "correct_answer": question["answer"],
            "is_correct": user_answer == question["answer"]
        })

        session["review"] = review

        if user_answer == question["answer"]:
            session["score"] += 10

        session["current"] = current + 1

        if session["current"] >= len(questions):
            return redirect(url_for("result"))

        return redirect(url_for("quiz"))

    # TIMER BASED ON DIFFICULTY
    if question["difficulty"] == "easy":
        timer = 30
    elif question["difficulty"] == "medium":
        timer = 45
    else:
        timer = 60

    progress = int(((current + 1) / len(questions)) * 100)

    return render_template(
        "quiz.html",
        question=question["question"],
        category=question["category"],
        difficulty=question["difficulty"],
        options=question["options"],
        qno=current + 1,
        total=len(questions),
        progress=progress,
        timer=timer
    )
@app.route("/next_question", methods=["POST"])
def next_question():

    session["current"] += 1

    questions = session.get("questions", [])

    if session["current"] >= len(questions):
        return redirect(url_for("result"))

    return redirect(url_for("quiz"))


# RESULTS

@app.route("/result")
def result():

    score = session.get("score", 0)

    total_questions = len(
        session.get("questions", [])
    )

    percentage = round(
        (score / (total_questions * 10)) * 100
    )

    correct = score // 10
    wrong = total_questions - correct

    return render_template(
    "results.html",
    score=score,
    percentage=percentage,
    correct=correct,
    wrong=wrong,
    total=total_questions,
    review=session.get("review", [])
)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)