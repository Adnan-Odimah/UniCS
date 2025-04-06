"""
Simulated backend API for the EcoMeal Mentor.
This module provides functions to fetch smart kitchen inventory data,
energy efficiency metrics, and to generate recipe suggestions.
"""

import random

def get_kitchen_inventory():
    """
    Simulate fetching comprehensive kitchen inventory data.
    
    Returns:
        dict: A dictionary representing available ingredients.
    """
    inventory = {
        "vegetables": [
            "tomato", "spinach", "bell pepper", "broccoli", "carrot",
            "zucchini", "cauliflower", "asparagus", "green beans", "kale"
        ],
        "fruits": [
            "apple", "banana", "orange", "strawberry", "blueberry",
            "kiwi", "grapes", "pineapple", "mango", "peach"
        ],
        "proteins": [
            "chicken", "tofu", "beef", "pork", "lamb",
            "turkey", "salmon", "tuna", "beans", "lentils"
        ],
        "grains": [
            "rice", "quinoa", "barley", "oats", "bulgur",
            "couscous", "millet", "farro", "cornmeal", "spelt"
        ],
        "dairy": [
            "milk", "cheddar cheese", "mozzarella", "yogurt",
            "butter", "cream", "goat cheese", "ricotta", "feta", "sour cream"
        ],
        "bakery": [
            "bread", "bagel", "croissant", "muffin", "pita",
            "tortilla", "brioche", "naan", "sourdough", "biscuit"
        ],
        "spices_and_herbs": [
            "salt", "black pepper", "cumin", "paprika", "turmeric",
            "oregano", "basil", "rosemary", "thyme", "cilantro"
        ],
        "condiments": [
            "ketchup", "mustard", "mayonnaise", "soy sauce", "vinegar",
            "hot sauce", "barbecue sauce", "salsa", "pesto", "honey"
        ],
        "frozen": [
            "frozen peas", "frozen corn", "frozen berries", "ice cream",
            "frozen pizza", "frozen vegetables", "frozen shrimp", "frozen chicken", "frozen waffles", "frozen dinners"
        ],
        "beverages": [
            "water", "orange juice", "apple juice", "soda", "coffee",
            "tea", "sparkling water", "lemonade", "energy drink", "milkshake"
        ],
        "snacks": [
            "chips", "crackers", "nuts", "popcorn", "granola bar",
            "chocolate", "cookies", "pretzels", "dried fruit", "trail mix"
        ],
        "canned_goods": [
            "canned tomatoes", "canned beans", "canned corn", "canned tuna", "canned soup",
            "canned fruit", "canned olives", "canned coconut milk", "canned chili", "canned vegetables"
        ],
        "baking_supplies": [
            "flour", "sugar", "baking powder", "baking soda", "yeast",
            "vanilla extract", "cocoa powder", "chocolate chips", "maple syrup", "molasses"
        ],
        "oil_and_fats": [
            "olive oil", "vegetable oil", "coconut oil", "sesame oil", "avocado oil",
            "butter", "margarine", "ghee", "lard", "shortening"
        ]
    }
    return inventory


def simulate_energy_data():
    """
    Simulate energy data for each appliance by randomly selecting a status.
    
    Returns:
        dict: A dictionary with appliances as keys and randomly chosen energy statuses.
    """
    categories = [
        "efficient",   # The appliance is performing very well with minimal energy consumption.
        "optimal",     # The appliance is operating at a desirable level, balancing performance and energy usage.
        "suboptimal",  # The appliance is not performing as well as it could be.
        "inefficient", # The appliance is consuming more energy than expected.
        "low_usage",   # The appliance is being used sparingly.
        "high_usage",  # The appliance is consuming a lot of energy.
        "unknown"      # Fallback state when data is unavailable.
    ]
    
    appliances = ["oven", "stove", "fridge"]
    
    # Generate a random energy state for each appliance
    energy_data = {appliance: random.choice(categories) for appliance in appliances}
    return energy_data

def get_energy_data():
    """
    Fetch energy usage data from smart kitchen appliances by calling the simulation function.
    
    Returns:
        dict: A dictionary representing the current energy efficiency metrics.
    """
    return simulate_energy_data()

