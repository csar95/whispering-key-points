import os
import discord
from discord import app_commands, Intents, Client, Object, Interaction
import responses_controller
from responses import *
from validators import url
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


CHECKPOINT = "facebook/bart-large-cnn"


async def send_message(message, message_content, is_private):
    try:
        if is_private:
            await message.author.send(default_response)
        else:
            await message.channel.send(default_response)

    except Exception as e:
        print(e)


def run_discord_bot():
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    intents = Intents.default()
    intents.message_content = True    
    client = Client(intents=intents)

    # The tree holds all of your application commands
    tree = app_commands.CommandTree(client)

    tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT)
    model = AutoModelForSeq2SeqLM.from_pretrained(CHECKPOINT)

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

    @tree.command(name="help", description="Shows help for the bot")
    async def help(interaction: Interaction):
        '''
            Handles the help /chatgpt. With this command the user recibes help on how to use the bot.
        '''
        await interaction.response.send_message(help_response, ephemeral=True)
            
    @tree.command(name="chatgpt", description="Use OpenAI API to analyze the transcript of a YouTube video")
    @app_commands.describe(yt_url="URL of the YouTube video that is going to be analyze",
                           language="Language of the audio",
                           prompt="Tell ChatGPT what you want it to do with the transcript",
                           model_version="ID of the model to use")
    @app_commands.choices(language=[app_commands.Choice(name="English", value="en"), app_commands.Choice(name="Spanish", value="es"), app_commands.Choice(name="Multi", value="")],
                          model_version=[app_commands.Choice(name="GPT-3.5", value="gpt-3.5-turbo"), app_commands.Choice(name="GPT-4", value="gpt-4")])
    async def chatgpt(interaction: Interaction, yt_url: str, language: app_commands.Choice[str], prompt: str, model_version: app_commands.Choice[str]):
        '''
            Handles the command /chatgpt. With this command the user can pass a URL of a YouTube video and
            tell ChatGPT what to do with it.
        '''
        await interaction.response.defer()  # ephemeral=True)

        print(f"{interaction.user} send /chatgpt command. yt_url: '{yt_url}' | language: '{language.name}' | prompt: '{prompt}' | model_version: '{model_version.name}'")

        if not url(yt_url):
            await interaction.followup.send(f"URL {yt_url} is not valid")  # , ephemeral=True)
        
        else:
            try:
                response = responses_controller.get_chatGPT_response(yt_url, language.value, prompt, model_version.value)

            except Exception as err:
                response = f"An error occurred: {str(err)}"

            finally:
                if len(response) < 2_000:
                    # With ephemeral=True only the user that runs the command can see it
                    await interaction.followup.send(response)  # , ephemeral=True)

                else:
                    response_words = response.split(' ')
                    for list_of_words in [response_words[i:i+250] for i in range(0, len(response_words), 250)]:
                        await interaction.followup.send(' '.join(list_of_words))  # , ephemeral=True)

    
    @tree.command(name="summarize", description="Use a Hugging Face model to summarize the transcript of a YouTube video")
    @app_commands.describe(yt_url="URL of the YouTube video that is going to be analyze",
                           language="Language of the audio",
                           min_length="The minimum length of the summary to be generated",
                           max_length="The maximum length of the summary to be generated")
    @app_commands.choices(language=[app_commands.Choice(name="English", value="en"), app_commands.Choice(name="Spanish", value="es"), app_commands.Choice(name="Multi", value="")])
    async def summarize(interaction: Interaction, yt_url: str, language: app_commands.Choice[str], min_length: int = 120, max_length: int = 180):
        '''
            Handles the command /summarize. With this command the user can pass a URL of a YouTube video and
            make use of a model from the Hugging Face Hub to summarize the transcript.
        '''
        await interaction.response.defer()  # ephemeral=True)

        print(f"{interaction.user} send /summarize command. yt_url: '{yt_url}' | language: '{language.name}' | min_length: '{min_length}' | max_length: '{max_length}'")

        if not url(yt_url):
            await interaction.followup.send(f"URL {yt_url} is not valid")  # , ephemeral=True)
        
        else:
            try:
                response = responses_controller.get_summary(yt_url, language.value, min_length, max_length, tokenizer, model)

            except Exception as err:
                response = f"An error occurred: {str(err)}"

            finally:
                if len(response) < 2_000:
                    # With ephemeral=True only the user that runs the command can see it
                    await interaction.followup.send(response)  # , ephemeral=True)

                else:
                    response_words = response.split(' ')
                    for list_of_words in [response_words[i:i+250] for i in range(0, len(response_words), 250)]:
                        await interaction.followup.send(' '.join(list_of_words))  # , ephemeral=True)

    client.run(TOKEN)
