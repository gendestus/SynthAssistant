import openai
import os

class LargeLanguageModel:

    def __init__(self) -> None:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4"

    def interact(self, system_prompt, prompt):
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        response = openai.ChatCompletion.create(model=self.model, messages=messages)
        return response.choices[0].message.content
    def judge_importance(self, memory):
        system_prompt = "On the scale of 1 to 10, where 1 is purely mundane (e.g., brushing teeth, making bed) and 10 is extremely poignant (e.g., a break up, college acceptance), rate the likely poignancy of the following piece of memory. Do not respond with anything besides a number"
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": memory.value
            }
        ]
        response = openai.ChatCompletion.create(model=self.model, messages=messages)
        return float(response.choices[0].message.content)