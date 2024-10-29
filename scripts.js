document.getElementById('send-button').addEventListener('click', function() {
    const userInput = document.getElementById('user-input');
    const userMessage = userInput.value.trim();

    if (userMessage) {
        appendMessage(userMessage, 'user');
        userInput.value = '';

        setTimeout(() => {
            const botResponse = getBotResponse(userMessage);
            appendMessage(botResponse, 'bot');
        }, 1000);
    }
});

function appendMessage(message, sender) {
    const chatLog = document.getElementById('chat-log');
    const messageElement = document.createElement('p');
    messageElement.classList.add(sender);
    messageElement.textContent = message;
    chatLog.appendChild(messageElement);
    chatLog.scrollTop = chatLog.scrollHeight; 
}

document.getElementById('send-button').addEventListener('click', function() {
    const userInput = document.getElementById('user-input');
    const userMessage = userInput.value.trim();

    if (userMessage) {
        appendMessage(userMessage, 'user');
        userInput.value = '';

        setTimeout(() => {
            const botResponse = getBotResponse(userMessage);
            appendMessage(botResponse, 'bot');
        }, 1000);
    }
});

function appendMessage(message, sender) {
    const chatLog = document.getElementById('chat-log');
    const messageElement = document.createElement('p');
    messageElement.classList.add(sender);
    messageElement.textContent = message;
    chatLog.appendChild(messageElement);
    chatLog.scrollTop = chatLog.scrollHeight; 
}

function getBotResponse(userMessage) {
    const lowerCaseMessage = userMessage.toLowerCase();
    

    if (lowerCaseMessage.includes("hello") || lowerCaseMessage.includes("hey") || lowerCaseMessage.includes("whats up")) {
        return "Hi there! How can I help you?";
    } else if (lowerCaseMessage.includes("whats your name")) {
        return "I'm a Recipe Assistant Bot!";
    } else if (lowerCaseMessage.includes("how can I contact support")) {
        return "You can reach us at support@recipe.com.";
    } else if (lowerCaseMessage.includes("chicken")) {
        return "You can check out 'Saved Recipes' or browse 'My Recipes' for chicken dishes!";
    } else if (lowerCaseMessage.includes("cuisines")) {
        return "We have Italian, American, Mexican, Asian, and Baked Goodies!";
    } else if (lowerCaseMessage.includes("5 ingredient recipes")) {
        return "5 ingredient recipes are simple and easy to cook. They make meal prep quick and fun!";
    } else if (lowerCaseMessage.includes("saved recipes")) {
        return "You can find your saved recipes under the 'Saved Recipes' section in the navigation bar.";
    } else if (lowerCaseMessage.includes("dinner")) {
        return "How about trying one of our easy Italian recipes or a quick 5 ingredient meal?";
    } else if (lowerCaseMessage.includes("vegetarian")) {
        return "Absolutely! We have a variety of vegetarian recipes available in the Italian and Asian sections.";
    } else if (lowerCaseMessage.includes("save a recipe")) {
        return "To save a recipe, simply click on the 'Save Recipe' button on the recipe page.";
    } else if (lowerCaseMessage.includes("easiest recipe")) {
        return "Our 5 ingredient recipes are designed for quick and easy cooking. Check them out!";
    } else if (lowerCaseMessage.includes("dessert recipe")) {
        return "You might enjoy trying our baked goodies for some delicious dessert options!";
    } else if (lowerCaseMessage.includes("healthy recipes")) {
        return "Yes! We offer healthy recipes in various cuisines, focusing on fresh ingredients.";
    } else if (lowerCaseMessage.includes("recipe reviews")) {
        return "You can find user reviews on each recipe page, which can help you decide what to try!";
    } else if (lowerCaseMessage.includes("pasta")) {
        return "For perfect pasta, boil it in salted water until al dente, then drain and toss with your favorite sauce!";
    } else if (lowerCaseMessage.includes("chicken breast")) {
        return "You can grill, bake, or sauté chicken breast. It's versatile and easy to cook!";
    } else if (lowerCaseMessage.includes("meal prep")) {
        return "Yes! Many of our recipes are suitable for meal prep. Check the recipe details for serving sizes.";
    } else if (lowerCaseMessage.includes("roast")) {
        return "A roast typically takes about 20 minutes per pound at 350°F, but be sure to check the internal temperature!";
    } else if (lowerCaseMessage.includes("breakfast")) {
        return "How about a smoothie or a quick omelet? Both are healthy and easy to prepare!";
    } else if (lowerCaseMessage.includes("kitchen substitutes")) {
        return "If you run out of an ingredient, common substitutes include yogurt for sour cream and applesauce for oil in baking!";
    } else if (lowerCaseMessage.includes("gluten-free")) {
        return "You can find gluten-free options in our 'Healthy Recipes' section.";
    } else if (lowerCaseMessage.includes("burned my dish")) {
        return "Don't worry! Sometimes you can salvage a dish by removing the burnt parts or adding broth to loosen it up.";
    } else if (lowerCaseMessage.includes("meal planning")) {
        return "Sure! Try choosing a protein, a vegetable, and a grain, then find recipes that use those ingredients.";
    } else if (lowerCaseMessage.includes("international recipes")) {
        return "Yes! Explore our American, Mexican, and Asian cuisines for some international flavors.";
    } else if (lowerCaseMessage.includes("store leftover food")) {
        return "Store leftovers in airtight containers and refrigerate them to keep them fresh for a few days.";
    } else if (lowerCaseMessage.includes("beginner cooks")) {
        return "Start with simple recipes, read through the entire recipe before you start, and don't hesitate to ask questions!";
    } else if (lowerCaseMessage.includes("spice up my dishes")) {
        return "Experiment with herbs, spices, or sauces! A squeeze of lemon or a dash of hot sauce can make a big difference.";
    } else if (lowerCaseMessage.includes("favorite recipe") || lowerCaseMessage.includes("fav dish")) {
        return "My favorite dish is the classic chicken pot pies! It's simple yet delicious!";
    } else if (lowerCaseMessage.includes("what is your favorite dish") || lowerCaseMessage.includes("fav dish")) {
        return "My favorite dish is the classic chicken pot pies! It's simple yet delicious!";
    } else if (lowerCaseMessage.includes("what is your favorite recipe") || lowerCaseMessage.includes("which recipe is your favorite")) {
        return "One of my favorite recipes is the pot roast! It's so comforting!";
    } else if (lowerCaseMessage.includes("recommend a dish")) {
        return "How about trying broccoli casserole? It's comforting and can be made with various ingredients!";
    } else if (lowerCaseMessage.includes("snack ideas")) {
        return "For a quick snack, try avocado toast or quinoa salad!";
    } else if (lowerCaseMessage.includes("quick snack")) {
        return "For a quick snack, try avocado toast or quinoa salad!";
    } else if (lowerCaseMessage.includes("quick meal")) {
        return "Check out the saved recipes, they are all 5 ingredients and are quick and easy!";
    } else if (lowerCaseMessage.includes("where can I find a") || lowerCaseMessage.includes("where to find a")) {
        const dish = userMessage.split(" ").slice(4).join(" ");
        return `You can find a ${dish} recipe in the 'Recipes' page or check out your 'Saved Recipes'!`;
    } else if (lowerCaseMessage.includes("thanks")) {
        return "Of course!";
    } else {
        return "I'm sorry, I didn't understand that. Can you try rephrasing?";
    }
}
