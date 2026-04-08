const API_URL = 'http://localhost:8000';

document.getElementById('analyze-btn').addEventListener('click', async () => {
  const btn = document.getElementById('analyze-btn');
  const spinner = document.getElementById('spinner');
  const result = document.getElementById('result');
  const error = document.getElementById('error');

  // Reset state
  btn.disabled = true;
  spinner.classList.add('active');
  result.classList.remove('active');
  error.classList.remove('active');

  try {
    // Get the active tab's text content
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    const [{ result: pageText }] = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        // Extract main article text from the page
        const article = document.querySelector('article');
        if (article) return article.innerText;

        const main = document.querySelector('main, [role="main"]');
        if (main) return main.innerText;

        // Fallback: all paragraph text
        const paragraphs = document.querySelectorAll('p');
        return Array.from(paragraphs).map(p => p.innerText).join(' ');
      },
    });

    if (!pageText || pageText.trim().length < 50) {
      throw new Error('Could not extract enough text from this page');
    }

    // Send to API
    const response = await fetch(`${API_URL}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: pageText.trim().slice(0, 5000) }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || 'API request failed');
    }

    const data = await response.json();

    // Display result
    const badge = document.getElementById('badge');
    const badgeLabel = document.getElementById('badge-label');
    const confidence = document.getElementById('confidence');
    const wordsList = document.getElementById('words-list');

    const isFake = data.label === 'FAKE';
    badge.className = `badge ${isFake ? 'fake' : 'real'}`;
    badgeLabel.textContent = data.label;
    confidence.textContent = `Confidence: ${(data.confidence * 100).toFixed(1)}%`;

    wordsList.innerHTML = data.top_words
      .slice(0, 8)
      .map(w => `
        <div class="word-item">
          <span class="word-name">${w.word}</span>
          <span class="word-weight ${w.weight > 0 ? 'positive' : 'negative'}">
            ${w.weight > 0 ? '+' : ''}${w.weight.toFixed(4)}
          </span>
        </div>
      `)
      .join('');

    result.classList.add('active');
  } catch (err) {
    error.textContent = err.message;
    error.classList.add('active');
  } finally {
    btn.disabled = false;
    spinner.classList.remove('active');
  }
});