def suggest_recipe(mood, diet, preferences):
    """
    Generate a personalized recipe suggestion based on kitchen inventory, energy usage,
    user mood, dietary restrictions, and personal flavor/ingredient preferences.
    
    Args:
        mood (str): The user's current mood ("happy", "sad", "energetic", "relaxed").
        diet (str): The user's dietary requirement ("vegan", "vegetarian", "gluten-free", "low-carb", etc.).
        preferences (dict): User preferences including 'flavor' (e.g., "spicy", "sweet"),
                            'dislikes' (list of ingredients to avoid), and 'cooking_method' if any.
    
    Returns:
        str: A detailed recipe suggestion with ingredients and step-by-step instructions.
    """
    inventory = get_kitchen_inventory()
    energy_data = get_energy_data()
    
    # Standardize inputs to lower-case for consistency
    mood = mood.lower()
    diet = diet.lower()
    flavor_pref = preferences.get("flavor", "").lower()
    dislikes = [d.lower() for d in preferences.get("dislikes", [])]
    cooking_method_pref = preferences.get("cooking_method", "").lower()
    
    # Define some helper functions
    def ingredient_available(ingredient, category_list):
        return ingredient in inventory.get(category_list, [])
    
    # Initialize recipe variables
    recipe_name = ""
    ingredients = []
    instructions = []
    explanation = []
    
    # Example: Vegan recipe candidate using tofu
    if diet == "vegan" and ingredient_available("tofu", "proteins"):
        recipe_name = "Spicy Tofu Stir-Fry" if flavor_pref == "spicy" else "Tofu Vegetable Stir-Fry"
        ingredients.append("Tofu")
        
        # Check for available vegetables and add them if not in dislikes
        for veg in ["bell pepper", "spinach", "onion"]:
            if veg not in dislikes and ingredient_available(veg, "vegetables"):
                ingredients.append(veg.capitalize())
                
        # Choose a grain if available
        if ingredient_available("rice", "grains"):
            ingredients.append("Rice")
        elif ingredient_available("quinoa", "grains"):
            ingredients.append("Quinoa")
        
        # Add spices if the user likes spicy food
        if flavor_pref == "spicy" and ingredient_available("chili flakes", "spices"):
            ingredients.append("Chili Flakes")
            instructions.append("Add chili flakes to enhance the spiciness.")
        
        instructions.extend([
            f"Press and cube the tofu.",
            "Chop the vegetables.",
            "Heat olive oil in a pan over medium heat.",
            "Stir-fry tofu until lightly golden, then add vegetables.",
            "Mix in soy sauce and any additional spices.",
            f"Serve with {ingredients[-1]}."
        ])
        
        explanation.append("This recipe is vibrant and energizing—perfect for an energetic mood—while meeting vegan dietary requirements.")
    
    # If not vegan, consider a vegetarian or other diet-friendly option
    elif diet in ["vegetarian", "gluten-free", "low-carb"]:
        recipe_name = "Hearty Vegetable Quinoa Bowl"
        # Add vegetables from inventory, skipping any that are disliked
        for veg in ["tomato", "spinach", "bell pepper"]:
            if veg not in dislikes and ingredient_available(veg, "vegetables"):
                ingredients.append(veg.capitalize())
        
        # Add a grain substitute based on dietary need
        if diet == "low-carb" and ingredient_available("quinoa", "grains"):
            ingredients.append("Quinoa (in moderation)")
        elif ingredient_available("rice", "grains"):
            ingredients.append("Rice")
        elif ingredient_available("quinoa", "grains"):
            ingredients.append("Quinoa")
        
        instructions.extend([
            "Cook the chosen grain as per package instructions.",
            "Chop and lightly sauté the vegetables with olive oil.",
            "Mix the cooked grain with vegetables and season with herbs and lemon juice.",
            "Serve warm or chilled depending on your mood."
        ])
        
        explanation.append("This bowl is balanced and comforting—ideal for a relaxed or reflective mood—while aligning with vegetarian or other dietary restrictions.")
    
    # Fallback simple recipe: If tofu is missing and diet is flexible
    else:
        recipe_name = "Simple Vegetable Quinoa Salad"
        for veg in ["tomato", "spinach", "bell pepper"]:
            if veg not in dislikes and ingredient_available(veg, "vegetables"):
                ingredients.append(veg.capitalize())
        if ingredient_available("quinoa", "grains"):
            ingredients.append("Quinoa")
        instructions.extend([
            "Cook quinoa and let it cool.",
            "Chop all available vegetables.",
            "Mix the vegetables with quinoa and drizzle olive oil and lemon juice.",
            "Season with salt and pepper and serve chilled."
        ])
        explanation.append("This refreshing salad works well for any mood and uses ingredients that are likely available in your kitchen.")
    
    # Energy usage considerations: Adjust cooking method if an appliance shows high energy usage.
    # For example, if the stove is in high_usage or inefficient state, suggest no-cook or minimal-cook recipes.
    stove_status = energy_data.get("stove", "unknown")
    if stove_status in ["high_usage", "inefficient"]:
        instructions = ["Due to current energy efficiency concerns with your stove, prepare a no-cook version:"] + instructions
        explanation.append("The recipe was modified to minimize stove use since the energy consumption is high.")
    
    # Combine the final recipe suggestion
    final_recipe = f"{recipe_name}:\n"
    final_recipe += "Ingredients: " + ", ".join(ingredients) + ".\n"
    final_recipe += "Instructions: " + " ".join(instructions) + "\n"
    final_recipe += "Note: " + " ".join(explanation)
    
    return final_recipe

