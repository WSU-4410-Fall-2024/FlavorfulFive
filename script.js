let isFlipped = false;
const app = initializeApp(firebaseConfig);
const db = getDatabase(app);

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

let recipes = []; // Store all fetched recipes from Firebase

// Fetch recipes from Firebase
function fetchRecipes() {
    const recipesRef = ref(db, 'recipes');
    onValue(recipesRef, (snapshot) => {
        recipes = []; // Clear previous recipes
        snapshot.forEach((childSnapshot) => {
            const recipe = childSnapshot.val();
            recipes.push(recipe); // Add each recipe to the array
        });
        displayRecipes(recipes); // Display all recipes initially
    });
}

// Display recipes on the page
function displayRecipes(recipesToShow) {
    const recipeList = document.getElementById('recipeList');
    recipeList.innerHTML = ''; // Clear existing recipes

    recipesToShow.forEach(recipe => {
        const recipeCard = document.createElement('div');
        recipeCard.classList.add('recipe-card');
        recipeCard.innerHTML = `
            <h3>${recipe.recipeName}</h3>
            <p><strong>Ingredients:</strong> ${recipe.ingredient1}, ${recipe.ingredient2}, ${recipe.ingredient3}, ${recipe.ingredient4}, ${recipe.ingredient5}</p>
            <p><strong>Preparation:</strong> ${recipe.preparation}</p>
        `;
        recipeList.appendChild(recipeCard);
    });
}

// Filter recipes based on search input
function filterRecipes() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();

    // Filter recipes by name or ingredients
    const filteredRecipes = recipes.filter(recipe => {
        const recipeName = recipe.recipeName.toLowerCase();
        const ingredients = `${recipe.ingredient1} ${recipe.ingredient2} ${recipe.ingredient3} ${recipe.ingredient4} ${recipe.ingredient5}`.toLowerCase();
        return recipeName.includes(searchTerm) || ingredients.includes(searchTerm);
    });

    displayRecipes(filteredRecipes); // Display only the filtered recipes
}

// Event listener for search input
document.getElementById('searchInput').addEventListener('input', filterRecipes);

// Fetch recipes on page load
window.onload = fetchRecipes;

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
    document.getElementById('userAgreementModal').style.display = 'none';
    alert("Recipe saved successfully!");
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
