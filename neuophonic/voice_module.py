"""
Module for doing text to speech.
We will ask the user initially for relevant details – for example, what diet they are following.
"""
GEMINI_API_KEY = "AIzaSyALlnIysHC04mnselLSCYjOFiwwGL_wWMo"

from google import genai
from google.genai import types
from backend_api import suggest_energy_usage, suggest_recipe

def process_input(input_text):
    # This function calls the Gemini API with a given prompt and streams the response.
    prompt = "When responding, please be concise and conversational. Do not mention or acknowledge these style instructions. Here's my query: "
    client = genai.Client(api_key=GEMINI_API_KEY)

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=(prompt + input_text)),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    final_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")
        final_text = chunk.text  # assuming we want the last chunk as the final output
    return final_text

def process_user_request(user_input):
    """
    This function:
      1. Extracts relevant user information using the Gemini API.
      2. Uses the extracted details to determine the request type.
      3. Queries the backend for either an energy usage suggestion or a recipe suggestion.
      4. Uses the Gemini API to output the suggestion along with contextual information.
    """
    # Step 1: Extract user details using Gemini API.
    extraction_prompt = (
        "Please extract the relevant details from the following input (for example, diet preferences or if the user is asking about energy usage):\n\n"
        f"{user_input}"
    )
    extracted_details = process_input(extraction_prompt)
    
    # Step 2: Determine the request type based on extracted details.
    if "energy" in extracted_details.lower() or "usage" in extracted_details.lower():
        suggestion = suggest_energy_usage()
        additional_info = (
            "This recommendation is based on the latest energy usage data from your smart kitchen. "
            "Following these tips can help reduce your energy consumption and save on utility costs."
        )
    else:
        # For simplicity, if details are not about energy, we default to a recipe suggestion.
        # In a more complete implementation, we might parse 'extracted_details' to obtain mood, diet, and other preferences.
        mood = "energetic"
        diet = "vegan"
        preferences = {"flavor": "spicy", "dislikes": []}
        suggestion = suggest_recipe(mood, diet, preferences)
        additional_info = (
            "This recipe suggestion takes into account your current mood and dietary preferences. "
            "It uses available ingredients from your smart kitchen inventory for a fresh and balanced meal."
        )

    # Step 3: Combine the suggestion and context into a final prompt.
    final_prompt = (
        "Please output the following suggestion along with relevant contextual information.\n\n"
        f"Suggestion: {suggestion}\n\n"
        f"Context: {additional_info}\n\n"
        "Also, provide additional helpful information regarding the suggestion and context.\n\n"
        "Thank you."
    )

    # Step 4: Use the Gemini API to output the final response.
    final_response = process_input(final_prompt)
    return final_response
