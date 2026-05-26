import os
import sys
import pytest
from unittest.mock import patch

# Set the environment variable to prevent chat.py from initializing the heavy LLM model
os.environ["TESTRUNNER"] = "true"

import main  # Import the student's module


# ==============================================================================
# TASK 1: FIXING THE BUG (The Router & NoneType Error)
# ==============================================================================
def test_task1_routing_logic():
    """
    Tests if classify_character accurately returns 'guard' or 'villager'
    and ensures it handles unpredicted AI formatting by defaulting to 'villager'
    instead of returning None (which causes the upper() crash in main).
    """
    # Test case A: Chat returns explicit guard (with or without think tags parsed)
    # If they use string slicing/splitting correctly, 'guard' should be isolated.
    with patch("main.chat") as mock_chat:
        mock_chat.return_value = "<think>this is a guard request</think>\nguard"
        assert main.classify_character("Help, a monster!") == "guard"

    # Test case B: Chat returns explicit villager
    with patch("main.chat") as mock_chat:
        mock_chat.return_value = "<think>standard greeting</think>\nvillager"
        assert main.classify_character("Hello there!") == "villager"

    # Test case C: The Catch-All Fallback (Fixes the None/Crash Bug)
    # If the LLM returns random gibberish, the function must return 'villager'
    with patch("main.chat") as mock_chat:
        mock_chat.return_value = "<think>unclear</think>\nsome random response"
        result = main.classify_character("xyz123")
        
        assert result != None, "Bug Found: classify_character returned None, which will crash main()!"
        assert result == "villager", "When intent is unclear, the router should default to 'villager'."


# ==============================================================================
# TASK 2: REMOVING ALL THE "THINKING"
# ==============================================================================
def test_task2_thinking_tags_removed():
    """
    Tests if the NPC functions successfully strip out the <think>...</think> tags.
    The final string returned by the character functions must NOT contain the tags 
    or the internal reasoning content.
    """
    sample_raw_llm_output = (
        "<think>\nI am an old wizard, I must speak in a riddle.\n</think>\nThe blue moon shines at midnight."
    )

    # We mock chat() to return the dirty raw output from Qwen
    with patch("main.chat") as mock_chat:
        mock_chat.return_value = sample_raw_llm_output
        
        # Test the wizard function (or guard/villager, depending on which ones they updated)
        # We check talk_to_guard as it is guaranteed to be in the starter code
        clean_response = main.talk_to_guard("Where is the tower?")

        # Assertions to ensure string parsing successfully isolated the actual answer
        assert "<think>" not in clean_response, "The '<think>' tag is still present in the output!"
        assert "</think>" not in clean_response, "The '</think>' tag is still present in the output!"
        assert "internal" not in clean_response.lower(), "The hidden thinking text was leaked into the final output!"
        assert clean_response.strip() == "The blue moon shines at midnight.", "The clean output didn't extract the correct final response."


# ==============================================================================
# TASK 3: MORE CHARACTERS (Wizard & Merchant)
# ==============================================================================
def test_task3_extended_characters_implemented():
    """
    Tests if the student successfully extended the engine to include 
    the 'wizard' and the 'merchant' functions and classifier options.
    """
    # 1. Verify functions exist in main.py
    assert hasattr(main, "talk_to_wizard"), "Missing function: talk_to_wizard() has not been created."
    assert hasattr(main, "talk_to_merchant"), "Missing function: talk_to_merchant() has not been created."

    # 2. Verify classify_character handles the 'wizard' classification
    with patch("main.chat") as mock_chat:
        mock_chat.return_value = "<think>routing to magic npc</think>\nwizard"
        assert main.classify_character("Tell me a spell") == "wizard"

    # 3. Verify classify_character handles the 'merchant' classification
    with patch("main.chat") as mock_chat:
        mock_chat.return_value = "<think>routing to shop npc</think>\nmerchant"
        assert main.classify_character("How much for the sword?") == "merchant"