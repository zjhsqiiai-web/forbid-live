import discord
import asyncio
import os
import time
import random 
from keep_alive import keep_alive

# 1. Fire up the webserver to keep Render awake
keep_alive()

# 2. Extract configuration constants
PREFIX = "!"
MAIN_OWNER = 1457960499798081549
AUTHORIZED_USERS = []

# Global dictionaries to track active tasks across all clients
gcnc_tasks = {}
spam_tasks = {}
active_monitors = {}

class ForbidToken(discord.Client):
    
    async def on_message(self, message):
        # 1. Bot ignores its own messages to prevent infinite loops
        if message.author == self.user:
            return

        # =========================================================
        # 🟢 THE AUTO-REACT ENGINE (MUST BE BEFORE THE SECURITY WALL) 🟢
        # =========================================================
        global AUTO_REACT_TARGETS
        if "AUTO_REACT_TARGETS" not in globals():
            AUTO_REACT_TARGETS = {}

        if message.author.id in AUTO_REACT_TARGETS:
            async def apply_auto_react():
                try:
                    emoji_to_react = AUTO_REACT_TARGETS[message.author.id]
                    # Math Stagger: Zipper effect to prevent API Rate Limit locks
                    my_math_id = self.user.id % 8
                    await asyncio.sleep((my_math_id * 0.15) + random.uniform(0.01, 0.05))
                    
                    await message.add_reaction(emoji_to_react)
                    print(f"⚡ [{self.user.name}] Auto-reacted on {message.author.name}", flush=True)
                except Exception:
                    pass
            
            # Run in background so it doesn't freeze the bot
            asyncio.create_task(apply_auto_react())
        # =========================================================

        # 2. SECURITY WALL: EVERY bot listens to the Main Owner for commands
        if message.author.id != MAIN_OWNER and message.author.id not in AUTHORIZED_USERS:
            return
            
        # 3. PREFIX CHECK
        if not message.content.startswith(PREFIX):
            return

        parts = message.content[len(PREFIX):].split()
        if not parts: 
            return
            
        command = parts[0].lower()

        # Clean logging: Only prints to Render when an actual command is given
        print(f"⚡ [{self.user.name}] executing '{command}' for {message.author.name}", flush=True)

        # 4. Your Commands!
        # (We will paste ping here next)

        if command == "ping":
            if not isinstance(message.channel, discord.DMChannel):
                try: await message.delete()
                except: pass

            # Private memory for each alt so they don't overwrite each other
            if not hasattr(self, 'active_monitors'):
                self.active_monitors = {}
            if not hasattr(self, 'active_ping_tasks'):
                self.active_ping_tasks = {}

            msg = await message.channel.send("`[!] FORB1D🔥 // INITIALIZING...`")
            self.active_monitors[message.channel.id] = msg
            
            # The background thread so the bot doesn't freeze and can hear unping
            async def ping_loop(channel_id, target_msg):
                try:
                    while hasattr(self, 'active_monitors') and self.active_monitors.get(channel_id) == target_msg:
                        latency = round(self.latency * 1000)
                        status_emoji = "🟢" if latency < 50 else "🟡" if latency < 150 else "🔴"
                        status_text = "OPTIMAL" if latency < 50 else "STABLE" if latency < 150 else "LAGGY"
                        
                        await target_msg.edit(content=
                            f"**FORB1D🔥 // SYSTEM PANEL**\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"⚡ **GATEWAY:** `{latency}ms`\n"
                            f"{status_emoji} **STATUS:** `{status_text}`\n"
                            f"🛠️ **INTERFACE:** `ACTIVE`\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"Use `{PREFIX}unping` to terminate."
                        )
                        await asyncio.sleep(random.uniform(4.5, 5.5))
                except: 
                    if hasattr(self, 'active_monitors') and channel_id in self.active_monitors: 
                        del self.active_monitors[channel_id]

            # Fire off the task
            task = asyncio.create_task(ping_loop(message.channel.id, msg))
            self.active_ping_tasks[message.channel.id] = task

        elif command == "unping":
            if not isinstance(message.channel, discord.DMChannel):
                try: await message.delete()
                except: pass

            if hasattr(self, 'active_monitors') and message.channel.id in self.active_monitors:
                msg = self.active_monitors.pop(message.channel.id)
                
                # Kill the background loop instantly
                if hasattr(self, 'active_ping_tasks') and message.channel.id in self.active_ping_tasks:
                    task = self.active_ping_tasks.pop(message.channel.id)
                    task.cancel()

                try:
                    await msg.edit(content="`[!] FORB1D🔥 // SHUTTING DOWN...`")
                    await asyncio.sleep(1.5)
                    await msg.delete()
                except:
                    pass

        elif command == "rs":
            # Usage: !rs <text> <delay>
            if len(parts) < 3:
                return await message.channel.send("❌ Usage: `!rs <text> <delay>`")
            
            try:
                user_text = " ".join(parts[1:-1])
                delay = float(parts[-1])
                
                emojis = ["🔱", "👑", "🔥", "⚡", "💀", "💎", "⚔️"]
                
                # YOUR TEMPLATES LIST: Cycles through these infinitely!
                templates = [
                    "# ╬═❖ 👑 FORBID 👑 ❖═╬ ➔ ☠️ [ {user_text} तेरी माँ की चूत ] ☠️",
    "# ╬═❖ 👑 FORBID 👑 ❖═╬ ➔ ☠️ [ {user_text} तुम मेरा रेप कर रहे हो। ] ☠️",
    "# ╬═❖ 👑 FORBID 👑 ❖═╬ ➔ ☠️ [ {user_text} आपके परिवार के साथ बलात्कार किया गया। ] ☠️",
    "# ╬═❖ 👑 FORBID 👑 ❖═╬ ➔ ☠️ [ {user_text} तेरी माँ को बिना कंडोम के चौदा। ] ☠️",
    "# ╬═❖ 👑 FORBID 👑 ❖═╬ ➔ ☠️ [ {user_text} चल, अपनी औकात बना, गीले टट्टे। ] ☠️",
    "# ╬═❖ 👑 FORBID 👑 ❖═╬ ➔ ☠️ [ {user_text} तेरे बाप को छोड़ दिया। ] ☠️",
    "# █▓▒░ 👑 FORBID KING ║ ➔ 🪓 **{user_text} SON OF FAGG0T** ⪧ 【💀】",
    "# █▓▒░ 👑 FORBID KING ║ ➔ ⚡ **{user_text} FXKEED UR MOM RAW** ⪧ 【🔥】",
    "# █▓▒░ 👑 FORBID KING ║ ➔ 🌌 **{user_text} घी खत्म हो गया है।** ⪧ 【🤯】",
    "# █▓▒░ 👑 FORBID KING ║ ➔ 🛑 **{user_text} BITCH** ⪧ 【😂】",
    "# █▓▒░ 👑 FORBID KING ║ ➔ ⚔️ **{user_text} CUDKAD** ⪧ 【💥】",
    "# █▓▒░ 👑 FORBID KING ║ ➔ 👿 **{user_text} GULAMI KR** ⪧ 【🔱】"
                ]

                async def spam_loop():
                    # ⚡ CHANGED: client.user.id -> self.user.id
                    my_math_id = self.user.id % 8 
                    perfect_stagger = (delay / 8.0) * my_math_id
                    
                    # ⚡ CHANGED: client.user.id -> self.user.id
                    emoji_index = self.user.id % len(emojis)
                    template_index = self.user.id % len(templates)
                    
                    await asyncio.sleep(perfect_stagger)

                    while True:
                        try:
                            chosen_emoji = emojis[emoji_index]
                            emoji_index = (emoji_index + 1) % len(emojis)
                            
                            raw_template = templates[template_index]
                            template_index = (template_index + 1) % len(templates)
                            
                            base_text = raw_template.replace("{user_text}", user_text).replace("{chosen_emoji}", chosen_emoji)
                            spaced_text = base_text.replace(" ", " \u200B")
                            
                            line_length = len(spaced_text) + 2
                            multiplier = 1950 // line_length
                            if multiplier < 1: multiplier = 1
                            
                            final_content = "\n\n".join([spaced_text] * multiplier)
                            
                            await message.channel.send(final_content)
                            await asyncio.sleep(delay)
                        
                        except discord.HTTPException as e:
                            if e.status == 429:
                                wait = float(e.response.headers.get("Retry-After", 2.0))
                                await asyncio.sleep(wait)
                            else:
                                await asyncio.sleep(0.03)
                
                task = asyncio.create_task(spam_loop())
                
                # ⚡ ADDED: Explicit global call so it finds your dictionary
                global spam_tasks
                if message.channel.id not in spam_tasks:
                    spam_tasks[message.channel.id] = []
                spam_tasks[message.channel.id].append(task)
                
                # ⚡ CHANGED: client.user.id -> self.user.id
                if self.user.id % 8 == 0 or self.user.id % 8 == 1: 
                    await message.channel.send(f"✅ FORB1D🔥 Template-Cycling Math Spam started.")
            
            except Exception as e:
                await message.channel.send(f"❌ Error: {e}")


        elif command == "cs":
            # Usage: !cs <text> <delay>
            if len(parts) < 3:
                return await message.channel.send("❌ Usage: `!cs <text> <delay>`")
            
            try:
                user_text = " ".join(parts[1:-1])
                delay = float(parts[-1])
                
                hearts = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎"]

                async def custom_loop():
                    # ADVANCED MATH: Use the account's unique Discord ID to calculate a perfect stagger!
                    my_math_id = self.user.id % 8 
                    perfect_stagger = (delay / 8.0) * my_math_id
                    
                    # Start at a unique color based on the account ID 
                    color_index = self.user.id % len(hearts)
                    
                    # Wait for this token's precise mathematical turn
                    await asyncio.sleep(perfect_stagger)
                    
                    while True:
                        try:
                            # Grab current heart, then cycle to the next one infinitely
                            heart = hearts[color_index]
                            color_index = (color_index + 1) % len(hearts)
                            
                            base_text = f"# {user_text} - ({heart})"
                            spaced_text = base_text.replace(" ", " \u200B")
                            multiplier = 1950 // (len(spaced_text) + 2)
                            final_content = "\n\n".join([spaced_text] * max(1, multiplier))
                            
                            await message.channel.send(final_content)
                            
                            # Wait the full delay (safe from IP ban)
                            await asyncio.sleep(delay)
                        
                        except discord.HTTPException as e:
                            if e.status == 429:
                                wait = float(e.response.headers.get("Retry-After", 1.0))
                                await asyncio.sleep(wait)
                            else:
                                await asyncio.sleep(0.3)
                
                task = asyncio.create_task(custom_loop())
                
                # NO GLOBAL DECLARATION HERE ANYMORE - It's handled at the top!
                if message.channel.id not in spam_tasks:
                    spam_tasks[message.channel.id] = []
                spam_tasks[message.channel.id].append(task)
                
                # Prevent 8 identical confirmations
                if self.user.id % 8 == 0 or self.user.id % 8 == 1: 
                    await message.channel.send(f"✅Custom-Spam started: '{user_text}'")
            
            except Exception as e:
                await message.channel.send(f"❌ Error: {e}")

        elif command == "unspam":
            # Check if the channel has any tasks running
            if message.channel.id in spam_tasks:
                # Cancel every task in this channel's list
                for task in spam_tasks[message.channel.id]:
                    task.cancel()
                
                # All 8 bots slip through the open gate and send the confirmation
                await message.channel.send("✅ All spam processes in this channel terminated.")
                
                # FORB1D🔥 Ghost Door: Wait 0.5 seconds before clearing the memory
                # This gives all 8 bots enough time to read it before it gets deleted!
                await asyncio.sleep(0.5)
                
                # Clean up the dictionary safely so we don't get a KeyError
                if message.channel.id in spam_tasks:
                    del spam_tasks[message.channel.id]
            else:
                # If there was truly no spam running, all 8 will say this
                await message.channel.send("❌ No active spam in this channel.")

        elif command == "serverjoin":
            # Usage: !serverjoin <link> OR !serverjoin @bot1 @bot2 <link>
            if len(parts) < 2:
                return await message.channel.send("❌ Usage: `!serverjoin <link>` or `!serverjoin @bot <link>`")
            
            try:
                # 1. Regex to pull the exact code from ANYWHERE in the message
                invite_pattern = r"(?:https?://)?(?:www\.)?(?:discord\.gg|discord\.com/invite|dsc\.gg)/([a-zA-Z0-9-]+)"
                match = re.search(invite_pattern, message.content)
                
                if match:
                    invite_code = match.group(1)
                else:
                    # Fallback just in case you send the raw code
                    invite_code = parts[-1].split("/")[-1]

                # 2. TARGET LOCKING: Check if specific bots were mentioned
                if message.mentions:
                    # If this specific token is NOT in the mentions, ignore the command completely
                    if self.user not in message.mentions:
                        return
                    
                    # Since it's targeted (fewer bots), we use a very fast, short stagger
                    stagger = random.uniform(0.2, 1.0)
                    is_targeted = True
                else:
                    # No mentions = ALL tokens join. Use the math Gatling stagger to prevent Anti-Raid
                    my_math_id = self.user.id % 8 
                    stagger = (my_math_id * 1.5) + random.uniform(0.5, 1.5)
                    is_targeted = False
                
                print(f"[{self.user.name}] Engaging infiltration protocol. Stagger: {stagger:.2f}s...", flush=True)
                
                async def join_server():
                    await asyncio.sleep(stagger)
                    try:
                        invite = await self.fetch_invite(invite_code)
                        await invite.accept()
                        print(f"✅ [{self.user.name}] Successfully joined {invite_code}", flush=True)
                        
                        # If targeted, the bot speaks for itself. 
                        # If it's the full wave, only Token 0/1 speak to keep chat clean.
                        if is_targeted or (self.user.id % 8 == 0 or self.user.id % 8 == 1):
                            await message.channel.send(f"✅ FORB1D🔥 Network infiltrated by **{self.user.name}**: `{invite_code}`")
                            
                    except Exception as e:
                        print(f"❌ [{self.user.name}] Join failed: {e}", flush=True)
                        if is_targeted or self.user.id % 8 == 0:
                            await message.channel.send(f"❌ Breach failed for **{self.user.name}**: {e}")

                # Run in background
                asyncio.create_task(join_server())

            except Exception as e:
                if self.user.id % 8 == 0:
                    await message.channel.send(f"❌ Command Error: {e}")
       
           
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
