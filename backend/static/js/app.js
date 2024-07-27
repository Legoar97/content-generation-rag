// static/js/app.js
document.getElementById('article-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const title = document.getElementById('title').value;
    const content = document.getElementById('content').value;

    const response = await fetch('/news/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title, content })
    });

    const result = await response.json();
    document.getElementById('result').innerText = `Sentiment: ${result.sentiment}`;
});
