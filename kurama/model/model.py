import openai
from kurama.config.constants import OPENAI_MODEL, DEFAULT_TEMPERATURE
from kurama.config.environment import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def ask_model(prompt):
    return openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=DEFAULT_TEMPERATURE,
    )["choices"][0]["message"]["content"]


def ask_model_with_retry(prompt, func=lambda x: x, max_retries=3):
    """
    Retries `ask_model` if the `func` argument performed on the LLM output throws an error.
    This is useful since model outputs are undeterministic and may be malformatted.
    Defaults to 3 maximum retries.
    """
    # TODO: Handle OpenAI API failures gracefully
    # TODO: Implement an exponential backoff

    retries = 0
    while retries < max_retries:
        if retries:
            print(f"Retrying ask_model - Attempt {retries}")
        try:
            llm_output = ask_model(prompt)
            print(f"Attempt {retries + 1} - Raw LLM Output: {llm_output}")
            res = func(llm_output)
            return res
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            retries += 1
    return None
