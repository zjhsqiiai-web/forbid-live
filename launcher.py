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
        # 4. Your Commands!
        if command == "ping":
            if not isinstance(message.channel, discord.DMChannel):
                try: 
                    await message.delete()
                except: 
                    pass

            # Create a private memory bank for THIS specific alt if it doesn't exist yet
            if not hasattr(self, 'active_monitors'):
                self.active_monitors = {}

            msg = await message.channel.send("`[!] FORB1D🔥 // INITIALIZING...`")
            # Save the message to this bot's private memory
            self.active_monitors[message.channel.id] = msg

        elif command == "unping":
            # Check if this specific alt has a memory of a ping in this channel
            if hasattr(self, 'active_monitors') and message.channel.id in self.active_monitors:
                msg = self.active_monitors.pop(message.channel.id)
                
                # Wrapped in a try/except so if Discord blocks it, Render tells us exactly why
                try:
                    await msg.edit(content="`[!] FORB1D🔥 // SHUTTING DOWN...`")
                    await asyncio.sleep(1.5)
                    await msg.delete()
                except Exception as e:
                    print(f"❌ [{self.user.name}] failed to unping: {e}", flush=True)

        elif command == "gcnc":
            # 1. Strip trigger message
            if not isinstance(message.channel, discord.DMChannel):
                try: await message.delete()
                except: pass

            # 2. Extract arguments (e.g., !gcnc TargetName Interval)
            args = message.content[len(PREFIX):].split()
            # If no name is provided, use your signature fallback
            target_name = " ".join(args[1:]) if len(args) > 1 else "FORB1D🔥"

            # 3. Define the asynchronous execution loop
            async def flash_loop(client_instance, channel_obj, name_to_flash):
                print(f"⚡ [{client_instance.user.name}] loop initiated for channel {channel_obj.id}", flush=True)
                while True:
                    try:
                        # Perform the high-speed name edit
                        await channel_obj.edit(name=name_to_flash)
                        # Clean, low-latency interval sleep to keep CPU usage low
                        await asyncio.sleep(1.2) 
                    except asyncio.CancelledError:
                        print(f"🛑 [{client_instance.user.name}] loop successfully cancelled.", flush=True)
                        break
                    except Exception as e:
                        print(f"⚠️ [{client_instance.user.name}] flash error: {e}", flush=True)
                        await asyncio.sleep(3) # Dynamic backing off if Discord hits a rate limit

            # 4. Check if a task is already running in this channel for this bot
            if not hasattr(self, 'active_gcnc_tasks'):
                self.active_gcnc_tasks = {}

            if message.channel.id in self.active_gcnc_tasks:
                await message.channel.send(f"⚠️ [{self.user.name}] already active in this sector.")
                return

            # 5. Spawn the background thread task safely inside the shared event loop
            task = asyncio.create_task(flash_loop(self, message.channel, target_name))
            self.active_gcnc_tasks[message.channel.id] = task

        elif command == "stopgcnc":
            if not isinstance(message.channel, discord.DMChannel):
                try: await message.delete()
                except: pass

            # Terminate the background task cleanly without breaking the bot engine
            if hasattr(self, 'active_gcnc_tasks') and message.channel.id in self.active_gcnc_tasks:
                task = self.active_gcnc_tasks.pop(message.channel.id)
                task.cancel()
                await message.channel.send(f"🛑 FORB1D🔥 [{self.user.name}] loop cut.")
            else:
                await message.channel.send(f"❌ [{self.user.name}] No active task detected here.")
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
