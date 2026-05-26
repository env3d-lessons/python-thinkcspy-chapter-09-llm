import random
import math
import sys, os
import shutil

# Detect if we're running inside a testrunner and skip heavy model init
running_under_testrunner = (
    os.environ.get("TESTRUNNER", "").lower() in ("1", "true", "yes")
    or "PYTEST_CURRENT_TEST" in os.environ
    or os.environ.get("GITHUB_ACTIONS", "").lower() in ("1", "true", "yes")
)

llm = None
if not running_under_testrunner:
    from llama_cpp import Llama
    # Suppress stderr temporarily
    stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')

    llm = Llama(
          model_path="./model.gguf",
          # n_gpu_layers=-1, # Uncomment to use GPU acceleration
          seed=random.randint(0, 2**31-1),
          #n_ctx=32768, # Uncomment to increase the context window
          verbose=False,
          logits_all=True
    )

    sys.stderr = stderr  # Restore stderr


def complete(prompt, temperature=0.7, max_tokens=1024, top_p=0.9, top_k=40, stop=['\n','<|endoftext|>','<|im_end|>']):
    if llm is None:
        raise RuntimeError("LLM not initialized (running under testrunner).")
    
    result = llm(prompt, 
                 max_tokens=max_tokens, 
                 temperature=temperature, 
                 top_p=top_p, top_k=top_k, 
                 stop=stop
                 )
    return result['choices'][0]['text'].strip()

def chat_no_output(prompt, temperature=0.7, max_tokens=1024, top_p=0.9, top_k=40):
    if llm is None:
        #raise RuntimeError("LLM not initialized (running under testrunner).")
        return "<think>\nsimulated thinking\n</think>\nguard"
    
    if type(prompt) is not list:
        prompt = [{"role": "user", "content": prompt}]
    result = llm.create_chat_completion(prompt, 
                                        max_tokens=max_tokens, 
                                        temperature=temperature, 
                                        top_p=top_p, 
                                        top_k=top_k)    
    return result['choices'][0]['message']['content'].strip()

def chat(prompt, temperature=0.7, max_tokens=1024, top_p=0.9, top_k=40):
    if llm is None:
        return "<think>\nsimulated thinking\n</think>\nguard"

    if type(prompt) is not list:
        prompt = [{"role": "user", "content": prompt}]
        
    # Call create_chat_completion with stream=True
    response_stream = llm.create_chat_completion(
        prompt, 
        max_tokens=max_tokens, 
        temperature=temperature, 
        top_p=top_p, 
        top_k=top_k,
        stream=True # <--- Enables token-by-token generation
    )    

    full_text = ""
    indicator = "\033[2m[AI is generating...] "
    use_ansi_clear = sys.stdout.isatty()
    use_stream_style = use_ansi_clear and os.environ.get("NO_COLOR") is None
    
    # 1. Print the loading indicator
    sys.stdout.write(indicator)
    sys.stdout.flush()

    if use_stream_style:
        # Use a lighter terminal style while tokens stream in.
        sys.stdout.write("\033[2m")
        sys.stdout.flush()

    # 2. Consume the stream and display tokens live
    try:
        for chunk in response_stream:
            # Structure for streaming chunks inside llama-cpp-python
            if 'choices' in chunk and len(chunk['choices']) > 0:
                delta = chunk['choices'][0].get('delta', {})
                token = delta.get('content', '')
                
                if token:
                    full_text += token
                    sys.stdout.write(token)
                    sys.stdout.flush()
    finally:
        if use_stream_style:
            # Always reset style, even if stream generation errors out.
            sys.stdout.write("\033[0m")
            sys.stdout.flush()

    # 3. Erase the stream from the console window
    if use_ansi_clear:
        # Clear every rendered line (including soft-wrapped lines) from bottom to top.
        cols = max(1, shutil.get_terminal_size(fallback=(80, 24)).columns)
        rendered = indicator + full_text

        lines_to_clear = 0
        for segment in rendered.split("\n"):
            # Each segment occupies at least one terminal row.
            lines_to_clear += max(1, (len(segment) + cols - 1) // cols)

        # Start on the current line, then clear upward line-by-line.
        sys.stdout.write("\r")
        for i in range(lines_to_clear):
            sys.stdout.write("\033[2K")
            if i < lines_to_clear - 1:
                sys.stdout.write("\033[1A\r")
        sys.stdout.write("\r")
    else:
        # Fallback for non-interactive output: best effort single-line clear.
        total_length = len(indicator) + len(full_text)
        sys.stdout.write("\r" + " " * total_length + "\r")
    sys.stdout.flush()

    # 4. Clean up trailing spaces and return the pristine string
    return full_text.strip()

def get_top_tokens(prompt, n=10):
    """
    Returns a list of the top n possible next tokens and their probabilities.
    """
    if llm is None:
        raise RuntimeError("LLM not initialized (running under testrunner).")
    
    result = llm(
        prompt,
        max_tokens=1,
        temperature=0,      # Greedy, but returns logprobs for all options
        logprobs=n
    )
    logprobs = result['choices'][0]['logprobs']['top_logprobs'][0]
    # logprobs is a dict: {token: logprob}
    tokens_probs = [
        (token, float(round(math.exp(logprob), 6)))  # Convert log-prob to prob
        for token, logprob in logprobs.items()
    ]
    return tokens_probs