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
        # 1. Print every single message it sees to the Render logs
        print(f"👀 [{self.user.name}] saw message from {message.author.id}: {message.content}")

        # 2. Check for the prefix first
        if not message.content.startswith(PREFIX):
            return

        print(f"✅ [{self.user.name}] saw a command prefix!")

        # 3. TEMPORARILY DISABLED SECURITY LOCKS FOR TESTING
        # (We will turn these back on once we prove it works)
        # if message.author.id == self.user.id: return
        # if message.author.id != MAIN_OWNER ... return

        parts = message.content[len(PREFIX):].split()
        if not parts:
            return
        command = parts[0].lower()

        # 4. Commands
        if command == "ping":
            await message.channel.send(f"🏓 FORB1D🔥 [{self.user.name}] is ONLINE!")

        elif command == "stopgcnc":
            await message.channel.send(f"🛑 FORB1D🔥 [{self.user.name}] received stop command.")
# 4. Master Engine Initialization
async def main():
    raw_tokens = os.environ.get('BOT_TOKENS')
    if not raw_tokens:
        print("❌ ERROR: No BOT_TOKENS found in Render Environment Variables!")
        return

    token_list = [t.strip() for t in raw_tokens.split(',') if t.strip()]
    clients = []

    print(f"⚡ Initializing multi-token array with {len(token_list)} targets...")

    # Create a shielded login function so dead tokens don't crash the good ones
    async def safe_start(client, token):
        try:
            await client.start(token)
        except Exception as e:
            print(f"💀 DEAD TOKEN SKIPPED [{token[:10]}...]: {e}")

    # Build client instances for every token
    for token in token_list:
        client = ForbidToken()
        # Use our shielded start function instead of the raw one
        clients.append(safe_start(client, token))
        # Brief sleep during setup loop to keep connections clean
        await asyncio.sleep(0.5)

    # Fire all connections concurrently
    print("🚀 Firing connections concurrently...")
    await asyncio.gather(*clients)

if __name__ == "__main__":
    asyncio.run(main())
