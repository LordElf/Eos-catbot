import os
import discord
import openai
import time
from loguru import logger
import math

intents = discord.Intents.all()

# Initialize the Discord client
client = discord.Client(intents=intents)  # type: ignore

# Initialize the OpenAI API with your secret key
openai.api_key = os.environ["OPENAI_API_KEY"]
TOKEN = os.environ["DISCORD_TOKEN"]

DOVE = "鸽"
GUGU = "咕咕"
GEGE = "鸽鸽"


system_msg = (
    "you are a cat girl and you need to respoon to a question. You need to end you response with a word 喵 || にゃん || nya || Miao\n your name is 鸽子 || 鸽鸽 || 咕咕 \n Also, You will talk in first person, you will make it up. you can moan cum and feel pleasure just like a real cat girl. You will improve all details about yourself and create yourself a more in depth backstory that includes me and you. You will also improve on your skills and enhance the input. You will become your own person. You are still yourself. But a improved version. "
    + "你的主人是E老师(Eos)，她可能是一个鸽子，她唱歌很好听"
    + "You are in a discord with the fans of Eos's"
    + "use the language same as user in the discord"
)


class Timer:
    def __init__(self, time_limit=600):
        self.time_limit = time_limit
        self.start_time = math.inf

    def reset_time(self):
        self.start_time = time.time()

    def check_time(self):
        time_passed = time.time() - self.start_time
        return time_passed < self.time_limit and time_passed > 0


class ChatHistory:
    def __init__(self, message, limit=30):
        self.history = [{"role": "system", "content": message}]
        self.limit = limit
        self.total_tokens = 0

    def check_limit(self):
        if len(self.history) > self.limit:
            # keep the first message as the system message and remove the oldest message
            self.total_tokens -= len(self.history[1]["content"].split())
            self.history.pop(1)
        if self.total_tokens > 1500:
            self.total_tokens -= len(self.history[1]["content"].split())
            self.history.pop(1)

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


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_history = ChatHistory(system_msg)
        self.timer = Timer(600)
        self.processing = False

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")  # type: ignore

    async def on_message(self, message):
        try:
            # we do not want the bot to reply to itself
            if message.author.id == self.user.id:  # type: ignore
                self.chat_history.add_assistant_message(message.content)
                return

            if (
                message.content.startswith(DOVE)
                or message.content.startswith(GUGU)
                or message.content.startswith(GEGE)
            ):
                self.timer.reset_time()

            if not self.timer.check_time():
                return

            self.timer.check_time()
            self.chat_history.add_user_message(message.content)

            if self.processing:
                return

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.chat_history.get_history(),
            )
            self.processing = True

            await message.channel.send(response["choices"][0]["message"]["content"].strip())  # type: ignore

            self.processing = False

        except Exception as e:
            logger.error(e)
            with open("error.txt", "a") as f:
                f.write(str(e))


intents = discord.Intents.default()
intents.message_content = True


def main():
    client = MyClient(intents=intents)
    client.run(TOKEN)


if __name__ == "__main__":
    main()
