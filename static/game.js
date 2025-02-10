function updateCounts() {
    fetch('/count')
        .then(response => response.json())
        .then(data => {
            document.getElementById('wordCount').textContent = data.count;
        })
        .catch(error => console.error('Error fetching counts:', error));
}

function addEventListeners() {
    document.querySelectorAll('.word').forEach(function (button) {
        button.addEventListener('click', function (event) {
            fetch('/submit_word', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ word: event.target.textContent })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.gameover) {
                        gameOver();
                    } else {
                        updateCounts();
                        displayWords(data);
                    }
                })
                .catch(error => console.error('Error submitting word:', error));
        });
    });
}

function displayWords(data) {
    if (data.shuffle_words) {
        const wordContainer = document.getElementById('wordContainer');
        wordContainer.innerHTML = '';
        data.shuffle_words.forEach(word => {
            const button = document.createElement('button');
            button.textContent = word;
            button.className = 'word fade-in';
            wordContainer.appendChild(button);
        });
        addEventListeners();
    } else {
        console.error('shuffle_words is undefined in the response data');
    }
}


function fetchNewWords() {
    fetch('/shuffle_words')
        .then(response => response.json())
        .then(data => {
            displayWords(data);
        })
        .catch(error => console.error('Error fetching new words:', error));
}

function gameOver() {
    window.location.href = '/gameover';
}

function updateTimer() {
    fetch('/start_time')
        .then(response => response.json())
        .then(data => {
            startTime = data.start_time;
            update();
        })
        .catch(error => console.error('Error fetching start time:', error));
    const timerElement = document.getElementById('timer');
    timerElement.style.position = 'relative'; // Keep the timer position relative
    timerElement.style.left = '10px'; // Adjust the left position as needed
    timerElement.style.top = '0px'; // Keep the top position as needed
    function update() {
        const currentTime = new Date().getTime();
        const elapsedTime = currentTime - startTime;
        timerElement.textContent = formatTime(elapsedTime);
        requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    const hours = date.getUTCHours().toString().padStart(2, '0');
    const minutes = date.getUTCMinutes().toString().padStart(2, '0');
    const seconds = date.getUTCSeconds().toString().padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
}

updateTimer();
updateCounts();
fetchNewWords();