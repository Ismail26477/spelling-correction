// Add blur effect to all sections while typing
// Clear and blur the output box and errors tab while typing
function handleTyping() {
    const outputSection = document.getElementById('output-section');
    const correctedText = document.getElementById('corrected-text');
    const tabs = document.getElementById('tabs');
    const tabContents = document.querySelectorAll('.tab-content');

    // Clear the content of the corrected text and error lists
    correctedText.textContent = "The corrected text will appear here after analysis.";
    document.getElementById('all-errors').innerHTML = "";
    document.getElementById('capitalization-errors').innerHTML = "";
    document.getElementById('grammar-errors').innerHTML = "";
    document.getElementById('spelling-errors').innerHTML = "";
    document.getElementById('punctuation-errors').innerHTML = "";

    // Reset the error counts in the tabs
    document.querySelector('[data-tab="all"]').textContent = "All Errors (0)";
    document.querySelector('[data-tab="capitalization"]').textContent = "Capitalization (0)";
    document.querySelector('[data-tab="grammar"]').textContent = "Grammar (0)";
    document.querySelector('[data-tab="spelling"]').textContent = "Spelling (0)";
    document.querySelector('[data-tab="punctuation"]').textContent = "Punctuation (0)";

    // Add blur effect to the output section and tabs
    outputSection.classList.add('blur');
    tabs.classList.add('blur');
    tabContents.forEach(tab => tab.classList.add('blur'));
}

// Remove blur effect after analysis
function removeBlur() {
    const outputSection = document.getElementById('output-section');
    const tabs = document.getElementById('tabs');
    const tabContents = document.querySelectorAll('.tab-content');

    outputSection.classList.remove('blur');
    tabs.classList.remove('blur');
    tabContents.forEach(tab => tab.classList.remove('blur'));
}

async function analyzeText() {
    const text = document.querySelector('#text-input').value;

    if (!text) {
        alert("Please enter text for analysis.");
        return;
    }

    const response = await fetch("/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
    });

    if (response.ok) {
        const data = await response.json();
        document.getElementById('corrected-text').textContent = data.corrected_text;

        // Update error counts and error lists
        const errorCounts = data.error_counts;
        document.querySelector('[data-tab="all"]').textContent = `All Errors (${errorCounts.all})`;
        document.querySelector('[data-tab="capitalization"]').textContent = `Capitalization (${errorCounts.capitalization})`;
        document.querySelector('[data-tab="grammar"]').textContent = `Grammar (${errorCounts.grammar})`;
        document.querySelector('[data-tab="spelling"]').textContent = `Spelling (${errorCounts.spelling})`;
        document.querySelector('[data-tab="punctuation"]').textContent = `Punctuation (${errorCounts.punctuation})`;

        // Populate error lists
        document.getElementById('all-errors').innerHTML = data.errors.all.map(err => `<li>${err}</li>`).join('');
        document.getElementById('capitalization-errors').innerHTML = data.errors.capitalization.map(err => `<li>${err}</li>`).join('');
        document.getElementById('grammar-errors').innerHTML = data.errors.grammar.map(err => `<li>${err}</li>`).join('');
        document.getElementById('spelling-errors').innerHTML = data.errors.spelling.map(err => `<li>${err}</li>`).join('');
        document.getElementById('punctuation-errors').innerHTML = data.errors.punctuation.map(err => `<li>${err}</li>`).join('');

        // Remove blur effect
        removeBlur();
    } else {
        alert("Error analyzing text. Please try again.");
    }
}



function updateErrorList(errors, errorCounts) {
    const errorCategories = ['all', 'capitalization', 'grammar', 'spelling', 'punctuation'];

    errorCategories.forEach(category => {
        // Update error count in the tab
        const tabElement = document.querySelector(`.tab[data-tab="${category}"]`);
        tabElement.textContent = `${capitalize(category)} (${errorCounts[category]})`;

        // Update error list
        const errorList = document.getElementById(`${category}-errors`);
        errorList.innerHTML = '';

        errors[category].forEach(errorDetail => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <strong>Before:</strong> ${errorDetail.before} 
                <span class="error-word">${errorDetail.error}</span> 
                <strong>After:</strong> <span class="corrected-word">${errorDetail.correction}</span>
                ${errorDetail.after}
            `;
            errorList.appendChild(listItem);
        });
    });
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });

    document.getElementById(tabName).classList.add('active');
    document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('active');
}
