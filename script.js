let isFlipped = false;
const app = initializeApp(firebaseConfig);
const db = getDatabase(app);
let recipes = [] //declared an array named recipes that will store all fetched recipes from Firebase

//Defines a function fetchRecipes that will retrieve recipe data from a firebase database

function fetchRecipes() {
    const recipesRef = ref(db, 'recipes'); //creates a reference to the recipes collection in Firebase database (is firebase database defined as 'db'?)
    onValue(recipesRef, (snapshot) => { //looks for real-time updates to the recipes data. when there's a change, this will update the recipes array
        recipes = []; // Clear previous recipes to avoid duplicates
        snapshot.forEach((childSnapshot) => { //iterates through each recipe in the Firebase database snapshot
            const recipe = childSnapshot.val(); // retrieved data of each recipe entry as an object and stores it in the recipe variable
            recipes.push(recipe); // Add each recipe to the array
        });
        displayRecipes(recipes); // Calls displayRecipes function and passes the full recipes array to display all recipes on page
}

// Display recipes on the page
function displayRecipes(recipesToShow) { // function named displayRecipes that takes an array recipesToShow and displays each recipe 
    const recipeList = document.getElementById('recipeList'); // selects the HTML element with ID recipeList 
    recipeList.innerHTML = ''; // Clear existing recipes to avoid duplicates
    recipesToShow.forEach(recipe => { // loops through each recipe in the recipesToShow array
        const recipeCard = document.createElement('div'); //creates a new div element to act as a container for a single recipe
        recipeCard.classList.add('recipe-card'); //adds a CSS Class recipeCard to the div 
        recipeCard.innerHTML = ` //sets the innerHTML of the recipe card to display recipe's details
            <h3>${recipe.recipeName}</h3>
            <p><strong>Ingredients:</strong> ${recipe.ingredient1}, ${recipe.ingredient2}, ${recipe.ingredient3}, ${recipe.ingredient4}, ${recipe.ingredient5}</p>
            <p><strong>Preparation:</strong> ${recipe.preparation}</p>
        `; //displays recipe name, list of ingredients, and instructions
        recipeList.appendChild(recipeCard); // adds the recipeCard to recipeList 
    });
}

// Filter recipes based on search input
function filterRecipes() { // defines a function filterRecipes that filters recipes based on user input in a search box
    const searchTerm = document.getElementById('searchInput').value.toLowerCase(); //retrieves the text entered in the search input box and converts it to lowercase and stores in searchTerm

    // Filter recipes by name or ingredients
    const filteredRecipes = recipes.filter(recipe => { //creates a new array filteredRecipes by filtering the recipes array to only include recipes that match the search term
        const recipeName = recipe.recipeName.toLowerCase(); // converts recipe name to lowercase
        const ingredients = `${recipe.ingredient1} ${recipe.ingredient2} ${recipe.ingredient3} ${recipe.ingredient4} ${recipe.ingredient5}`.toLowerCase(); //combines all ingredients into a single lowercase string for easier searching
        return recipeName.includes(searchTerm) || ingredients.includes(searchTerm);
    }); //checks if the searchTerm is included in either recipe name or ingredients. if it is, adds to filteredRecipes

    displayRecipes(filteredRecipes); //Calls displayRecipes with filteredRecipes to update the displayed recipes based on the search term.
}

// Event listener for search input
document.getElementById('searchInput').addEventListener('input', filterRecipes); // Adds an event listener to the search input box. Every time the user types, it calls filterRecipes to filter recipes in real-time.

// Fetch recipes on page load
window.onload = fetchRecipes; // Calls fetchRecipes when the page loads, populating the page with recipes from Firebase.
const firebaseConfig = {
    apiKey: "AIzaSyC-2pPQQFE91QhJ1jjoAeOmECFCVdkqDzU",
    authDomain: "flavor-1a23c.firebaseapp.com",
    databaseURL: "https://flavor-1a23c-default-rtdb.firebaseio.com",
    projectId: "flavor-1a23c",
    storageBucket: "flavor-1a23c.appspot.com",
    messagingSenderId: "185874751125",
    appId: "1:185874751125:web:9c98cfb3aa74062418459c",
    measurementId: "G-KB859RPX9N"
  };

function flipCard() {
    const card = document.getElementById('recipeCard');
    if (!isFlipped) {
        card.classList.add('flipped');
        isFlipped = true;
        document.getElementById('left-arrow').style.display = 'block'; 
        document.getElementById('right-arrow').style.display = 'none'; 
    } else {
        card.classList.remove('flipped');
        isFlipped = false;
        document.getElementById('left-arrow').style.display = 'none'; 
        document.getElementById('right-arrow').style.display = 'block'; 
    }
}

function flipCardBack() {
    const card = document.getElementById('recipeCard');
    card.classList.remove('flipped');
    isFlipped = false;
    document.getElementById('left-arrow').style.display = 'none'; 
    document.getElementById('right-arrow').style.display = 'block'; 
}

function confirmSaveRecipe() {
    const recipeName = document.getElementById('recipe-name').value.trim();
    if (recipeName.length < 3) {
        alert("Recipe name must be at least 3 characters.");
        return;
    }

    const ingredients = document.querySelectorAll('.ingredient');
    const preparationInstructions = document.getElementById("preparation").value.trim();

    let allValid = true;

    ingredients.forEach((input) => {
        if (input.value.trim().length < 3) {
            allValid = false;
        }
    });
    if (preparationInstructions.length < 20) {
        alert("Preparation instructions must be at least 20 characters long.");
        return;
}

    if (!allValid) {
        alert("Each ingredient must be at least 3 characters long.");
        return;
    }

    // If validation passes, flip the card to show the back side
    flipCard();  // This line flips the card to show the ingredients input

    // Now display the modal for user agreement
    document.getElementById('userAgreementModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('userAgreementModal').style.display = 'none';
}

function saveModal() {
    const successMessage = document.getElementById('successMessage');
    successMessage.style.display = 'block';

    // Optional: Hide the message after a few seconds
    setTimeout(() => {
        successMessage.style.display = 'none';
    }, 3000); // Hide after 3 seconds
    document.getElementById('userAgreementModal').style.display = 'none';

}

function clearFields() {
    document.getElementById("recipe-name").value = "";
    document.getElementById("recp1").value = "";
    document.getElementById("recp2").value = "";
    document.getElementById("recp3").value = "";
    document.getElementById("recp4").value = "";
    document.getElementById("recp5").value = "";
    document.getElementById("preparation").value = "";
}

function saveFinalRecipe() {
    const checkbox = document.getElementById('agreement-checkbox');
    if (checkbox.checked) {
        alert("Recipe saved successfully!");
        
        // Clear inputs after saving
    
        const ingredients = document.querySelectorAll('.ingredient');
        const newRecipeRef = push(ref(db, 'recipes'));
        set(newRecipeRef, {
            recipeName: document.getElementById("recipe-name").value.trim(),
            ingredient1: document.getElementById("recp1").value.trim(),
            ingredient2: document.getElementById("recp2").value.trim(),
            ingredient3: document.getElementById("recp3").value.trim(),
            ingredient4: document.getElementById("recp4").value.trim(),
            ingredient5: document.getElementById("recp5").value.trim(),
            preparation: document.getElementById("preparation").value
 }).then(() => {
            alert("Recipe saved successfully!");
            clearFields(); // Clear all input fields
            closeModal(); // Close the modal after saving
            flipCardBack(); // Optionally, flip the card back after saving
        }).catch((error) => {
            console.error("Error saving recipe: ", error);
        });
    } else {
        alert("You must agree to save your recipe.");
    }
}
// Close modal when clicking outside of the modal
window.onclick = function(event) {
    const modal = document.getElementById('userAgreementModal');
    if (event.target === modal) {
        closeModal();
    }
}

