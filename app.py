import os
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DATABASE = os.path.join(os.path.dirname(__file__), "learnloop.db")

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

CORS(app)


# =========================================================
# SUBJECT TOPICS
# =========================================================

TOPICS = {
    "Java": [
        "Variables",
        "Loops",
        "OOP",
        "Exceptions",
        "Collections"
    ],

    "DSA": [
        "Arrays",
        "Strings",
        "Linked Lists",
        "Stacks & Queues",
        "Sorting"
    ],

    "DBMS": [
        "SQL",
        "Keys",
        "Normalization",
        "Joins",
        "Transactions"
    ]
}


# =========================================================
# QUIZ QUESTIONS
# =========================================================

QUIZ_DATA = {

    "Java": [

        {
            "id": 1,
            "topic": "Variables",
            "question": "Which keyword is used to declare an integer variable in Java?",
            "options": [
                "integer",
                "int",
                "number",
                "IntegerType"
            ],
            "answer": 1
        },

        {
            "id": 2,
            "topic": "Loops",
            "question": "Which loop is best when the number of iterations is known?",
            "options": [
                "while",
                "do-while",
                "for",
                "switch"
            ],
            "answer": 2
        },

        {
            "id": 3,
            "topic": "OOP",
            "question": "Which concept allows one class to acquire properties of another class?",
            "options": [
                "Encapsulation",
                "Inheritance",
                "Abstraction",
                "Compilation"
            ],
            "answer": 1
        },

        {
            "id": 4,
            "topic": "Exceptions",
            "question": "Which block is used to handle an exception?",
            "options": [
                "if",
                "switch",
                "catch",
                "loop"
            ],
            "answer": 2
        },

        {
            "id": 5,
            "topic": "Collections",
            "question": "Which collection does not allow duplicate elements?",
            "options": [
                "List",
                "Set",
                "ArrayList",
                "Vector"
            ],
            "answer": 1
        }

    ],

    "DSA": [

        {
            "id": 1,
            "topic": "Arrays",
            "question": "What is the index of the first element in a normal Java array?",
            "options": [
                "0",
                "1",
                "-1",
                "Depends on array"
            ],
            "answer": 0
        },

        {
            "id": 2,
            "topic": "Strings",
            "question": "Which data structure is commonly used to reverse a string?",
            "options": [
                "Stack",
                "Graph",
                "Tree",
                "Heap"
            ],
            "answer": 0
        },

        {
            "id": 3,
            "topic": "Linked Lists",
            "question": "A linked list node normally contains data and what?",
            "options": [
                "Only index",
                "Reference to another node",
                "Only array",
                "Only loop"
            ],
            "answer": 1
        },

        {
            "id": 4,
            "topic": "Stacks & Queues",
            "question": "Which principle does a stack follow?",
            "options": [
                "FIFO",
                "LIFO",
                "Random",
                "Priority only"
            ],
            "answer": 1
        },

        {
            "id": 5,
            "topic": "Sorting",
            "question": "Which sorting algorithm repeatedly compares adjacent elements?",
            "options": [
                "Binary Search",
                "Bubble Sort",
                "DFS",
                "BFS"
            ],
            "answer": 1
        }

    ],

    "DBMS": [

        {
            "id": 1,
            "topic": "SQL",
            "question": "Which command is used to retrieve data from a database?",
            "options": [
                "GET",
                "SELECT",
                "FETCHALL",
                "READ"
            ],
            "answer": 1
        },

        {
            "id": 2,
            "topic": "Keys",
            "question": "Which key uniquely identifies a record?",
            "options": [
                "Foreign Key",
                "Primary Key",
                "Secondary Key",
                "Normal Key"
            ],
            "answer": 1
        },

        {
            "id": 3,
            "topic": "Normalization",
            "question": "What is a major purpose of normalization?",
            "options": [
                "Increase redundancy",
                "Reduce redundancy",
                "Delete databases",
                "Increase duplicate data"
            ],
            "answer": 1
        },

        {
            "id": 4,
            "topic": "Joins",
            "question": "Which JOIN returns matching rows from both tables?",
            "options": [
                "INNER JOIN",
                "OUTER JOIN",
                "CROSS JOIN",
                "RANDOM JOIN"
            ],
            "answer": 0
        },

        {
            "id": 5,
            "topic": "Transactions",
            "question": "Which property ensures that a transaction is treated as one unit?",
            "options": [
                "Atomicity",
                "Redundancy",
                "Indexing",
                "Sorting"
            ],
            "answer": 0
        }

    ]
}


