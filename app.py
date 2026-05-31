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

    category = request.form["category"]
    difficulty = request.form["difficulty"]
    amount = request.form["amount"]

    session["questions"] = get_questions(
        category,
        difficulty,
        amount
    )

    session["current"] = 0
    session["score"] = 0

    return redirect(url_for("instructions"))


@app.route("/instructions")
def instructions():
    return render_template("instructions.html")

# QUIZ PAGE

@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    questions = session.get("questions")

    if not questions:
        return redirect(url_for("home"))

    current = session.get("current", 0)

    if request.method == "POST":

        user_answer = request.form.get("user_answer")

        correct_answer = questions[current]["answer"]

        if user_answer == correct_answer:
            session["score"] += 10

        session["current"] += 1

        if session["current"] >= len(questions):
            return redirect(url_for("result"))

        return redirect(url_for("quiz"))

    question = questions[current]

    progress = int(((current) / len(questions)) * 100)

    return render_template(
        "quiz.html",
        question=question["question"],
        category=question["category"],
        difficulty=question["difficulty"],
        options=question["options"],
        qno=current + 1,
        total=len(questions),
        progress=progress
    )


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
        total=total_questions
    )


if __name__ == "__main__":
    app.run(debug=True)