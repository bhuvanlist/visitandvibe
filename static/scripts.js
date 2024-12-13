document.getElementById('searchForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const placeName = document.getElementById('placeName').value;
    const resultsDiv = document.getElementById('results');

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ place_name: placeName }),
        });
        const data = await response.json();

        if (data.error) {
            resultsDiv.textContent = `Error: ${data.error}`;
        } else {
            resultsDiv.textContent = `Results: ${JSON.stringify(data.results)}`;
        }
    } catch (error) {
        resultsDiv.textContent = 'An error occurred while searching.';
    }
});
