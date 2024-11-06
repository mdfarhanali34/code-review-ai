# llm.py
import openai
from dotenv import load_dotenv
import os

# Assuming you are using OpenAI's GPT model to generate feedback
def generate_feedback(line: str) -> str:
    """
    Generate feedback for the given line using OpenAI's API (or any custom logic).
    This function can be extended to provide more detailed feedback depending on the context.

    Args:
    line (str): The line of code to generate feedback for.

    Returns:
    str: Feedback for the code line.
    """
    # Example API call to OpenAI's GPT model to generate feedback
    try:
        # Setup your OpenAI API key
        load_dotenv()  # Load environment variables from .env file
        api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key  # Set the OpenAI API key directly on the openai module


        # Construct the prompt for code review
        prompt = f"Provide feedback for this line of code: '{line}'. Please include suggestions for improvement if applicable."
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a highly knowledgeable software engineer reviewing pull requests. "
                        "Responses should be concise, accurate, and professional, focusing on key details under 300 tokens."
                    )
                },
                {
                    "role": "user",
                    "content": line 
                }
            ],
            temperature=0.7,
            max_tokens=100,
        )

        # Extract the feedback from the response
        feedback = completion.choices[0].message.content

        return feedback
    except Exception as e:
        # Handle any exceptions that occur while interacting with the API
        return f"Error generating feedback: {e}"
