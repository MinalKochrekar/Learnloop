const API = "http://127.0.0.1:5000/api";

let currentSubject = "Java";
let quizQuestions = [];


// =====================================================
// INITIAL LOAD
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadDashboard();

        loadQuiz();

        loadPlan();

        loadWeakTopics();

    }
);


// =====================================================
// SUBJECT CHANGE
// =====================================================

function changeSubject() {

    currentSubject =
        document.getElementById(
            "subject"
        ).value;

    loadDashboard();

    loadQuiz();

    loadPlan();

    loadWeakTopics();

}


// =====================================================
// NAVIGATION
// =====================================================

function showSection(sectionId) {

    document
        .querySelectorAll(".section")
        .forEach(section => {

            section.classList.remove(
                "active"
            );

        });


    const section =
        document.getElementById(
            sectionId
        );


    if (section) {

        section.classList.add(
            "active"
        );

    }


    document
        .querySelectorAll(".nav-item")
        .forEach(button => {

            button.classList.remove(
                "active"
            );

        });


    const buttons =
        document.querySelectorAll(
            ".nav-item"
        );


    buttons.forEach(button => {

        if (
            button.innerText
                .toLowerCase()
                .includes(
                    sectionId === "dashboard"
                        ? "dashboard"
                        : sectionId === "diagnostic"
                            ? "diagnostic"
                            : sectionId === "focus"
                                ? "focus"
                                : "plan"
                )
        ) {

            button.classList.add(
                "active"
            );

        }

    });


    if (sectionId === "focus") {

        loadWeakTopics();

    }


    if (sectionId === "plan") {

        loadPlan();

    }

}


// =====================================================
// DASHBOARD
// =====================================================

async function loadDashboard() {

    try {

        const response =
            await fetch(
                `${API}/dashboard?subject=${currentSubject}`
            );


        const data =
            await response.json();


        document.getElementById(
            "overallScore"
        ).innerText =
            `${data.overall_score}%`;


        document.getElementById(
            "sessions"
        ).innerText =
            data.practice_sessions;


        document.getElementById(
            "streak"
        ).innerText =
            data.streak;


        document.getElementById(
            "sidebarStreak"
        ).innerText =
            `${data.streak} days`;


        renderTopicMap(
            data.topic_scores
        );


        renderFocus(
            data.weak_topics
        );

    }
    catch (error) {

        console.error(
            "Dashboard error:",
            error
        );

    }

}


// =====================================================
// TOPIC MAP
// =====================================================

function renderTopicMap(scores) {

    const container =
        document.getElementById(
            "topicMap"
        );


    container.innerHTML = "";


    Object.entries(scores)
        .forEach(
            ([topic, score]) => {

                container.innerHTML += `

                    <div class="topic-row">

                        <span class="topic-name">
                            ${topic}
                        </span>

                        <div class="progress">

                            <div
                                class="progress-fill"
                                style="width:${score}%"
                            ></div>

                        </div>

                        <span class="topic-score">
                            ${score}%
                        </span>

                    </div>

                `;

            }
        );

}


// =====================================================
// FOCUS
// =====================================================

function renderFocus(weakTopics) {

    const container =
        document.getElementById(
            "focusContent"
        );


    if (!weakTopics.length) {

        container.innerHTML = `

            <p>
                Great work! You don't have
                any major weak areas yet.
            </p>

            <button
                class="secondary-btn"
                onclick="showSection('diagnostic')"
            >
                Practice again
            </button>

        `;

        return;

    }


    const weakest =
        weakTopics[0];


    container.innerHTML = `

        <div style="margin-bottom:15px">

            <strong>
                ${weakest.topic}
            </strong>

            <div class="progress" style="margin-top:8px">

                <div
                    class="progress-fill"
                    style="width:${weakest.score}%"
                ></div>

            </div>

            <small>
                Current confidence: ${weakest.score}%
            </small>

        </div>

        <button
            class="secondary-btn"
            onclick="showSection('plan')"
        >
            Build my study plan →
        </button>

    `;

}


// =====================================================
// QUIZ
// =====================================================

async function loadQuiz() {

    const container =
        document.getElementById(
            "quizContainer"
        );


    container.innerHTML =
        `<div class="loading">
            Loading diagnostic...
        </div>`;


    try {

        const response =
            await fetch(
                `${API}/quiz?subject=${currentSubject}`
            );


        const data =
            await response.json();


        quizQuestions =
            data.questions;


        container.innerHTML = "";


        quizQuestions.forEach(
            (question, index) => {

                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "question-card";


                let optionsHTML = "";


                question.options.forEach(
                    (option, optionIndex) => {

                        optionsHTML += `

                            <label class="option">

                                <input
                                    type="radio"
                                    name="question-${question.id}"
                                    value="${optionIndex}"
                                >

                                ${option}

                            </label>

                        `;

                    }
                );


                card.innerHTML = `

                    <span class="question-number">
                        QUESTION ${index + 1}
                        · ${question.topic}
                    </span>

                    <h3>
                        ${question.question}
                    </h3>

                    ${optionsHTML}

                `;


                container.appendChild(
                    card
                );

            }
        );

    }
    catch (error) {

        container.innerHTML = `
            <div class="loading">
                Could not load quiz.
            </div>
        `;

        console.error(
            error
        );

    }

}


