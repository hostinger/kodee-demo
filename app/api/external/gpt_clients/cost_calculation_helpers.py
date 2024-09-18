def calculate_openai_cost(model, prompt_tokens, completion_tokens) -> float | str:
    if model in openai_pricing_per_1k_tokens:
        pricing = openai_pricing_per_1k_tokens[model]
        total_cost = (prompt_tokens * pricing["prompt"] / 1000) + (completion_tokens * pricing["completion"] / 1000)
        return total_cost
    else:
        return "Model not found"


openai_pricing_per_1k_tokens = {
    "gpt-4-turbo": {
        "prompt": 0.01,
        "completion": 0.03,
    },
    "gpt-4o": {
        "prompt": 0.005,
        "completion": 0.015,
    },
    "gpt-4o-2024-05-13": {
        "prompt": 0.005,
        "completion": 0.015,
    },
    "gpt-4o-2024-08-06": {
        "prompt": 0.0025,
        "completion": 0.010,
    },
}
