"""
Entry point for the EcoMeal Mentor application.
Integrates voice command processing with backend API functions to provide recipe suggestions.
"""

from voice_module import process_voice_command
from backend_api import suggest_recipe

def main():
    # Simulate capturing a voice command from the user
    print("Listening for your command...")
    command = process_voice_command()  # Simulated voice input
    print(f"Received command: {command}")

    # Process the command: if it includes a recipe request, fetch a recipe suggestion
    if "recipe" in command.lower():
        recipe = suggest_recipe()
        print("Recipe Suggestion:")
        print(recipe)
    else:
        print("Command not recognized. Please try saying 'Give me a recipe suggestion.'")

if __name__ == "__main__":
    main()