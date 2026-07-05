import discord
import asyncio
import os
import time
from keep_alive import keep_alive

# 1. Fire up the webserver to keep Render awake
keep_alive()

# 2. Extract configuration constants
PREFIX = "!"
MAIN_OWNER = 1457960499798081549
AUTHORIZED_USERS = []

# Global dictionary to track active tasks across all clients
gcnc_tasks = {}
spam_tasks = {}

# 3. Define the Custom Client Blueprint
class ForbidToken(discord.Client):
    async def on_ready(self):
        print(f"🔥 [{self.user.name}] Connected & Ready to operate.")

    async def on_message(self, message):
        # Ignore messages from other bots or itself to avoid loops
        if message.author.id == self.user.id:
            return

        # Basic command handling
        if not message.content.startswith(PREFIX):
            return

        # Check authorization
        if message.author.id != MAIN_OWNER and message.author.id not in AUTHORIZED_USERS:
            return

        # Parse command name and arguments
        parts = message.content[len(PREFIX):].split()
        if not parts:
            return
        command = parts[0].lower()

        # Place your !gcnc, !stopgcnc, !cs, and other command blocks right here!
        # Example for stopgcnc:
        if command == "stopgcnc":
            global gcnc_tasks
            if message.channel.id in gcnc_tasks and gcnc_tasks[message.channel.id]:
                for task in gcnc_tasks[message.channel.id]:
                    task.cancel()
                gcnc_tasks[message.channel.id] = []
                if self.user.id % 8 == 0:
                    await message.channel.send("🛑 FORB1D🔥 GC Name Flasher terminated in this chat.")
            else:
                if self.user.id % 8 == 0:
                    await message.channel.send("⚠️ No active FORB1D🔥 GC Name Flasher running here.")

# 4. Master Engine Initialization
async def main():
    raw_tokens = os.environ.get('BOT_TOKENS')
    if not raw_tokens:
        print("❌ ERROR: No BOT_TOKENS found in Render Environment Variables!")
        return

    token_list = [t.strip() for t in raw_tokens.split(',') if t.strip()]
    clients = []

    print(f"⚡ Initializing multi-token array with {len(token_list)} targets...")

    # Build client instances for every token
    for token in token_list:
        client = ForbidToken()
        clients.append(client.start(token))
        # Brief sleep during setup loop to keep connections clean
        await asyncio.sleep(0.5)

    # Fire all 8 connections concurrently inside a single Python engine
    print("🚀 Firing connections concurrently...")
    await asyncio.gather(*clients)

if __name__ == "__main__":
    asyncio.run(main())
