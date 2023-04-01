import os
import discord
from discord import app_commands, Intents, Client, Object, Interaction
import responses_controller
from validators import url


async def send_message(message, message_content, is_private):
    try:
        response = responses_controller.get_response(input=message_content)
        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)

    except Exception as e:
        print(e)

def run_discord_bot():
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    intents = Intents.default()
    intents.message_content = True    
    client = Client(intents=intents)

    # The tree holds all of your application commands
    tree = app_commands.CommandTree(client)

    @client.event
    async def on_ready():
        '''
            Triggers each time the code is run and the bot is ready to be used on the server.
            Is's necessary to sync the commands to discord once the client is ready.
        '''
        await tree.sync()
        print(f"{client.user} is now running!")

    @client.event
    async def on_message(message):
        '''
            Handles the messages that come into the Discord server and the response
        '''
        
        if message.author == client.user:  # client.user is the bot
            return

        username = str(message.author)
        message_content = str(message.content)
        channel = str(message.channel)

        print(f"{username} said '{message_content}' ({channel})")

        if message_content[0] == '?':
            # Answer in a private conversation to the user
            message_content = message_content[1:]
            await send_message(message, message_content, is_private=True)
        else:
            await send_message(message, message_content, is_private=False)
            
    @tree.command(name="chatgpt", description="My first application Command")
    @app_commands.describe(yt_url="URL of the YouTube video that is going to be analyze", language="Language of the audio", prompt="Tell ChatGPT what you want it to do with the transcript", model_version="ID of the model to use")
    @app_commands.choices(language=[app_commands.Choice(name="English", value="en"), app_commands.Choice(name="Spanish", value="es"), app_commands.Choice(name="Multi", value="")],
                          model_version=[app_commands.Choice(name="GPT-3.5", value="gpt-3.5-turbo"), app_commands.Choice(name="GPT-4", value="gpt-4")])
    async def chatgpt(interaction: Interaction, yt_url: str, language: app_commands.Choice[str], prompt: str, model_version: app_commands.Choice[str]):
        '''
            Handles the command /chatgpt. With this command the user can pass a URL of a YouTube video and tell ChatGPT what to do with it.
        '''
        await interaction.response.defer(ephemeral=True)

        if not url(yt_url):
            await interaction.followup.send(f"URL {yt_url} is not valid", ephemeral=True)
        
        else:
            try:
                response = responses_controller.get_chatGPT_response(yt_url, language.value, prompt, model_version.value)

            except Exception as err:
                response = f"An error occurred: {str(err)}"

            finally:
                if len(response) < 2_000:
                    # With ephemeral=True only the user that runs the command can see it
                    await interaction.followup.send(response, ephemeral=True)

                else:
                    response_words = response.split(' ')
                    for list_of_words in [response_words[i:i+250] for i in range(0, len(response_words), 250)]:
                        await interaction.followup.send(' '.join(list_of_words), ephemeral=True)

    client.run(TOKEN)
