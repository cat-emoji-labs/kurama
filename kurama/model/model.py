import openai
from kurama.config.constants import OPENAI_MODEL


def ask_model(prompt):
    return openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )["choices"][0]["message"]["content"]
