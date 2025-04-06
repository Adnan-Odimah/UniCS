"""
Simulated backend API for the EcoMeal Mentor.
This module provides functions to fetch smart kitchen inventory data,
energy efficiency metrics, and to generate recipe suggestions.
"""

def get_kitchen_inventory():
    """
    Simulate fetching kitchen inventory data.
    
    Returns:
        dict: A dictionary representing available ingredients.
    """
    # Simulated inventory data
    inventory = {
        "vegetables": ["tomato", "spinach", "bell pepper"],
        "proteins": ["chicken", "tofu"],
        "grains": ["rice", "quinoa"],
    }
    return inventory

def get_energy_data():
    """
    Simulate fetching energy usage data from smart kitchen appliances.
    
    Returns:
        dict: A dictionary representing energy efficiency metrics.
    """
    # Simulated energy data, e.g., current energy consumption metrics
    energy_data = {
        "oven": "efficient",
        "stove": "optimal",
        "fridge": "low_usage",
    }
    return energy_data

def suggest_recipe():
    """
    Generate a recipe suggestion based on simulated kitchen inventory and energy data.
    
    Returns:
        str: A string with a suggested recipe.
    """
    # Get simulated data
    inventory = get_kitchen_inventory()
    energy_data = get_energy_data()
    
    # For the prototype, we use a simple logic: if tofu is available and energy is optimal, suggest a tofu stir-fry.
    if "tofu" in inventory.get("proteins", []):
        recipe = (
            "Tofu Stir-Fry:\n"
            "Ingredients: Tofu, bell pepper, spinach, rice.\n"
            "Instructions: Stir-fry tofu with vegetables in a lightly oiled pan. Serve over rice. "
            "Optimal for energy efficiency as it requires minimal cooking time."
        )
    else:
        recipe = (
            "Vegetable Quinoa Salad:\n"
            "Ingredients: Tomato, spinach, quinoa, bell pepper.\n"
            "Instructions: Mix fresh vegetables with cooked quinoa. Serve chilled for a refreshing meal."
        )
    return recipe