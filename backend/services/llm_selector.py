"""
Choose between GPT, Claude and LLaMA based on logic.  This file was originally
located at `utils/llm_selector.py`.  In a full implementation, you would
consider factors such as model capability, cost, latency and context length to
decide which model to use for a given task.
"""

def choose_model(task_description: str) -> str:
    """Select an appropriate language model for a given task.

    :param task_description: A brief description of the task to be performed.
    :returns: The name of the selected model (e.g. "gpt-4", "claude-3", "llama-3").
    """
    # TODO: Implement smart model selection logic
    # This placeholder always returns GPT-4.
    return "gpt-4"
