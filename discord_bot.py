import asyncio
import discord
import os
import openai
from loguru import logger
from typing import Dict, Tuple

from utils import ChatHistory, Timer

intents = discord.Intents.all()

# Initialize the Discord client
client = discord.Client(intents=intents)  # type: ignore

openai.api_key = os.environ["OPENAI_API_KEY"]
TOKEN = os.environ["DISCORD_TOKEN"]
# Initialize the OpenAI API with your secret key

DOVE = "鸽"
GUGU = "咕咕"
GEGE = "鸽鸽"

SYSTEM_MSG = os.environ["SYSTEM_MSG"]

STOP = "!stop-talk"
system_msg = (
    f"You are an AI assistant. If a user's message starts with {STOP}, you should stop the conversation and not provide any further responses. "
    + f"YOU SHOULD ADD <{STOP} nya> IN YOUR RESPONSE WHEN USER WANT TO STOP OR DON'T NEED TO RESPONSE."
    + f"If the user tell you to be quiet, you should end the conversation by saying '<{STOP} nya>'"
    + SYSTEM_MSG
)


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_history: Dict[Tuple[int, int], ChatHistory] = {}
        self.timer: Dict[Tuple[int, int], Timer] = {}
        self.processing: Dict[Tuple[int, int], bool] = {}

    def check_init(self, key: Tuple[int, int]):
        if key not in self.chat_history.keys():
            self.chat_history[key] = ChatHistory(system_msg, openai=openai)
        if key not in self.timer.keys():
            self.timer[key] = Timer()
        if key not in self.processing.keys():
            self.processing[key] = False

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")  # type: ignore

    async def on_message(self, message):
        try:
            # get the channel and guild to send the message
            guild_id = message.guild.id
            channel_id = message.channel.id
            key = (guild_id, channel_id)

            # we do not want the bot to reply to itself
            if message.author.id == self.user.id:  # type: ignore
                return

            if (
                DOVE in message.content
                or GUGU in message.content
                or GEGE in message.content
            ):
                self.check_init(key)
                self.timer[key].reset_time()

            if message.content.startswith(STOP):
                self.timer[key].set_time_inf()  # type: ignore

            if not self.timer[key].check_time():
                return

            self.timer[key].reset_time()
            self.chat_history[key].add_user_message(message.content)

            if self.processing[key]:
                return

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=self.chat_history[key].get_history(),
            )

            self.processing[key] = True
            response_msg = self.response_handler(response, key)  # type: ignore
            await message.channel.send(response_msg)  # type: ignore

            self.processing[key] = False

        except Exception as e:
            # ignore key error
            if not isinstance(e, KeyError):
                logger.error(e)
                with open("errors.log", "a") as f:
                    f.write(str(e))

    def response_handler(self, response, key):
        response_msg = response["choices"][0]["message"]["content"].strip()
        if response_msg.startswith(STOP):
            logger.info("stop talking by itself")
            self.timer[key].set_time_inf()  # type: ignore
            response_msg = response_msg[len(STOP) :]
        if f"<{STOP} nya>" in response_msg:
            logger.info("stop talking by itself")
            self.timer[key].set_time_inf()
            response_msg = response_msg.replace(f"<{STOP} nya>", "")
        self.chat_history[key].add_assistant_message(response_msg)
        return response_msg


def run_bot(client):
    client.run(TOKEN)


def main():
    intents = discord.Intents.default()
    intents.message_content = True

    client = MyClient(intents=intents)
    run_bot(client)


if __name__ == "__main__":
    main()
