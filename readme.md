``` bash
docker build -t discord_chat_bot .
```
You need a .env file with the following variables:
``` bash
DISCORD_TOKEN=your_discord_token
OPENAI_API_KEY=your_openai_api_key
SYSTEM_MSG="<your system message for the bog>"
```
Then run the container:

``` bash
docker run -d --env-file .env --name discord_chat_bot --restart unless-stopped discord_chat_bot
```