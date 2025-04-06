"""
Flask application for the EcoMeal Mentor frontend.
Provides a web interface to display the recipe suggestion.
"""

from flask import Flask, render_template
from backend_api import suggest_recipe

app = Flask(__name__)

@app.route("/")
def index():
    """
    Home route that fetches a recipe suggestion and renders it in the UI.
    
    Returns:
        HTML: Rendered template with the recipe suggestion.
    """

    user_preferences = {
    "flavor": "spicy",
    "dislikes": ["onion"],
    "cooking_method": "stir-fry"
    }  

    recipe = suggest_recipe("energetic", "vegan", user_preferences) 
    return render_template("index.html", recipe=recipe)

if __name__ == "__main__":
    app.run(debug=True)