def suggest_energy_usage():
    """
    Generate an energy suggestion based on simulated energy data.
    
    Returns:
        str: A detailed message with energy-saving suggestions.
    """
    # Fetch current energy data from smart kitchen appliances
    energy_data = get_energy_data()
    
    # Initialize a list to hold individual recommendations
    suggestions = []
    
    # Analyze the oven's energy efficiency
    oven_state = energy_data.get("oven", "unknown")
    if oven_state == "efficient":
        suggestions.append(
            "Oven: Your oven is running efficiently. Consider using energy-saving cooking methods such as baking with convection or using lower temperatures for longer durations to capitalize on its efficiency."
        )
    elif oven_state == "suboptimal":
        suggestions.append(
            "Oven: Your oven appears to be underperforming. Check for issues like poor insulation or malfunctioning heating elements, and consider scheduling maintenance."
        )
    else:
        suggestions.append(
            f"Oven: Current state is '{oven_state}'. Monitor its performance and consult a technician if energy usage unexpectedly increases."
        )
    
    # Analyze the stove's energy usage
    stove_state = energy_data.get("stove", "unknown")
    if stove_state == "optimal":
        suggestions.append(
            "Stove: Your stove is operating at an optimal level. Keep using lids on pots and pans to retain heat, and remember to turn off burners immediately after use to conserve energy."
        )
    elif stove_state == "inefficient":
        suggestions.append(
            "Stove: The stove's performance suggests inefficiency. Consider using pressure cookers or induction alternatives if available, and check that burners are properly aligned."
        )
    else:
        suggestions.append(
            f"Stove: Current state is '{stove_state}'. Keep an eye on energy consumption and adjust cooking methods as needed."
        )
    
    # Analyze the fridge's energy usage
    fridge_state = energy_data.get("fridge", "unknown")
    if fridge_state == "low_usage":
        suggestions.append(
            "Fridge: Your fridge is in low usage mode, indicating energy conservation. To maintain this, ensure the door seals are intact, avoid frequent door openings, and set the temperature to the recommended level."
        )
    elif fridge_state == "high_usage":
        suggestions.append(
            "Fridge: The fridge appears to be using more energy than expected. Clean the coils and check the seals to improve efficiency."
        )
    else:
        suggestions.append(
            f"Fridge: Current state is '{fridge_state}'. Regular maintenance can help keep energy consumption in check."
        )
    
    # Add general energy-saving tips applicable to all appliances
    suggestions.append(
        "General Tips: Always turn off appliances when not in use, and consider using timers or smart plugs to reduce standby energy consumption. Regular maintenance and cleaning can also help improve efficiency."
    )
    
    # Join all suggestions into a detailed message string
    detailed_suggestions = "\n\n".join(suggestions)
    return detailed_suggestions


