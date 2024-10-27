// Reference the form, sliders, and results container
const mainForm = document.getElementById("main_form");
const moodSelect = document.getElementById("mood");
const sliderEnergy = document.getElementById("slider-energy");
const sliderValence = document.getElementById("slider-valence");
const resultsDiv = document.getElementById("results");
const warn = document.getElementById("warn");

// Function to get form values
function getFormValues() {
    return {
        mood: moodSelect.value,
        energy: sliderEnergy.value,
        valence: sliderValence.value
    };
}

// Function to display recommended songs
function displaySongs(songs) {
    // If no songs were returned, log an error and show a message to the user
    if (!songs || songs.length === 0) {
        console.log("Error: No songs returned.");
        warn.innerHTML ="No recommendations available. Please try again."
        return;
    }

    resultsDiv.innerHTML = '';  // Clear previous results
    songs.forEach(song => {
        const iframe = document.createElement('iframe');
        iframe.src = song.embed_url;
        iframe.width = "300";
        iframe.height = "80";
        iframe.allow = "encrypted-media";
        resultsDiv.appendChild(iframe);
    });
}

// Handle form submission
mainForm.onsubmit = function(event) {
    event.preventDefault();
    warn.innerHTML = ''

    fetch('/recommend', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(getFormValues())
    })
    .then(response => {
        // Check if the response status is OK (200)
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => displaySongs(data.songs))  // Display the songs if the response is good
    .catch(error => {
        console.error('Error:', error);
        warn.innerHTML = 'An error occurred. Please try again later'
    });
};
