function updateLeaderboard() {
    fetch('/scores')
        .then(response => response.json())
        .then(data => {
            const leaderboard = document.getElementById('leaderboard');
            const table = document.createElement('table');

            const headerRow = document.createElement('tr');
            ['Rank', 'Player', 'Difficulty', 'Score', 'Duration'].forEach(headerText => {
                const header = document.createElement('th');
                header.textContent = headerText;
                headerRow.appendChild(header);
            });
            table.appendChild(headerRow);

            data.forEach((score, index) => {
                const row = document.createElement('tr');
                [index + 1, score.username, score.difficulty, score.score, score.duration].forEach(text => {
                    const cell = document.createElement('td');
                    cell.textContent = text;
                    row.appendChild(cell);
                });
                table.appendChild(row);
            });

            leaderboard.innerHTML = '';
            leaderboard.appendChild(table);
        })
        .catch(error => console.error('Error fetching scores:', error));
}

updateLeaderboard();