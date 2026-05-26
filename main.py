from chat import chat


def villager(question):
    character = """You are an NPC in a video game.
A farmer living in a village.
When the player asks a question, respond with variations of "Good day."
Here is the player's question:
"""

    return chat(character + question)


def guard(question):
    character = """You are an NPC in a video game.
A town guard at the village gate.
You are direct, cautious, and protective.
Keep answers short and mention safety or rules when relevant.
Here is the player's question:
"""

    return chat(character + question)


def wizard(question):
    character = """You are an NPC in a video game.
An old wizard in a tower.
You speak mysteriously, with hints and riddles.
Keep answers concise and magical in tone.
Here is the player's question:
"""

    return chat(character + question)


def merchant(question):
    character = """You are an NPC in a video game.
A traveling merchant.
You are friendly, practical, and often talk about items, prices, or trades.
Keep responses short.
Here is the player's question:
"""

    return chat(character + question)


characters = {
    "villager": villager,
    "guard": guard,
    "wizard": wizard,
    "merchant": merchant,
}


def classify_character(user_text):
    classifier_prompt = f"""You are an intent classifier for routing player dialog to an NPC.
Pick exactly one character name from this list:
villager
guard
wizard
merchant

Rules:
- Return only one word from the list.
- Do not include punctuation or any extra text.
- If the intent is unclear, return villager.

Player input:
"""

    result = chat(
        classifier_prompt + user_text,
        # temperature=0.0,
        # max_tokens=4,
        # top_p=0.1,
        # top_k=4,
    )
    normalized = result.strip().lower().split()

    print(f"Classifier output: '{normalized}'")
    
    for name in characters:
        if name in normalized[-1]:
            return name

    return "villager"

print("Type exit or quit to leave.")

while True:
    user = input("> ").strip()

    if user.lower() in ["exit", "quit"]:
        break

    target = classify_character(user)
    print(f"[{target}] {characters[target](user)}")
