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
        # If this doesn't print, Discord is blocking the websocket connection
        print(f"🔥 [{self.user.name}] WEBSOCKET FULLY CONNECTED! I am alive!", flush=True)

    async def on_message(self, message):
        # 1. Ignore friendly fire (prevents endless spam loops)
        if message.author.id == self.user.id:
            return

        # 2. Check for the prefix first (ignores normal chatting instantly)
        if not message.content.startswith(PREFIX):
            return

        # 3. SECURITY LOCK: Only your Main Account can command the botnet
        if message.author.id != MAIN_OWNER and message.author.id not in AUTHORIZED_USERS:
            return

        # Parse the command
        parts = message.content[len(PREFIX):].split()
        if not parts:
            return
        command = parts[0].lower()

        # Clean logging: Only prints to Render when YOU give an actual command
        print(f"⚡ [{self.user.name}] executing '{command}' for {message.author.name}", flush=True)

        # 4. Your Commands!
        # 4. Your Commands!
        if command == "ping":
            if not isinstance(message.channel, discord.DMChannel):
                try: await message.delete()
                except: pass

            # Create the private memory bank if it doesn't exist yet
            if not hasattr(self, 'active_monitors'):
                self.active_monitors = {}

            msg = await message.channel.send("`[!] FORB1D🔥 // INITIALIZING...`")
            self.active_monitors[message.channel.id] = msg
            
            try:
                # Loop runs perfectly because it yields to asyncio.sleep
                while self.active_monitors.get(message.channel.id) == msg:
                    # Swapped client.latency to self.latency for the new architecture
                    latency = round(self.latency * 1000)
                    status_emoji = "🟢" if latency < 50 else "🟡" if latency < 150 else "🔴"
                    status_text = "OPTIMAL" if latency < 50 else "STABLE" if latency < 150 else "LAGGY"
                    
                    await msg.edit(content=
                        f"**FORB1D🔥 // SYSTEM PANEL**\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"⚡ **GATEWAY:** `{latency}ms`\n"
                        f"{status_emoji} **STATUS:** `{status_text}`\n"
                        f"🛠️ **INTERFACE:** `ACTIVE`\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"Use `{PREFIX}unping` to terminate."
                    )
                    # Smart randomization to avoid API bans
                    await asyncio.sleep(random.uniform(4.5, 5.5))
            except: 
                if message.channel.id in self.active_monitors: 
                    del self.active_monitors[message.channel.id]

        elif command == "unping":
            if hasattr(self, 'active_monitors') and message.channel.id in self.active_monitors:
                msg = self.active_monitors.pop(message.channel.id)
                try:
                    await msg.edit(content="`[!] FORB1D🔥 // SHUTTING DOWN...`")
                    await asyncio.sleep(1.5)
                    await msg.delete()
                except:
                    pass
           
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
