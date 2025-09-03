import os
import discord
from discord import app_commands
from discord.ext import commands
from inference_sdk import InferenceHTTPClient

# Set intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot with command prefix (not required for slash cmds but common)
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize Roboflow client
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key=os.getenv("ROBOFLOW_API_KEY")
)

# On ready event
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# Slash command to detect Clash of Clans buildings in an uploaded image
@bot.tree.command(name="detect", description="Detect Clash of Clans buildings in an image")
@app_commands.describe(image="Upload the Clash of Clans base image")
async def detect(interaction: discord.Interaction, image: discord.Attachment):
    await interaction.response.defer()  # Acknowledge the command has been received

    try:
        # Download image bytes
        img_bytes = await image.read()
        temp_path = "temp.jpg"
        with open(temp_path, "wb") as f:
            f.write(img_bytes)

        # Send image to Roboflow for inference
        result = CLIENT.infer(temp_path, model_id="clash-of-clans-vop4y/4")

        # Extract detected classes
        detected_classes = set()
        for obj in result.get("predictions", []):
            detected_classes.add(obj.get("class", "Unknown"))

        # Prepare reply message
        if detected_classes:
            detected_str = ", ".join(detected_classes)
            reply = f"Detected Clash of Clans buildings: {detected_str}"
        else:
            reply = "No Clash of Clans buildings detected."

        await interaction.followup.send(reply)

    except Exception as e:
        await interaction.followup.send(f"Error processing image: {e}")

# Run the bot with token from environment
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
