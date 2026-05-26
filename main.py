from chat import chat

def talk_to_villager(question):
    prompt = "You are a village farmer. Respond with variations of 'Good day.'\nQuestion: "
    return chat(prompt + question)


def talk_to_guard(question):
    prompt = (
        "You are a cautious town guard. Keep answers short and mention safety.\nQuestion: "
    )
    return chat(prompt + question)


def talk_to_wizard(question):
    prompt = "You are an old wizard in a tower. Speak mysteriously with riddles.\nQuestion: "
    return chat(prompt + question)


def talk_to_merchant(question):
    prompt = "You are a friendly traveling merchant. Talk about items and prices.\nQuestion: "
    return chat(prompt + question)


def classify_character(user_text):
    classifier_prompt = """You are an intent classifier for routing player dialog to an NPC.
Pick exactly one character name from this list: villager, guard, wizard, merchant.
Return ONLY the single word. If unsure, return villager.

Player input: """

    result = chat(classifier_prompt + user_text)

    # Students use string methods to clean up the LLM's raw output
    clean_result = result.strip().lower().split()[-1]  

    # Determine the intent using basic membership (in) or equality
    if "guard" in clean_result:
        return "guard"
    elif "wizard" in clean_result:
        return "wizard"
    elif "merchant" in clean_result:
        return "merchant"
    else:
        return "villager"


print("Welcome to the AI Village! Type 'exit' or 'quit' to leave.")

while True:
    user_input = input("> ").strip()

    # Standard loop breakout
    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    # 1. Get the target character string from the classifier
    target = classify_character(user_input)

    # 2. Routing logic implemented directly in main using if/elif
    if target == "guard":
        response = talk_to_guard(user_input)
    elif target == "wizard":
        response = talk_to_wizard(user_input)
    elif target == "merchant":
        response = talk_to_merchant(user_input)
    else:
        response = talk_to_villager(user_input)

    # 3. Output the result
    print("["+target.upper()+"]: " + response + "\n")