# =========================================================
# DATABASE
# =========================================================

def get_db():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_db()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            question_id INTEGER NOT NULL,
            selected_answer INTEGER,
            correct_answer INTEGER NOT NULL,
            is_correct INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()

    connection.close()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_topic_scores(subject):

    topics = TOPICS.get(subject, [])

    connection = get_db()

    cursor = connection.cursor()

    scores = {}

    for topic in topics:

        cursor.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(is_correct) AS correct
            FROM attempts
            WHERE subject = ? AND topic = ?
        """, (subject, topic))

        row = cursor.fetchone()

        total = row["total"] or 0
        correct = row["correct"] or 0

        if total == 0:
            scores[topic] = 0
        else:
            scores[topic] = round((correct / total) * 100)

    connection.close()

    return scores


def get_weak_topics(subject):

    scores = get_topic_scores(subject)

    weak_topics = []

    for topic, score in scores.items():

        if score < 60:
            weak_topics.append({
                "topic": topic,
                "score": score
            })

    weak_topics.sort(key=lambda item: item["score"])

    return weak_topics


# =========================================================
# FRONTEND
# =========================================================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/api/health")
def health():

    ai_available = (
        OpenAI is not None
        and bool(os.getenv("OPENAI_API_KEY"))
    )

    return jsonify({
        "status": "online",
        "ai_mode": "live" if ai_available else "demo"
    })


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/api/dashboard")
def dashboard():

    subject = request.args.get(
        "subject",
        "Java"
    )

    topic_scores = get_topic_scores(subject)

    connection = get_db()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(is_correct) AS correct
        FROM attempts
        WHERE subject = ?
    """, (subject,))

    row = cursor.fetchone()

    total = row["total"] or 0
    correct = row["correct"] or 0

    if total:
        overall_score = round(
            (correct / total) * 100
        )
    else:
        overall_score = 0

    cursor.execute("""
        SELECT COUNT(*)
        FROM sessions
        WHERE subject = ?
    """, (subject,))

    sessions = cursor.fetchone()[0]

    connection.close()

    weak_topics = get_weak_topics(subject)

    return jsonify({
        "subject": subject,
        "overall_score": overall_score,
        "practice_sessions": sessions,
        "topic_scores": topic_scores,
        "weak_topics": weak_topics,
        "streak": min(sessions, 7)
    })


# =========================================================
# GET QUIZ
# =========================================================

@app.route("/api/quiz")
def quiz():

    subject = request.args.get(
        "subject",
        "Java"
    )

    questions = QUIZ_DATA.get(
        subject,
        []
    )

    clean_questions = []

    for question in questions:

        clean_questions.append({
            "id": question["id"],
            "topic": question["topic"],
            "question": question["question"],
            "options": question["options"]
        })

    return jsonify({
        "subject": subject,
        "questions": clean_questions
    })


# =========================================================
# SUBMIT QUIZ
# =========================================================

@app.route("/api/submit", methods=["POST"])
def submit_quiz():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data received"
        }), 400

    subject = data.get("subject", "Java")
    answers = data.get("answers", [])

    questions = QUIZ_DATA.get(
        subject,
        []
    )

    question_map = {
        question["id"]: question
        for question in questions
    }

    connection = get_db()

    cursor = connection.cursor()

    correct_count = 0

    results = []

    for submitted in answers:

        question_id = submitted.get("question_id")

        selected_answer = submitted.get(
            "selected_answer"
        )

        question = question_map.get(
            question_id
        )

        if not question:
            continue

        correct_answer = question["answer"]

        is_correct = (
            selected_answer == correct_answer
        )

        if is_correct:
            correct_count += 1

        cursor.execute("""
            INSERT INTO attempts (
                subject,
                topic,
                question_id,
                selected_answer,
                correct_answer,
                is_correct,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            subject,
            question["topic"],
            question_id,
            selected_answer,
            correct_answer,
            1 if is_correct else 0,
            datetime.now().isoformat()
        ))

        results.append({
            "question_id": question_id,
            "topic": question["topic"],
            "correct": is_correct
        })

    total = len(answers)

    cursor.execute("""
        INSERT INTO sessions (
            subject,
            score,
            total,
            created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        subject,
        correct_count,
        total,
        datetime.now().isoformat()
    ))

    connection.commit()

    connection.close()

    percentage = (
        round((correct_count / total) * 100)
        if total > 0
        else 0
    )

    return jsonify({
        "subject": subject,
        "score": correct_count,
        "total": total,
        "percentage": percentage,
        "results": results,
        "weak_topics": get_weak_topics(subject)
    })


