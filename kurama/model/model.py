import openai
from kurama.config.constants import OPENAI_MODEL, DEFAULT_TEMPERATURE
from kurama.config.environment import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def ask_model(messages):
    return openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=DEFAULT_TEMPERATURE,
    )["choices"][0]["message"]["content"]


def ask_model_with_retry(prompt, system_prompt, func=lambda x: x, max_retries=3, retry_prompt=None):
    """
    Retries `ask_model` if the `func` argument performed on the LLM output throws an error.
    This is useful since model outputs are undeterministic and may be malformatted.
    Defaults to 3 maximum retries.
    """
    # TODO: Handle OpenAI API failures gracefully
    # TODO: Implement an exponential backoff

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
    retries = 0
    error = None
    while retries < max_retries:
        if retries:
            # TODO: Allow multiple formats for retry_prompt
            prompt = retry_prompt.format(error=error) if retry_prompt else prompt
            messages.append({"role": "user", "content": prompt})
            print(f"Retrying ask_model - Attempt {retries}")
        try:
            llm_output = ask_model(messages=messages)
            print(f"Attempt {retries + 1} - Raw LLM Output: {llm_output}")

            # Validate output
            res = llm_output
            for f in [func] if callable(func) else func:
                res = f(res)

            # Save the assistant response
            messages.append({"role": "assistant", "content": res})
            return res
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            error = str(e)
            retries += 1
    return None
