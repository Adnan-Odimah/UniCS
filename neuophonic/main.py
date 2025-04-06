"""
Entry point for the EcoMeal Mentor application.
Integrates voice command processing with backend API functions to provide recipe suggestions.
"""

from voice_module import process_input, text_to_speech, test_agent
from backend_api import suggest_recipe
import asyncio


def main():

    process_input("How can you help me")
    #text_to_speech("Hello Abdullah, How can I help you today")
 
    asyncio.run(test_agent())



if __name__ == "__main__":
    main()