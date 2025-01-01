import random

def get_response(user_input: str) -> str:
    """
    Processes user input and generates appropriate responses based on commands.

    Args:
        user_input (str): The input message from the user.

    Returns:
        str: The response generated based on the user's input.
    """
    # Check if input starts with '!'
    if not user_input.startswith('!'):
        return ''  # Return an empty string to avoid any response

    # Remove the '!' and process the input
    lowered = user_input[1:].strip().lower()

    if not lowered:
        return "Well, you're awfully silent..."

    # Handle predefined commands
    if 'hello' in lowered:
        return 'Hello there!'
    elif 'how are you' in lowered:
        return 'Good, thanks!'
    elif 'bye' in lowered:
        return 'See you!'
    elif 'roll dice' in lowered:
        return f'You rolled: {random.randint(1, 6)}'
    elif 'generate a poem' in lowered:
        # Extract the topic of the poem from the user's input
        topic = user_input.lower().replace('!generate a poem about', '').strip()
        if not topic:
            topic = "something random"  # Default topic if no specific topic is given

        # Generate a rule-based poem
        poems = [
            f"Roses are red, violets are blue,\nA lovely poem about {topic}, just for you.",
            f"The {topic} is bright, under the sun,\nA poem to delight, for everyone.",
            f"Through the {topic}'s embrace, a story unfolds,\nA poem of wonder, in words so bold.",
            f"The {topic} whispers secrets of old,\nIn every shadow and story told.",
            f"With {topic} as the muse, we write,\nA song of dreams in the moonlight."
        ]
        return random.choice(poems)

# Example for testing
if __name__ == "__main__":
    print("Type 'exit' to quit the program.")
    while True:
        user_input = input("Enter your command: ")
        if user_input.strip().lower() == 'exit':
            print("Goodbye!")
            break
        response = get_response(user_input)
        if response:
            print(response)
