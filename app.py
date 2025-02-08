import time
import random
from flask import Flask, redirect, render_template, request, url_for, session
from Score import Score
from Base import Base
from utils import format_time
import fake_word_generator
from sqlalchemy import case, create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv("ENGLISH_PROJECT_SECRET_KEY", "BAD_SECRET_KEY")

word_set = fake_word_generator.load_word_list("words_alpha.txt")
# Create a Markov chain with the word list and order 3
markov_chain_easy = fake_word_generator.MarkovChain(word_set, order=1)
markov_chain_normal = fake_word_generator.MarkovChain(word_set, order=2)
markov_chain_hard = fake_word_generator.MarkovChain(word_set, order=3)


# Create an SQLite engine. This creates a file 'scores.db' in your directory.
engine = create_engine("sqlite:///scores.db", echo=True)

# Create all tables in the database based on the defined models
Base.metadata.create_all(engine)

# Create a session for interacting with the database
Session = sessionmaker(bind=engine)
session_db = Session()


@app.route("/")
def home():
    session.clear()
    return render_template("index.html")


@app.route("/game/<difficulty>")
def game(difficulty: str):
    if "start_time" not in session:
        session.clear()
        session["start_time"] = time.time()
        session["difficulty"] = difficulty
        session["score"] = 0
        session["duration_seconds"] = 0
        shuffle_words_difficulty()
    app.logger.debug(session["start_time"])
    return render_template("game.html")


@app.route("/shuffle_words")
def shuffle_words():
    if "fake_words" not in session:
        session.clear()
        return {"error": "Session expired"}
    if "real_words" not in session:
        session.clear()
        return {"error": "Session expired"}
    shuffle_words = session["fake_words"] + session["real_words"]
    random.shuffle(shuffle_words)
    return {"shuffle_words": shuffle_words}


def shuffle_words_difficulty():
    if "difficulty" not in session:
        session.clear()
        return render_template("error.html", message="Session expired")
    match session["difficulty"]:
        case "easy":
            real_words, fake_words = fake_word_generator.fake_and_real_word(
                markov_chain_easy, word_set, 2, 1
            )
        case "normal":
            real_words, fake_words = fake_word_generator.fake_and_real_word(
                markov_chain_normal, word_set, 2, 1
            )
        case "hard":
            real_words, fake_words = fake_word_generator.fake_and_real_word(
                markov_chain_hard, word_set, 2, 1
            )
    session["fake_words"] = fake_words
    session["real_words"] = real_words


@app.route("/submit_score", methods=["POST"])
def submit_score():
    username = request.form["name"]
    difficulty = session["difficulty"]
    score = session["score"]
    duration_seconds = session["duration_seconds"]

    new_score = Score(
        username=username,
        difficulty=difficulty,
        score=score,
        duration_seconds=duration_seconds,
    )
    session_db.add(new_score)
    session_db.commit()
    session["score"] = 0
    session["duration_seconds"] = 0

    return redirect(url_for("home"))


@app.route("/gameover")
def gameover():
    if "duration_seconds" not in session:
        return redirect(url_for("home"))
    format_duration = format_time(session["duration_seconds"])
    return render_template(
        "gameover.html", score=session["score"], duration=format_duration
    )


@app.route("/submit_word", methods=["POST"])
def submit_word():
    data = request.get_json()
    app.logger.debug(data)
    submitted_word = data["word"]
    if submitted_word in session["fake_words"]:
        session["score"] += 1
        shuffle_words_difficulty()
        return {"score": session["score"]}
    else:
        session["score"]
        if "start_time" in session:
            session["duration_seconds"] = time.time() - session["start_time"]
            app.logger.debug(session["duration_seconds"])
            session.pop("start_time")
        else:
            session["duration_seconds"] = 0
        return {"score": session["score"], "gameover": True}


@app.route("/scores")
def scores():
    scores = (
        session_db.query(Score)
        .order_by(
            (
                (Score.score / Score.duration_seconds)
                * case(
                    (Score.difficulty == "hard", 1.5),
                    (Score.difficulty == "normal", 1),
                    (Score.difficulty == "easy", 0.5),
                    else_=1,
                )
            ).desc()
        )
        .limit(10)
    )
    return [score.to_dict() for score in scores]

@app.route("/scoresFull")
def scoresFull():
    scores = (
        session_db.query(Score)
        .order_by(
            (
                (Score.score / Score.duration_seconds)
                * case(
                    (Score.difficulty == "hard", 1.5),
                    (Score.difficulty == "normal", 1),
                    (Score.difficulty == "easy", 0.5),
                    else_=1,
                )
            ).desc()
        )
    )
    return [score.to_dict() for score in scores]

@app.route("/leaderboard")
def leaderboard():
    return render_template("leaderboard.html")

@app.route("/count")
def count():
    return {"count": session["score"]}


@app.route("/start_time")
def start_time():
    return {"start_time": round(session["start_time"] * 10**3)}


if __name__ == "__main__":
    app.run(debug=True)
