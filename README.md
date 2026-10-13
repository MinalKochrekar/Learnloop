# Learnloop
# 📚 LearnLoop AI — Your Personalized Learning Companion

LearnLoop AI is an adaptive learning platform designed to help students identify their weak areas, practice technical subjects, and build personalized study plans.

Instead of following the same study plan for everyone, LearnLoop helps students understand where they need improvement and guides them toward more focused learning.

## ✨ Features

### 📊 1. Personalized Dashboard
- View your overall practice score.
- Track your completed practice sessions.
- Monitor your learning streak.
- Visualize your performance across different topics.

### 📝 2. Diagnostic Quiz
- Take quizzes to test your knowledge.
- Practice questions from different technical subjects.
- Receive your score after submitting the quiz.
- Identify topics that need more attention.

### 🎯 3. Weak Topic Detection
- Analyze your quiz performance topic by topic.
- Identify areas where your accuracy is low.
- Focus your learning efforts on topics that need improvement.

### 📅 4. Personalized Study Plan
- Get a study plan based on your performance.
- Review important concepts.
- Practice questions from weaker topics.
- Follow focused learning tasks.

### 🤖 5. AI Learning Tutor
- Ask questions related to your studies.
- Get explanations in simple language.
- Learn concepts with examples and hints.
- Use demo tutoring even when live AI is not configured.

### 💾 6. Progress Tracking
- Store quiz attempts and scores using SQLite.
- Track performance across multiple practice sessions.
- Use previous attempts to calculate topic-level accuracy.

## 📚 Supported Subjects

LearnLoop AI currently includes practice questions for:

- **Java** — Variables, Loops, OOP, Exceptions, Collections
- **DSA** — Arrays, Strings, Linked Lists, Stacks & Queues, Sorting
- **DBMS** — SQL, Keys, Normalization, Joins, Transactions

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Flask
- Flask-CORS

### Database
- SQLite

### AI Integration
- OpenAI API integration for live tutoring
- Demo tutoring mode when live AI is unavailable

## 📁 Project Structure

```text
LearnLoop_AI/
│
├── backend/
│   ├── app.py
│   ├── learnloop.db
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
└── README.md
