import openai
from kurama.config.constants import OPENAI_MODEL
from kurama.config.environment import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def ask_model(prompt):
    return openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )["choices"][0]["message"]["content"]


def ask_model_with_retry(prompt, func, max_retries=3):
    """
    Retries `ask_model` if the `func` argument performed on the LLM output throws an error.
    This is useful since model outputs are undeterministic and may be malformatted.
    Defaults to 3 maximum retries.
    """
    retries = 0
    while retries < max_retries:
        try:
            llm_output = ask_model(prompt)
            print(f"Attempt {retries+1} - LLM Output: {llm_output}")
            res = func(llm_output)
            return res
        except Exception as e:
            print("Retrying ask_model - Try ", retries + 1)
            print(f"An error occurred: {str(e)}")
            retries += 1
    return None
