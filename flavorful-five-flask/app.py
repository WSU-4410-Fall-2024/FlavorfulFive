from flask import Flask, render_template, url_for, redirect, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
import pyotp
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os


app = Flask(__name__)

#loads env variables
load_dotenv()
#set up app and email sending parameters
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  
mail = Mail(app)
key = os.getenv('key') #key for otp

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-default-secret-key')


#FOR RUNNING LOCALLY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#FOR USE WHEN HOSTING
# app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database.db')}"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    '''
    used to return user, based on the userID
    '''
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    '''
    structure of user in database for sql-lite
    id (int): Primary key for the user.
        username (str): The username of the user.
        password (str): The hashed password of the user.
        email (str): The email address of the user. (added using migration)
    '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)  


class RegisterForm(FlaskForm):
    '''
    utilize flasks built in forms for authentication
     username (StringField): Field for the username.
    password (PasswordField): Field for the password.
    email (EmailField): Field for the email address.
    submit (SubmitField): Submit button for the form.
    '''
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    
    email = EmailField(validators=[
        InputRequired(), Length(min=6, max=120)], render_kw={"placeholder": "Email"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        '''
        verifies username is unique, or else sends a message
        '''
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')
        
    def validate_email(self, email):
        '''
        verifies email is unique, or else sends a message
        '''
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError(
                'That email already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    '''
    A login form for existing users.

        username (StringField): Field for the username.
        password (PasswordField): Field for the password.
        submit (SubmitField): Submit button for the form.
    '''
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


@app.route('/')
def home():
    '''
    syntax for defining a route, in this case home
    '''
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    route for login, compares hashed password to database
    '''
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                # return redirect(url_for('home'))
                return redirect(url_for('send_2fa_code'))  # Redirect to send the 2FA code
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    '''
    logout route clears logged in and 2fa status
    '''
    session.pop('2fa_verified', None)
    logout_user()
    return redirect(url_for('home'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    route to create new user and add to db
    '''
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password, email=form.email.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

all_recipes = [
    {
        "name": "Microwave Baked Potato",
        "image": "images2/1.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "1 large russet potato",
            "Salt and ground black pepper",
            "1 tablespoon butter",
            "2 tablespoons shredded Cheddar cheese",
            "1 tablespoon sour cream"
        ],
        "instructions": """Scrub potato and prick with a fork. Place on a microwave-safe plate. Microwave on full power for 5 minutes. Turn potato over, and microwave until soft, about 5 more minutes. Remove potato from the microwave, and cut in half lengthwise. Season with salt and pepper and mash up the inside a little with a fork. Add butter and Cheddar cheese. Microwave until melted, about 1 more minute. Top with sour cream, and serve."""
    },
    {
        "name": "Tater Tot Casserole",
        "image": "images2/2.png",
        "cuisine": "American",
        "rating": 4,
        "ingredients": [
            "1 pound ground beef",
            "1 (10.5 ounce) can condensed cream of mushroom soup",
            "Salt and ground black pepper to taste",
            "1 (16 ounce) package frozen tater tots",
            "2 cups shredded Cheddar cheese"
        ],
        "instructions": """Preheat the oven to 350°F. Heat a skillet over medium-high heat and cook ground beef until browned and crumbly, about 7 to 10 minutes. Stir in the condensed soup and season with salt and pepper. Transfer the beef mixture to a baking dish, layer tater tots evenly on top, and sprinkle with Cheddar cheese. Bake until tater tots are golden brown and hot, about 30 to 45 minutes."""
    },
    {
        "name": "Pesto Salmon",
        "image": "images2/3.png",
        "cuisine": "Italian",
        "rating": 5,
        "ingredients": [
            "24 ounces salmon fillets (4 6-ounce fillets)",
            "6-7 tablespoons pesto",
            "⅓ cup fresh breadcrumbs",
            "½ cup freshly grated parmesan cheese"
        ],
        "instructions": """Preheat the oven to 400°F. Place a piece of tin foil on a rimmed baking sheet and spray with vegetable spray. Lay the salmon fillets on the baking sheet so they don’t touch. Spoon 1½ tablespoons of basil pesto over each fillet and spread it with the back of a spoon or knife so it’s lightly coated with the herb sauce. Combine the breadcrumbs and parmesan cheese in a small bowl. Top the salmon fillets with the breadcrumb mixture. Cook the salmon for 12 minutes for medium and up to 15 minutes to cook through."""
    },
    {
        "name": "Slow Cooker Sausage and Peppers",
        "image": "images2/4.png",
        "cuisine": "American",
        "rating": 4,
        "ingredients": [
            "5 links Italian Sausage",
            "2 tablespoons olive oil",
            "One 24 oz. jar Rao’s Marinara Sauce",
            "2 large red bell peppers",
            "1 large green bell pepper"
        ],
        "instructions": """Heat half the olive oil in a non-stick frying pan over medium-high heat, add sausages, and cook until they're nicely browned on both sides. Remove sausage to cutting board and cut each sausage in half lengthwise. Heat the rest of the olive oil, add sausage, and brown the cut side of the sausage. Put sausage on cutting board and cut into pieces when it’s cool enough to handle. Put sausage pieces in slow cooker and turn to LOW. Add the pasta sauce to the frying pan and simmer about 10 minutes so sauce is slightly reduced. While sauce reduces, cut red and green peppers into pieces a little bigger than one inch across. Add peppers to slow cooker. When sauce has reduced by about 1/4, pour over sausage and peppers in the slow cooker and stir to combine. Put lid on the slow cooker and cook on LOW about 1 1/2 hours for peppers that are still slightly crisp, or a bit longer if you prefer softer peppers."""
    },
    {
        "name": "Air Fryer French Bread Pizza",
        "image": "images2/5.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "2 French rolls",
            "2 tablespoons garlic butter",
            "½ cup pizza sauce",
            "1 cup pizza mozzarella",
            "½ cup pepperoni"
        ],
        "instructions": """Preheat air fryer to 350 degrees. Spread garlic butter on split French bread rolls. Add 2 buttered roll halves to the preheated air fryer tray. Cook for 3 minutes. Next, add the pizza sauce to the toasted buns. Top with cheese followed by pepperoni or any of your favorite toppings. Cook for an additional 5 minutes or until desired crispiness is reached. Cook remaining rolls and enjoy hot!"""
    },
    {
        "name": "Mississippi Pot Roast",
        "image": "images2/6.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "3–4 lb. beef rump roast",
            "1 packet ranch dressing mix",
            "1 packet au jus gravy mix",
            "8–10 pepperoncini peppers",
            "1/4 cup butter"
        ],
        "instructions": """Place the roast in your slow cooker. Sprinkle the ranch dressing mix and au jus mix over the top of the roast. Add pepperoncini peppers on top of and around the roast. Cut the butter into slices and arrange on top of the roast. Add 1/4 cup pickle juice from pepperoncini jar to the bottom of the slow cooker. Cover and cook on low for 6 to 8 hours or until the roast is fork tender."""
    },
        {
        "name": "Mini Chicken Pot Pies",
        "image": "images2/7.png",
        "cuisine": "American",
        "rating": 4,
        "ingredients": [
            "1 cup cooked chicken, diced",
            "1 cup mixed frozen vegetables, thawed",
            "1/2 cup sharp cheddar cheese, shredded",
            "1 (10.5 ounce) can of condensed cream of chicken soup",
            "1 (16.3 ounce) can refrigerated biscuits (8 count)"
        ],
        "instructions": """Preheat oven to 375°F. Coat an 8-muffin pan with cooking spray. In a bowl, mix chicken, vegetables, cheese, and soup. Flatten each biscuit into a circle. Press biscuits into muffin cups. Fill with chicken mixture. Bake for 18–23 minutes until crust is golden brown."""
    },
    {
        "name": "5 Ingredient Crock Pot Beef Stroganoff",
        "image": "images2/8.png",
        "cuisine": "Italian",
        "rating": 5,
        "ingredients": [
            "1.5 lb sirloin steak, diced",
            "2 cans cream soup (1 mushroom, 1 onion)",
            "16 oz mushrooms, sliced",
            "16 oz egg noodles",
            "1/2 cup sour cream"
        ],
        "instructions": """Brown steak in a skillet. Add steak, soups, and mushrooms to crockpot. Cook on low for 6 hours. Cook egg noodles. Stir in sour cream before serving. Serve over noodles."""
    },
    {
        "name": "Copycat KFC Famous Bowl Recipe",
        "image": "images2/9.png",
        "cuisine": "American",
        "rating": 4,
        "ingredients": [
            "20 chicken nuggets or tenders",
            "12 oz frozen corn",
            "8 oz bag Idahoan Buttery Homestyle Mashed Potatoes",
            "18 oz jar Heinz chicken gravy",
            "2 cups shredded cheddar cheese"
        ],
        "instructions": """Prepare chicken, mashed potatoes, and gravy as directed. Layer mashed potatoes, corn, chicken, gravy, and cheese in a bowl. Serve warm."""
    },
    {
        "name": "5-Ingredient Mac and Cheese",
        "image": "images2/10.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "4 cups water",
            "1/2 lb elbow macaroni",
            "2 jars Olde English Cheese Spread or 8-10 oz cheddar cheese spread like you would put on crackers",
            "8 oz Velveeta (sliced)",
            "4 tbsp butter (sliced)"
        ],
        "instructions": """Bring water to boil in large pot with the lid on When water is boiling, add macaroni and cook pasta until half done – about 4-5 minutes – DO NOT DRAIN. Lower to medium heat, stir in Velveeta and Old English cheeses.When cheese is almost melted, add butter and stir.Add a pinch of salt & pepper to taste.Turn off heat and let rest. Sauce will thicken up after it stands for 15 minutes – or is even better the next day!"""
    },
    {
        "name": "Easy Cheesy Tortellini Bake",
        "image": "images2/11.png",
        "cuisine": "Italian",
        "rating": 5,
        "ingredients": [
            "1 lb cheese tortellini",
            "24 oz jar marinara sauce",
            "4 oz mozzarella cheese, shredded",
            "1/4 cup parsley, chopped",
            "4 oz fresh mozzarella, sliced"
        ],
        "instructions": """Preheat oven to 350°F. Cook tortellini for 3 minutes. Mix cooked tortellini, marinara, shredded mozzarella, and parsley. Pour into baking dish. Top with sliced mozzarella. Bake for 30 minutes."""
    },
    {
        "name": "5-Ingredient Pesto Chicken Stuffed Peppers",
        "image": "images2/12.png",
        "cuisine": "Italian",
        "rating": 5,
        "ingredients": [
            "6 bell peppers",
            "2 chicken breasts, shredded",
            "1 1/2 cups shredded mozzarella cheese",
            "1 cup cooked quinoa",
            "1 (6.25 oz) jar of pesto"
        ],
        "instructions": """Preheat oven to 350°F. Broil peppers until blistered. Mix chicken, cheese, quinoa, and pesto. Stuff peppers with mixture. Bake for 10 minutes."""
    },
    {
        "name": "Quick N' Easy Meatballs N' Gravy",
        "image": "images2/13.png",
        "cuisine": "American",
        "rating": 4,
        "ingredients": [
            "1 lb ground beef, seasoned",
            "1 envelope dry onion soup mix",
            "1 can cream of mushroom soup",
            "1 ¾ cups water"
        ],
        "instructions": """Form ground beef into meatballs and brown in a pan. Remove excess fat. Add onion soup mix, mushroom soup, and water. Simmer until gravy thickens. Serve over rice or noodles."""
    },
    {
        "name": "Penne with Chicken & Broccoli Casserole",
        "image": "images2/14.png",
        "cuisine": "Italian",
        "rating": 5,
        "ingredients": [
            "16 oz penne pasta, cooked",
            "16 oz jar alfredo sauce",
            "4 cups shredded cheese",
            "1 bunch broccoli, cooked",
            "3-4 chicken breasts, cooked and diced"
        ],
        "instructions": """Preheat oven to 350°F. Mix pasta, chicken, broccoli, Alfredo sauce, and half the cheese. Pour into a greased dish. Top with remaining cheese. Bake for 10 minutes or until melted."""
    },
    {
        "name": "Emergency Meatball Sub Dinner",
        "image": "images2/15.png",
        "cuisine": "American",
        "rating": 4,
        "ingredients": [
            "6 frozen meatballs",
            "1/2 cup pasta sauce",
            "2 tablespoons shredded cheese",
            "4 submarine rolls"
        ],
        "instructions": """Heat meatballs in the microwave. Warm pasta sauce in a pan. Add meatballs to rolls, top with sauce and cheese. Microwave until cheese melts."""
    },
    {
        "name": "Quick Swedish Meatballs",
        "image": "images2/16.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "24 meatballs",
            "1 (10 oz) can cream of chicken soup",
            "1/3 cup milk",
            "1/8 tsp nutmeg",
            "1/2 cup sour cream"
        ],
        "instructions": """Combine meatballs, soup, milk, and nutmeg in a skillet. Simmer for 15 minutes. Add sour cream and heat for 3 more minutes. Serve warm."""
    },
    {
        "name": "Five Ingredient Caprese Chicken",
        "image": "images2/17.png",
        "cuisine": "Italian",
        "rating": 5,
        "ingredients": [
            "3 chicken breasts",
            "2 roma tomatoes",
            "1 cup shredded mozzarella",
            "1/3 cup balsamic syrup",
            "1/2 cup basil, shredded"
        ],
        "instructions": """Season chicken and cook in a skillet until browned. Drizzle with balsamic syrup, top with mozzarella and tomato slices. Cover and cook until cheese melts. Garnish with basil."""
    },
    {
        "name": "Crock-Pot Chicken with Black Beans & Cream Cheese",
        "image": "images2/18.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "4-5 chicken breasts",
            "1 (15 oz) can black beans",
            "1 (15 oz) can corn",
            "1 (16 oz) jar salsa",
            "8 oz cream cheese"
        ],
        "instructions": """Place chicken in slow cooker. Add black beans, corn, and salsa. Top with cream cheese. Cook on low for 4 hours. Shred chicken before serving."""
    },
    {
        "name": "Bacon-Wrapped Jalapeno Poppers",
        "image": "images2/19.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
           "25 fresh jalapeño peppers",
           "14-16 ounces cream cheese",
           "2 cups shredded cheddar cheese",
           "2 (16 ounce) packages bacon"
        ],
        "instructions": """Cut stems off of peppers and cut them all in half lengthwise.
Remove seeds from peppers.
Fill each pepper with cream cheese and sprinkle cheddar cheese on top.
Wrap 1/2 slice of bacon around each pepper half.
Place on baking sheets and place in a 450-degree oven for 10 to 15 minutes or until bacon is fully cooked.
Remove and serve when cooled.
Enjoy!
"""
    },
    {
        "name": "Baked Pesto Chicken",
        "image": "images2/20.png",
        "cuisine": "Italian",
        "rating": 5,
        "ingredients": [
            "4 boneless skinless chicken breast halves",
            "1/2 cup refrigerated basil pesto",
            "2-3 plum tomatoes (sliced, optional)"
            "1/2 cup mozzarella cheese (shredded)"

        ],
        "instructions": """Preheat oven to 400 degrees F.
Line baking sheet with heavy-duty foil.
Place chicken and pesto in medium bowl; toss to coat.
Place chicken on prepared baking sheet.
Bake for 20-25 minutes or until chicken is no longer pink in the center.
Remove from oven; top with tomatoes and cheese.
Bake for an additional 3-5 minutes or until cheese is melted.
"""
    },
    {
        "name": "Bang Bang Shrimp",
        "image": "images2/21.png",
        "cuisine": "Asian",
        "rating": 5,
        "ingredients": [
            "1 lb shrimp, shelled and deveined",
            "1/2 cup mayonnaise",
            "1/4 cup Thai sweet chili sauce",
            "3–5 drops hot chili sauce",
            "1/2–3/4 cup cornstarch"
        ],
        "instructions": """Mix mayonnaise, chili sauce, and hot chili sauce. Coat shrimp with cornstarch and deep fry until golden brown. Toss shrimp in sauce and serve."""
    },
    {
        "name": "Crockpot Salsa Chicken",
        "image": "images2/22.png",
        "cuisine": "Mexican",
        "rating": 4,
        "ingredients": [
            "4 boneless, skinless chicken breasts",
            "2 tsp taco seasoning mix",
            "2 cups chunky red salsa",
            "Lime wedges (for serving)"
        ],
        "instructions": """Place chicken in slow cooker. Sprinkle with taco seasoning and pour salsa over the chicken. Cook on high for 3 hours or low for 6 hours. Shred chicken and mix with additional salsa. Serve with lime wedges."""
    },
    {
        "name": "Black Bean Tacos",
        "image": "images2/23.png",
        "cuisine": "Mexican",
        "rating": 4,
        "ingredients": [
            "2 (15 oz) cans black beans, rinsed",
            "1 tsp ground cumin",
            "1/2 tsp garlic powder",
            "8 hard taco shells",
            "3/4 cup shredded Mexican cheese blend"
        ],
        "instructions": """Mash half the beans in a bowl. Mix with whole beans, cumin, and garlic powder. Fill taco shells with the bean mixture and cheese. Bake at 325°F for 12–15 minutes until cheese melts."""
    },
    {
        "name": "Lazy Lasagna",
        "image": "images2/24.png",
        "cuisine": "Italian",
        "rating": 5,
        "ingredients": [
            "1 lb store-bought ravioli (spinach and ricotta recommended)",
            "750 mL jarred marinara sauce",
            "3 cups grated mozzarella cheese"
        ],
        "instructions": """Preheat oven to 450°F. Layer marinara, ravioli, and cheese in a baking dish. Repeat layers and finish with cheese. Cover with foil and bake for 30 minutes. Uncover and bake until cheese is bubbly and golden."""
    },
    {
        "name": "Sloppy Joes",
        "image": "images2/25.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
          "1 pound ground beef",
          "1 cup ketchup",
          "¼ cup yellow mustard",
          "½ cup water optional - for a saucier sloppy joe",
          "salt & pepper optional - to taste"
        ],
        "instructions": """In a medium pot, add the ground beef & cover with 1-2 inches of water. Use a wooden spoon or spatula to break the meat apart.
Turn the stove to medium-high heat to bring the meat and water to a boil.
Once it is boiling, turn it down to low so it will simmer. Let the meat cook until all the pieces are brown, about 3 minutes.
Drain the meat in a colander with fine openings. Return the meat to the pot.
Add in 1 cup of ketchup and ¼ a cup of yellow mustard. Keep the heat on low and let it heat through for 5 minutes. Stir occasionally.
Taste test the meat. Add optional salt & pepper to taste. I find the ketchup and mustard add enough salt and flavor that it is not needed.
Spoon over toasted hamburger buns or rolls to serve. Top with any of the suggested ideas shared above. Enjoy.
"""
    },
    {
        "name": "Lazy Enchiladas",
        "image": "images2/26.png",
        "cuisine": "Mexican, American",
        "rating": 5,
        "ingredients": [
            "22.5 ounces box frozen beef & cheese taquitos",
            "10 ounces can of enchilada sauce",
            "4 ounces can of mild diced green chilis",
            "8 ounces block of Colby jack cheese shredded",
            "1 tablespoon fresh cilantro chopped"
        ],
        "instructions": """Preheat the oven to 425°F. Spray a 9x13 glass baking dish with cooking spray.
Place the frozen beef & cheese taquitos into the baking dish in a single layer.
Pour the enchilada sauce over the entire surface of the taquitos, followed by the diced green chilis.
Top the entire dish of lazy enchiladas with the shredded cheese and bake for 20-25 minutes or until the cheese is melted and bubbly.
Allow the lazy enchiladas to rest for 5 minutes, then garnish with the chopped fresh cilantro before serving.
"""
    },
    {
        "name": "Crunchy Peanut Butter Cookies",
        "image": "images2/27.png",
        "cuisine": "Baked Goods/Desserts",
        "rating": 5,
        "ingredients": [
           "1 cup smooth peanut butter",
           "1 cup sugar",
           "1 teaspoon baking soda",
           "1 extra-large egg (lightly beaten)"
        ],
        "instructions": """reheat the oven to 350° and position 2 racks in the upper and lower thirds. In a medium bowl, mix the peanut butter with the sugar, baking soda and egg. Roll tablespoons of the dough into 24 balls. Set the balls on 2 baking sheets, and using a fork, make a crosshatch pattern on each cookie. Bake for 15 minutes, shifting the baking sheets from front to back and bottom to top, until the cookies are lightly browned and set. Let cool on a wire rack."""
    },
    {
        "name": "Lemon-Ricotta Pasta",
        "image": "images2/28.png",
        "cuisine": "Italian",
        "rating": 5,
        "ingredients": [
            "1 pound cellentani, gemelli, or another short pasta",
            "1 cup (8 ounces) whole-milk ricotta, room temperature",
            "1 cup (2 ounces) freshly grated Parmesan, plus more for serving",
            "Freshly grated zest of 1 lemon, plus 1 tablespoon lemon juice",
            "1/2 teaspoon black pepper"
        ],
        "instructions": """Step 1: Bring a large pot of salted water to a boil over high heat. Add the pasta and cook according to package instructions until al dente. Reserve 1 cup pasta cooking water, then drain the pasta and return it to the pot.
Step 2: Add the ricotta, Parmesan, lemon zest, juice, and black pepper to a blender or food processor. Blend to a smooth paste, scraping down sides of bowl as needed, about 1 minute. With the machine running, slowly add 1/3 cup pasta water. Scrape down the sides of the bowl and check the consistency of the sauce, adding more pasta water to thin it out if you prefer. Pour the sauce over the pasta and stir until the pasta is evenly coated with the sauce. Add more pasta water as needed for a smooth sauce.
Step 3: Divide the pasta among bowls, being sure to top it with any sauce from the bottom of the pot.
"""
    },
    {
        "name": "Bourbon Chicken",
        "image": "images2/29.png",
        "cuisine": "American",
        "rating": 4,
        "ingredients": [
            "1 package McCormick® Bourbon Chicken Skillet Sauce",
            "1 tablespoon vegetable oil",
            "1 1/2 pounds boneless skinless chicken breasts, cut into 1 inch cubes"
        ],
        "instructions": """Heat oil in a large nonstick skillet on medium-high heat. Add chicken; cook and stir for 7 to 8 minutes or until lightly browned.
Stir in Skillet Sauce. Reduce heat to low and simmer for 5 minutes or until chicken is 
cooked through. Serve with cooked rice, if desired."""
    },
    {
        "name": "Herb Roasted Chicken",
        "image": "images2/30.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "1 package McCormick® Herb Roasted Chicken Oven Bake Sauce",
            "1 1/2 pounds boneless chicken breasts", 
            "2 cups potatoes, cut into 1-inch pieces",
            "1 cup carrots, peeled and cut into 1/2 inch pieces"
        ],
        "instructions": """Place chicken and vegetables in a 13x9-inch baking pan.
Pour Sauce evenly over chicken and vegetables.
Bake in preheated 400°F oven 40 minutes or until chicken is cooked through and vegetables are tender. Stir sauce and spoon over chicken and vegetables before serving.
"""
    },
    {
        "name": "Easy Pork Tacos",
        "image": "images2/31.png",
        "cuisine": "Mexican",
        "rating": 5,
        "ingredients": [
            "1 tablespoon oil",
            "1 pound boneless pork chops, cut into 1/2-inch cubes",
            "1 package McCormick® Original Taco Seasoning Mix",
            "1/2 cup water",
            "12 (6-inch) corn tortillas, warmed"
        ],
        "instructions": """Heat oil in large skillet on medium heat. Add pork; cook and stir 3 to 5 minutes or until no longer pink.
Stir in Seasoning Mix and water. Bring to boil. Reduce heat to low; simmer 5 to 7 minutes or until most of liquid is absorbed, stirring occasionally.
Spoon into warm tortillas and serve with desired toppings.
"""
    },
    {
        "name": "White Bean Chicken Chili",
        "image": "images2/32.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "1 tablespoon oil",
            "1 pound boneless skinless chicken breasts, cut into 1/2-inch cubes",
            "1 package McCormick® White Chicken Chili Seasoning Mix",
            "1 cup water",
            "1 can (15 to 16 ounces) white beans, undrained"

        ],
        "instructions": """Heat oil in large skillet on medium-high heat. Add chicken; cook and stir 3 to 5 minutes or until no longer pink.
Stir in Seasoning Mix, water and beans. Bring to boil. Reduce heat to low; cover and simmer 10 minutes or until chicken is cooked through. Serve with desired toppings.
"""
    },
    {
        "name": "Avocado Toast",
        "image": "images2/33.jpg",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "1 avocado",
            "2 slices of bread",
            "Salt",
            "Pepper",
            "Lemon juice"
        ],
        "instructions": """Toast the bread.
Mash avocado with salt, pepper, and lemon juice.
Spread avocado mixture on toast.
"""
    },
     {
        "name": "Banana Pancakes",
        "image": "images2/34.jpg",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "1 banana",
            "2 eggs",
            "1/4 tsp baking powder",
            "A pinch of cinnamon (optional)",
            "Butter or oil (for cooking)"
        ],
        "instructions": """Mash the banana in a bowl.
Whisk in the eggs and baking powder until combined.
Cook in a greased skillet over medium heat until golden on both sides.
"""
    },
    {
        "name": "Egg Fried Rice",
        "image": "images/friedrice.jpg",
        "cuisine": "Asian",
        "rating": 5,
        "ingredients": [
            "2 cups cooked rice",
            "2 eggs",
            "1/2 cup peas or vegetables",
            "Soy sauce",
            "Oil for frying"
        ],
        "instructions": """Scramble eggs in a skillet. Add cooked rice, vegetables, and soy sauce. Stir-fry until heated through. Serve warm."""
    },
    {
        "name": "Guacamole",
        "image": "images2/36.png",
        "cuisine": "Mexican",
        "rating": 5,
        "ingredients": [
            "2 avocados",
            "1 lime (juiced)",
            "1 small onion (chopped)",
            "Salt",
            "Cilantro (optional)"
        ],
        "instructions": """Mash avocados in a bowl. Mix in lime juice, onion, and salt. Add cilantro if desired. Serve immediately."""
    },
    {
        "name": "Tomato Soup",
        "image": "images2/37.png",
        "cuisine": "Soup and Salad",
        "rating": 4,
        "ingredients": [
            "1 can crushed tomatoes",
            "1 onion (chopped)",
            "2 cloves garlic (minced)",
            "2 cups vegetable broth",
            "Salt & pepper"
        ],
        "instructions": """Sauté onion and garlic in olive oil. Add crushed tomatoes and vegetable broth. Simmer for 20 minutes. Blend until smooth and season with salt and pepper."""
    },
    {
        "name": "Greek Salad",
        "image": "images2/38.png",
        "cuisine": "Soup and Salad",
        "rating": 5,
        "ingredients": [
            "1 cucumber (chopped)",
            "2 tomatoes (chopped)",
            "1/4 red onion (sliced)",
            "100g feta cheese (crumbled)",
            "Olive oil"
        ],
        "instructions": """Combine cucumber, tomatoes, and onion in a bowl. Add crumbled feta and drizzle with olive oil. Serve chilled."""
    },
    {
        "name": "Bruschetta",
        "image": "images2/39.png",
        "cuisine": "Italian",
        "rating": 5,
        "ingredients": [
            "1 baguette (sliced)",
            "2 tomatoes (chopped)",
            "1 clove garlic (minced)",
            "Olive oil",
            "Basil (optional)"
        ],
        "instructions": """Toast baguette slices until golden. Top with chopped tomatoes, minced garlic, and a drizzle of olive oil. Garnish with basil if desired."""
    },
    {
        "name": "Lentil Soup",
        "image": "images2/40.png",
        "cuisine": "Soup and Salad",
        "rating": 5,
        "ingredients": [
            "1 cup lentils",
            "1 onion (chopped)",
            "2 carrots (diced)",
            "4 cups vegetable broth",
            "1 tsp cumin"
        ],
        "instructions": """Sauté onion and carrots in a pot. Add lentils, vegetable broth, and cumin. Simmer for 30 minutes until lentils are tender. Blend partially if desired."""
    },
    {
        "name": "Shrimp Scampi",
        "image": "images2/41.png",
        "cuisine": "Italian",
        "rating": 5,
        "ingredients": [
            "1 lb shrimp (peeled, deveined)",
            "4 cloves garlic (minced)",
            "1/4 cup butter",
            "1/4 cup white wine",
            "1 tbsp lemon juice"
        ],
        "instructions": """Sauté garlic in butter. Add shrimp and cook until pink. Add white wine and lemon juice. Cook for another 2 minutes and serve."""
    },
    {
        "name": "Stuffed Bell Peppers",
        "image": "images2/42.png",
        "cuisine": "Mexican",
        "rating": 4,
        "ingredients": [
            "4 bell peppers (halved)",
            "1 cup cooked rice",
            "1 cup ground beef (cooked)",
            "1 cup cheese (shredded)",
            "1/2 cup salsa"
        ],
        "instructions": """Mix rice, ground beef, salsa, and half the cheese. Stuff bell peppers with the mixture and top with remaining cheese. Bake at 375°F for 30 minutes."""
    },
    {
        "name": "Tzatziki",
        "image": "images2/43.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "1 cup Greek yogurt",
            "1 cucumber (grated)",
            "2 cloves garlic (minced)",
            "1 tbsp olive oil",
            "1 tbsp lemon juice"
        ],
        "instructions": """Combine all ingredients in a bowl. Mix well and chill for 1 hour before serving."""
    },
    {
        "name": "Vegetable Stir-Fry",
        "image": "images2/44.png",
        "cuisine": "Asian",
        "rating": 5,
        "ingredients": [
            "2 cups mixed vegetables (broccoli, bell peppers, carrots)",
            "2 tbsp soy sauce",
            "1 tbsp sesame oil",
            "2 cloves garlic (minced)",
            "1 tbsp ginger (grated)"
        ],
        "instructions": """Sauté garlic and ginger in sesame oil. Add vegetables and soy sauce. Stir-fry until tender and serve warm."""
    },
    {
        "name": "Beef Stroganoff",
        "image": "images2/45.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "1 lb beef sirloin (sliced thinly)",
            "1 cup mushrooms (sliced)",
            "1/2 cup sour cream",
            "1 onion (chopped)",
            "2 tbsp butter"
        ],
        "instructions": """Cook onion and mushrooms in butter. Add beef and cook until browned. Stir in sour cream and simmer for 10 minutes."""
    },
    {
        "name": "Shepherd's Pie",
        "image": "images2/46.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "1 lb ground beef or lamb",
            "1 onion (chopped)",
            "2 cups mashed potatoes",
            "1 cup mixed vegetables",
            "1/4 cup beef broth"
        ],
        "instructions": """Cook ground meat with onion. Add mixed vegetables and beef broth. Transfer to a baking dish, top with mashed potatoes, and bake at 375°F for 20 minutes."""
    },
    {
        "name": "Quinoa Salad",
        "image": "images2/47.png",
        "cuisine": "Soup and Salad",
        "rating": 5,
        "ingredients": [
            "1 cup cooked quinoa",
            "1 cucumber (chopped)",
            "1 tomato (chopped)",
            "2 tbsp olive oil",
            "1 tbsp lemon juice"
        ],
        "instructions": """Combine quinoa, cucumber, and tomato in a bowl. Drizzle with olive oil and lemon juice. Mix well and serve chilled."""
    },
    {
        "name": "Greek Chicken Gyros",
        "image": "images2/48.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "2 chicken breasts (sliced)",
            "1/2 cup Greek yogurt",
            "1 cucumber (sliced)",
            "2 pita breads",
            "1 tbsp lemon juice"
        ],
        "instructions": """Cook chicken with lemon juice. Warm pita bread. Spread yogurt on pita, top with chicken and cucumber. Fold and serve."""
    },
    {
        "name": "Sweet Potato Fries",
        "image": "images2/49.png",
        "cuisine": "American",
        "rating": 4,
        "ingredients": [
            "2 large sweet potatoes (sliced into fries)",
            "2 tbsp olive oil",
            "1 tsp paprika",
            "Salt & pepper"
        ],
        "instructions": """Toss sweet potato slices with olive oil, paprika, salt, and pepper. Bake at 400°F for 25 minutes until crispy."""
    },
    {
        "name": "Thai Green Curry",
        "image": "images2/50.png",
        "cuisine": "American",
        "rating": 5,
        "ingredients": [
            "1 lb chicken breast (sliced)",
            "2 tbsp green curry paste",
            "1 can coconut milk",
            "1 cup green beans",
            "1 tbsp fish sauce"
        ],
        "instructions": """Sauté curry paste and chicken until browned. Add coconut milk, green beans, and fish sauce. Simmer for 10 minutes. Serve with rice."""
    }
]

@app.route('/recipes', methods=['GET'])
def recipes():
    query = request.args.get('query', '')
    cuisine = request.args.get('cuisine', '')
    rating = request.args.get('rating', '')
    
    recipes = all_recipes
    
    if query:
        recipes = [r for r in recipes if query.lower() in r['name'].lower()]
    if cuisine:
        recipes = [r for r in recipes if cuisine.lower() in r.get('cuisine', '').lower()]
    if rating:
        recipes = [r for r in recipes if str(r.get('rating', '')) == rating]
    
    return render_template('recipes.html', recipes=recipes, query=query, cuisine=cuisine, rating=rating)

@app.route('/recipe_detail/<recipe_name>', methods=['GET', 'POST'])
def recipe_detail(recipe_name):
    recipe = get_recipe_by_name(recipe_name, all_recipes)
    
    if recipe:
        if request.method == 'POST':
            selected_ingredients = request.form.getlist('ingredients')  # Get the selected ingredients
            return redirect(url_for('generateshoppinglist', ingredients=selected_ingredients))

        return render_template('recipesfolder.html', recipe=recipe)
    
    else:
        flash("Recipe not found.", "danger")
        return redirect(url_for('recipes'))

def get_recipe_by_name(recipe_name, all_recipes):
    for recipe in all_recipes:
        if recipe['name'].lower() == recipe_name.lower():
            return recipe
    return None  

@app.route('/generate_shopping_list', methods=['POST', 'GET'])
def generateshoppinglist():
    if request.method == 'POST':
       
        selected_ingredients = request.form.getlist('ingredients')  
        if 'shopping_list' not in session:
            session['shopping_list'] = []
        
        for ingredient in selected_ingredients:
            if ingredient not in session['shopping_list']:
                session['shopping_list'].append({'name': ingredient})

        session.modified = True
        return render_template('generateshoppinglist.html', ingredients=session['shopping_list'])
    
    return render_template('generateshoppinglist.html', ingredients=session.get('shopping_list', []))


@app.route('/delete_ingredient', methods=['POST'])
def delete_ingredient():
    ingredient_to_delete = request.form['ingredient']
    
    if 'shopping_list' in session:
        session['shopping_list'] = [ingredient for ingredient in session['shopping_list'] if ingredient != ingredient_to_delete]
        session.modified = True
    return redirect(url_for('generateshoppinglist'))

@app.route('/add_custom_ingredient', methods=['POST'])
def add_custom_ingredient():
    ingredient_name = request.form['ingredient_name'].strip()
    quantity = request.form['ingredient_quantity'].strip()
    unit = request.form['ingredient_unit'].strip()
    notes = request.form['ingredient_notes'].strip()

    if not ingredient_name or not quantity:
        flash('Please provide a valid ingredient name and quantity.', 'danger')
        return redirect(url_for('generateshoppinglist'))

    if 'shopping_list' not in session:
        session['shopping_list'] = []

    ingredient = {
        'name': ingredient_name,
        'quantity': quantity,
        'unit': unit if unit else None,  
        'notes': notes if notes else None  
    }

    session['shopping_list'].append(ingredient)
    session.modified = True

    flash('Custom ingredient added!', 'success')
    return redirect(url_for('generateshoppinglist'))

@app.route('/delete_custom_ingredient', methods=['POST'])
def delete_custom_ingredient():
    ingredient_to_delete = request.form['ingredient']
    
    if 'shopping_list' in session:
        session['shopping_list'] = [
            ingredient for ingredient in session['shopping_list']
            if isinstance(ingredient, dict) and ingredient.get('name') != ingredient_to_delete
        ]
        session.modified = True
        
    return redirect(url_for('generateshoppinglist'))

from flask import render_template, request, redirect, url_for, session

@app.route('/edit_ingredient', methods=['POST', 'GET'])
def edit_ingredient():
    if request.method == 'POST':
        ingredient_name = request.form['ingredient_name']
        
        ingredient = find_ingredient_by_name(ingredient_name)
        
        if ingredient:
            ingredient['name'] = request.form['ingredient_name']
            ingredient['quantity'] = request.form['ingredient_quantity']
            ingredient['unit'] = request.form['ingredient_unit']
            ingredient['notes'] = request.form['ingredient_notes']
        
            session.modified = True 
            return redirect(url_for('generateshoppinglist'))  
    
    ingredient_to_edit = request.args.get('ingredient_name')
    if ingredient_to_edit:
        ingredient = find_ingredient_by_name(ingredient_to_edit)
        return render_template('generateshoppinglist.html', ingredient_to_edit=ingredient)
    return redirect(url_for('generateshoppinglist'))  

def find_ingredient_by_name(ingredient_name):
    for ingredient in session.get('shopping_list', []):  
        if ingredient['name'] == ingredient_name:
            return ingredient
    return None



@app.route('/saved')
def saved():
    username = current_user.username if current_user.is_authenticated else "Guest"
    return render_template('saved.html',username=username)  

@app.route('/myrecipes')
def my_recipes():
    username = current_user.username if current_user.is_authenticated else "Guest"
    return render_template('myrecipes.html',username=username)  

@app.route('/contactus')
def contact_us():
    return render_template('contactus.html')   

@app.route('/verify-2fa', methods=['GET', 'POST'])
@login_required
def verify_2fa():
    '''
    check to verify 2fa code
    '''
    if request.method == 'POST':
        entered_code = request.form.get('2fa_code')
        if str(session.get('2fa_code')) == entered_code:
            # 2FA successful
            session.pop('2fa_code', None)  # Clear the code from the session
            session['2fa_verified'] = True #add session for 2FA
            return redirect(url_for('home'))
        else:
            flash('Invalid 2FA code. Please try again.', 'danger')
    
    return render_template('verify_2fa.html')

@app.route('/send-2fa-code', methods=['GET', 'POST'])
@login_required
def send_2fa_code():
    # Generate time-sensitive 2FA code
    totp = pyotp.TOTP(key, interval=90)
    code = totp.now()
    session['2fa_code'] = code

    # Send the 2FA code via email
    msg = Message('Your 2FA Code', sender=app.config['MAIL_USERNAME'], recipients=[current_user.email])
    msg.body = f'Your 2FA code is: {code}'
    msg.html = f"""
    <html>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f9f9f9;">
        <table role="presentation" cellspacing="0" cellpadding="0" style="width: 100%; background-color: #f9f9f9; padding: 20px;">
            <tr>
                <td align="center">
                    <table role="presentation" cellspacing="0" cellpadding="0" style="max-width: 600px; width: 100%; background-color: #f5daf2; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                        <tr>
                            <td style="text-align: center;">
                                <h2 style="color: #333; font-size: 24px; margin: 0;">Your 2FA Code</h2>
                            </td>
                        </tr>
                        <tr>
                            <td style="font-size: 16px; color: #555; line-height: 1.5; margin: 15px 0;">
                                Hi <strong>{current_user.username}<strong>,
                            </td>
                        </tr>
                        <tr>
                            <td style="font-size: 16px; color: #555; line-height: 1.5; margin: 15px 0;">
                                Here is your 2FA code:
                            </td>
                        </tr>
                        <tr>
                            <td style="text-align: center; margin: 20px 0;">
                                <span style="font-size: 24px; color: #333; font-weight: bold; background-color: #f2f2f2; padding: 10px 20px; border-radius: 5px; display: inline-block;">{code}</span>
                            </td>
                        </tr>
                        <tr>
                            <td style="font-size: 16px; color: #555; line-height: 1.5; margin: 15px 0;">
                                This code is valid for <strong>90 seconds</strong>. Please do not share this code with anyone.
                            </td>
                        </tr>
                        <tr>
                            <td style="font-size: 16px; color: #555; line-height: 1.5; margin: 15px 0;">
                                If you did not request this code, please contact our support team immediately.
                            </td>
                        </tr>
                        <tr>
                            <td style="font-size: 14px; color: #aaa; text-align: center; margin-top: 20px;">
                                &copy; 2024 FlavorfulFive. All rights reserved.
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    mail.send(msg)

    flash('A 2FA code has been sent to your email.', 'info')
    return redirect(url_for('verify_2fa'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()


    #FOR RUNNING LOCALLY   
    app.run(debug=True, port=8000)

    #FOR USE WHEN HOSTING
    #app.run()
