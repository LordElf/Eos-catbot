import math
import time
from loguru import logger


class Timer:
    def __init__(self, time_limit=600, max_survival_time=1200):
        self.time_limit = time_limit
        self.start_time = math.inf
        self.max_survival_time = max_survival_time

    def reset_time(self):
        self.start_time = time.time()

    def set_time_inf(self):
        self.start_time = math.inf

    def check_time(self):
        time_passed = time.time() - self.start_time
        return time_passed < self.time_limit and time_passed > 0


class ChatHistory:
    def __init__(self, message, limit=40, openai=None, token_limit=1500):
        self.history = [{"role": "system", "content": message}]
        self.limit = limit
        self.total_tokens = 0
        self.openai = openai
        self.token_limit = token_limit

    def set_openai(self, openai):
        self.openai = openai

    def get_summary(self):
        if self.openai is None:
            return "OpenAI not set"

        # Create a copy of history and append the new message
        summary_history = self.history.copy()
        summary_history.append(
            {
                "role": "user",
                "content": "Can you summarize the conversation as short as possible? PLease keep the keywords users mentioned.",
            }
        )

        response = self.openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=summary_history,
        )
        return response["choices"][0]["message"]["content"].strip()

    def check_limit(self):
        while len(self.history) > self.limit or self.total_tokens > self.token_limit:
            logger.debug("History limit reached")
            summary = self.get_summary()
            logger.debug(summary)
            self.history = self.history[:1]
            self.history.append({"role": "system", "content": summary})

    def add_assistant_message(self, message):
        self.history.append({"role": "assistant", "content": message})
        self.total_tokens += len(message.split())
        self.check_limit()

    def add_user_message(self, message):
        self.history.append({"role": "user", "content": message})
        self.total_tokens += len(message.split())
        self.check_limit()

    def get_history(self):
        return self.history
