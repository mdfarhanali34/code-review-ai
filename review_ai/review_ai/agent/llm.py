# llm.py
import openai
from dotenv import load_dotenv
import os


def needs_feedback(line: str) -> bool:
    """
    Asks the LLM if a line of code needs feedback.
    
    Args:
    line (str): The line of code to evaluate.
    
    Returns:
    bool: True if the LLM suggests feedback is needed, False otherwise.
    """
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = api_key

        # Construct the prompt for feedback necessity check
        prompt = f"Does this line of code need improvement or feedback? Answer with 'Yes' or 'No': '{line}'"
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a code review assistant. For each line of code, answer only 'Yes' or 'No' to indicate if it needs feedback."
                },
                {
                    "role": "user",
                    "content": line
                }
            ],
            max_tokens=3,
            temperature=0.0
        )

        response = completion.choices[0].message.content.strip().lower()
        return response == "yes"
    except Exception as e:
        # Log or handle the exception as appropriate
        print(f"Error in needs_feedback: {e}")
        return False

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
        prompt = (
            f"Identify any critical error or bug in this line of code: '{line}'. "
            "Only provide feedback for significant issues that could impact functionality or security. "
            "Do not include minor improvements or style suggestions."
        )
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior software engineer providing code review. "
                        "Your feedback should only mention critical issues, errors, or bugs. "
                        "Avoid commenting on minor improvements or style changes."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
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