# =========================================================
# PERSONALIZED STUDY PLAN
# =========================================================

@app.route("/api/plan")
def study_plan():

    subject = request.args.get(
        "subject",
        "Java"
    )

    weak_topics = get_weak_topics(subject)

    if not weak_topics:

        weak_topics = [
            {
                "topic": topic,
                "score": 0
            }
            for topic in TOPICS.get(
                subject,
                []
            )[:3]
        ]

    selected_topics = weak_topics[:3]

    plan = []

    if len(selected_topics) >= 1:

        plan.append({
            "duration": "15 min",
            "topic": selected_topics[0]["topic"],
            "task": "Review the core concepts and write short notes."
        })

    if len(selected_topics) >= 2:

        plan.append({
            "duration": "15 min",
            "topic": selected_topics[1]["topic"],
            "task": "Solve 3 beginner-level practice questions."
        })

    if len(selected_topics) >= 3:

        plan.append({
            "duration": "15 min",
            "topic": selected_topics[2]["topic"],
            "task": "Attempt a mini challenge without looking at the solution."
        })

    return jsonify({
        "subject": subject,
        "total_duration": "45 minutes",
        "plan": plan
    })


# =========================================================
# AI TUTOR
# =========================================================

def demo_tutor(question, subject):

    question_lower = question.lower()

    if "loop" in question_lower:

        return (
            "Think of a loop as repeating an action until a "
            "condition becomes false. In Java, a for loop is "
            "useful when you know approximately how many times "
            "you want to repeat something."
        )

    if "array" in question_lower:

        return (
            "An array stores multiple values of the same type "
            "in a fixed-size structure. Array indexing normally "
            "starts from 0."
        )

    if "sql" in question_lower:

        return (
            "SQL is used to communicate with relational databases. "
            "For example, SELECT is used to retrieve data from a table."
        )

    return (
        f"Let's learn {subject} step by step. "
        "Start by identifying the concept, understand a small "
        "example, and then solve one simple problem yourself."
    )


@app.route("/api/tutor", methods=["POST"])
def tutor():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "No question received"
        }), 400

    question = data.get(
        "question",
        ""
    ).strip()

    subject = data.get(
        "subject",
        "Java"
    )

    if not question:

        return jsonify({
            "error": "Please enter a question"
        }), 400

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    model = os.getenv(
        "OPENAI_MODEL"
    )

    # -----------------------------------------------------
    # LIVE AI
    # -----------------------------------------------------

    if OpenAI and api_key and model:

        try:

            client = OpenAI(
                api_key=api_key
            )

            response = client.responses.create(

                model=model,

                instructions=(
                    "You are LearnLoop, an adaptive educational tutor. "
                    "Teach in simple language. "
                    "Do not immediately give the answer when a student "
                    "could learn it through a hint. "
                    "Use examples and short explanations. "
                    "The student's subject is "
                    + subject
                    + "."
                ),

                input=question
            )

            return jsonify({
                "answer": response.output_text,
                "mode": "live"
            })

        except Exception as error:

            print("AI error:", error)

    # -----------------------------------------------------
    # DEMO MODE
    # -----------------------------------------------------

    return jsonify({
        "answer": demo_tutor(
            question,
            subject
        ),
        "mode": "demo"
    })


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    initialize_database()

    print("")
    print("========================================")
    print("       LearnLoop AI is running")
    print("========================================")
    print("Open: http://127.0.0.1:5000")
    print("")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )