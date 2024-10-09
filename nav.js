class Button {
    constructor(buttonElement) {
        if (new.target === Button) {
            throw new TypeError("Cannot construct Button instances directly");
        }
        this.button = buttonElement;
    }

    addEffect() {
        throw new Error("addEffect() must be implemented in subclass");
    }
}

class NavButton extends Button {
    constructor(buttonElement) {
        super(buttonElement);
        this.addPopOutEffect();
    }

    addPopOutEffect() {
        this.button.addEventListener('mouseover', () => {
            this.button.style.transform = 'scale(1.2)'; 
            this.button.style.transition = 'transform 0.3s'; 
        });

        this.button.addEventListener('mouseout', () => {
            this.button.style.transform = 'scale(1)';
        });
    }
}

class ButtonFactory {
    createButton(buttonElement) {
        throw new Error("createButton() must be implemented in a subclass");
    }
}

class NavButtonFactory extends ButtonFactory {
    createButton(buttonElement) {
        return new NavButton(buttonElement);
    }
}


class NavMenu {
    constructor(navButtons, buttonFactory) {
        this.navButtons = navButtons;
        this.buttonFactory = buttonFactory; 
        this.initializeButtons();
    }

    initializeButtons() {
        this.navButtons.forEach(buttonElement => {
            this.buttonFactory.createButton(buttonElement); 
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const navButtonElements = document.querySelectorAll('.nav-link');
    const navMenu = new NavMenu(navButtonElements, new NavButtonFactory()); 
});