// =====================================================
// SUBMIT QUIZ
// =====================================================

async function submitQuiz() {

    const answers = [];


    quizQuestions.forEach(
        question => {

            const selected =
                document.querySelector(
                    `input[name="question-${question.id}"]:checked`
                );


            if (selected) {

                answers.push({

                    question_id:
                        question.id,

                    selected_answer:
                        Number(
                            selected.value
                        )

                });

            }

        }
    );


    if (
        answers.length !==
        quizQuestions.length
    ) {

        alert(
            "Please answer all questions before submitting."
        );

        return;

    }


    try {

        const response =
            await fetch(
                `${API}/submit`,
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        subject:
                            currentSubject,

                        answers:
                            answers

                    })

                }
            );


        const data =
            await response.json();


        const result =
            document.getElementById(
                "quizResult"
            );


        result.classList.remove(
            "hidden"
        );


        result.innerHTML = `

            <h3>
                Diagnostic complete 🎯
            </h3>

            <p style="margin-top:8px">

                You scored
                <strong>
                    ${data.score}/${data.total}
                </strong>

                (${data.percentage}%).

            </p>

            <p style="margin-top:8px">

                LearnLoop has updated your
                topic map and personalized plan.

            </p>

            <button
                class="secondary-btn"
                style="margin-top:14px"
                onclick="showSection('focus')"
            >
                See where to focus →
            </button>

        `;


        loadDashboard();

        loadWeakTopics();

        loadPlan();

    }
    catch (error) {

        console.error(
            error
        );

        alert(
            "Something went wrong while submitting."
        );

    }

}


// =====================================================
// WEAK TOPICS
// =====================================================

async function loadWeakTopics() {

    const container =
        document.getElementById(
            "weakTopics"
        );


    try {

        const response =
            await fetch(
                `${API}/dashboard?subject=${currentSubject}`
            );


        const data =
            await response.json();


        container.innerHTML = "";


        if (
            !data.weak_topics.length
        ) {

            container.innerHTML = `

                <div class="weak-card">

                    <h3>
                        No major gaps yet 🎉
                    </h3>

                    <p>
                        Complete the diagnostic to
                        get a more accurate analysis.
                    </p>

                </div>

            `;

            return;

        }


        data.weak_topics.forEach(
            item => {

                container.innerHTML += `

                    <div class="weak-card">

                        <span class="section-label">
                            NEEDS ATTENTION
                        </span>

                        <h3 style="margin-top:8px">
                            ${item.topic}
                        </h3>

                        <div class="score">
                            ${item.score}%
                        </div>

                        <p>
                            This is currently one of
                            your lowest-confidence areas.
                            Spend your next study session
                            strengthening it.
                        </p>

                    </div>

                `;

            }
        );

    }
    catch (error) {

        console.error(
            error
        );

    }

}


// =====================================================
// STUDY PLAN
// =====================================================

async function loadPlan() {

    const container =
        document.getElementById(
            "planContainer"
        );


    try {

        const response =
            await fetch(
                `${API}/plan?subject=${currentSubject}`
            );


        const data =
            await response.json();


        container.innerHTML = "";


        data.plan.forEach(
            item => {

                container.innerHTML += `

                    <div class="plan-card">

                        <div class="plan-time">
                            ${item.duration}
                        </div>

                        <div>

                            <h3>
                                ${item.topic}
                            </h3>

                            <p>
                                ${item.task}
                            </p>

                        </div>

                    </div>

                `;

            }
        );

    }
    catch (error) {

        console.error(
            error
        );

    }

}


// =====================================================
// AI TUTOR
// =====================================================

function openTutor() {

    document
        .getElementById(
            "tutorModal"
        )
        .classList.remove(
            "hidden"
        );

}


function closeTutor() {

    document
        .getElementById(
            "tutorModal"
        )
        .classList.add(
            "hidden"
        );

}


async function askTutor() {

    const question =
        document.getElementById(
            "tutorQuestion"
        ).value.trim();


    if (!question) {

        alert(
            "Please enter a question."
        );

        return;

    }


    const answerBox =
        document.getElementById(
            "tutorAnswer"
        );


    answerBox.classList.remove(
        "hidden"
    );


    answerBox.innerHTML =
        "Thinking...";


    try {

        const response =
            await fetch(
                `${API}/tutor`,
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        subject:
                            currentSubject,

                        question:
                            question

                    })

                }
            );


        const data =
            await response.json();


        answerBox.innerHTML = `

            <strong>
                LearnLoop:
            </strong>

            <p style="margin-top:8px">
                ${formatAnswer(
                    data.answer
                )}
            </p>

        `;

    }
    catch (error) {

        answerBox.innerHTML =
            "Sorry, something went wrong.";

        console.error(
            error
        );

    }

}


// =====================================================
// SIMPLE ANSWER FORMATTER
// =====================================================

function formatAnswer(text) {

    return text
        .replace(
            /\n/g,
            "<br>"
        );

}