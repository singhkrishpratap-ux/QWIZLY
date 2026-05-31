import random

# USER FUNCTIONS 

def register():
    username = input("Enter Username: ")
    password = input("Enter Password: ")

    with open("users.txt", "a") as file:
        file.write(f"{username}|{password}\n")

    print("Registration Successful!")


def login():
    username = input("Enter Username: ")
    password = input("Enter Password: ")

    with open("users.txt", "r") as file:
        users = file.readlines()

    for user in users:
        data = user.strip().split("|")

        if len(data) == 2:
            if data[0] == username and data[1] == password:
                print("Login Successful!")
                return username

    print("Invalid Username or Password")
    return None


# ADMIN FUNCTIONS 

def add_question():
    question = input("Enter Question: ")
    answer = input("Enter Answer: ")
    category = input("Enter Category: ")
    difficulty = input("Enter Difficulty: ")

    with open("questions.txt", "a") as file:
        file.write(
            f"{question}|{answer}|{category}|{difficulty}\n"
        )

    print("Question Added Successfully!")


def view_questions():
    print("\n===== QUESTION BANK =====")

    try:
        with open("questions.txt", "r") as file:
            questions = file.readlines()

        for i, q in enumerate(questions, start=1):
            print(f"{i}. {q.strip()}")

    except FileNotFoundError:
        print("Question file not found.")


def delete_question():
    view_questions()

    try:
        with open("questions.txt", "r") as file:
            questions = file.readlines()

        delete_no = int(input("Enter Question Number to Delete: "))

        if 1 <= delete_no <= len(questions):
            questions.pop(delete_no - 1)

            with open("questions.txt", "w") as file:
                file.writelines(questions)

            print("Question Deleted Successfully!")
        else:
            print("Invalid Question Number")

    except:
        print("Error deleting question")


def admin_panel():
    while True:

        print("\n===== ADMIN PANEL =====")
        print("1. Add Question")
        print("2. View Questions")
        print("3. Delete Question")
        print("4. Back")

        choice = input("Enter Choice: ")

        if choice == "1":
            add_question()

        elif choice == "2":
            view_questions()

        elif choice == "3":
            delete_question()

        elif choice == "4":
            break

        else:
            print("Invalid Choice")


# QUIZ FUNCTION 

def start_quiz(username):

    try:
        with open("questions.txt", "r") as file:
            questions = file.readlines()

        if len(questions) == 0:
            print("No Questions Available!")
            return

        random.shuffle(questions)

        score = 0
        total_questions = min(5, len(questions))

        print("\n===== QUIZ STARTED =====")

        for q in questions[:total_questions]:

            data = q.strip().split("|")

            if len(data) < 4:
                continue

            question = data[0]
            answer = data[1]
            category = data[2]
            difficulty = data[3]

            print("\n----------------------")
            print("Category:", category)
            print("Difficulty:", difficulty)
            print("Question:", question)

            user_answer = input("Your Answer: ")

            if user_answer.lower() == answer.lower():
                print("Correct!")
                score += 10
            else:
                print("Wrong!")
                print("Correct Answer:", answer)

        print("\n===== QUIZ COMPLETED =====")
        print("Final Score:", score)

        with open("leaderboard.txt", "a") as file:
            file.write(f"{username}|{score}\n")

        print("Score Saved Successfully!")

    except FileNotFoundError:
        print("questions.txt not found")


def view_leaderboard():

    print("\n===== LEADERBOARD =====")

    try:
        with open("leaderboard.txt", "r") as file:
            scores = []

            for line in file:
                data = line.strip().split("|")

                if len(data) == 2:
                    scores.append((data[0], int(data[1])))

            scores.sort(key=lambda x: x[1], reverse=True)

            for rank, (user, score) in enumerate(scores, start=1):
                print(f"{rank}. {user} - {score}")

    except FileNotFoundError:
        print("Leaderboard file not found")


# MAIN PROGRAM 

logged_user = None

while True:

    print("\n===== SMART QUIZ MANAGEMENT SYSTEM =====")
    print("1. Register")
    print("2. Login")
    print("3. Admin Login")
    print("4. Start Quiz")
    print("5. View Leaderboard")
    print("6. Exit")

    choice = input("Enter Choice: ")

    if choice == "1":
        register()

    elif choice == "2":
        logged_user = login()

    elif choice == "3":

        admin_user = input("Admin Username: ")
        admin_pass = input("Admin Password: ")

        if admin_user == "admin" and admin_pass == "admin123":
            print("Admin Login Successful!")
            admin_panel()
        else:
            print("Invalid Admin Credentials")

    elif choice == "4":

        if logged_user is None:
            print("Please Login First!")
        else:
            start_quiz(logged_user)

    elif choice == "5":
        view_leaderboard()

    elif choice == "6":
        print("Thank You!")
        break

    else:
        print("Invalid Choice")