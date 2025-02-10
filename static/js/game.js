let startTime

function updateCounts() {
    fetch("/count")
        .then((response) => response.json())
        .then((data) => {
            const wordCountElement = document.getElementById("wordCount")
            wordCountElement.textContent = data.count
            animateWordCount(wordCountElement)
        })
        .catch((error) => console.error("Error fetching counts:", error))
}

function animateWordCount(element) {
    element.classList.add("update-animation")
    setTimeout(() => {
        element.classList.remove("update-animation")
    }, 300)
}

function addEventListeners() {
    document.querySelectorAll(".word").forEach((button) => {
        button.addEventListener("click", (event) => {
            fetch("/submit_word", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ word: event.target.textContent }),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.error) {
                        console.log("Error submitting word:", data.error)
                        window.location.reload()
                    } else {
                        if (data.gameover) {
                            gameOver()
                        } else {
                            const wordCountElement = document.getElementById("wordCount")
                            wordCountElement.textContent = data.count
                            animateWordCount(wordCountElement)
                            if (data.correct) {
                                animateCorrectAnswer(event.target)
                            }
                            displayWords(data)
                        }
                    }
                })
                .catch((error) => console.error("Error submitting word:", error))
        })
    })
}

function animateCorrectAnswer(button) {
    button.classList.add("correct-answer")
    setTimeout(() => {
        button.classList.remove("correct-answer")
    }, 500)
}

function displayWords(data) {
    if (data.shuffle_words) {
        const wordContainer = document.getElementById("wordContainer")
        wordContainer.innerHTML = ""
        data.shuffle_words.forEach((word) => {
            const button = document.createElement("button")
            button.textContent = word
            button.className = "word fade-in"
            wordContainer.appendChild(button)
        })
        addEventListeners()
    } else {
        console.error("shuffle_words is undefined in the response data")
    }
}

function fetchNewWords() {
    fetch("/shuffle_words")
        .then((response) => response.json())
        .then((data) => {
            displayWords(data)
        })
        .catch((error) => console.error("Error fetching new words:", error))
}

function gameOver() {
    window.location.href = "/gameover"
}

function updateTimer() {
    fetch("/start_time")
        .then((response) => response.json())
        .then((data) => {
            startTime = data.start_time
            update()
        })
        .catch((error) => console.error("Error fetching start time:", error))
    const timerElement = document.getElementById("timer")
    timerElement.style.position = "relative"
    timerElement.style.left = "10px"
    timerElement.style.top = "0px"
    function update() {
        const currentTime = new Date().getTime()
        const elapsedTime = currentTime - startTime
        timerElement.textContent = formatTime(elapsedTime)
        requestAnimationFrame(update)
    }
    requestAnimationFrame(update)
}

function formatTime(timestamp) {
    const date = new Date(timestamp)
    const hours = date.getUTCHours().toString().padStart(2, "0")
    const minutes = date.getUTCMinutes().toString().padStart(2, "0")
    const seconds = date.getUTCSeconds().toString().padStart(2, "0")
    return `${hours}:${minutes}:${seconds}`
}

updateTimer()
updateCounts()
fetchNewWords()

