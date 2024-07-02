const searchForm = document.getElementById('search-form');
const resultsDiv = document.getElementById('results');

searchForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const formData = new FormData(searchForm);
  
  // Convert FormData to a plain object
  const formObject = {};
  formData.forEach((value, key) => {
    formObject[key] = value;
  });

  // Retrieve token from storage
  const token = localStorage.getItem('authToken');

  if (!token) {
    console.error('Authentication token not found');
    resultsDiv.innerHTML = '<p>Error: Authentication token not found.</p>';
    return;
  }

  try {
    const response = await fetch('/newsapp/api/search/', {
      method: 'POST',
      body: JSON.stringify(formObject), // Include all form data for filters
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `token ${token}` // Include token in Authorization header
      }
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    const data = await response.json();
    // Handle the response data
    displayResults(data); // Function to handle displaying the results
  } catch (error) {
    console.error('Error:', error);
    resultsDiv.innerHTML = '<p>Error fetching articles.</p>';
  }
});

function displayResults(data) {
  // Clear previous results
  resultsDiv.innerHTML = '';
  
  if (data.results && data.results.length > 0) {
    const ul = document.createElement('ul');
    data.results.forEach(article => {
      const li = document.createElement('li');
      li.textContent = article.title; // Adjust based on your data structure
      ul.appendChild(li);
    });
    resultsDiv.appendChild(ul);
  } else {
    resultsDiv.innerHTML = '<p>No articles found.</p>';
  }
}
