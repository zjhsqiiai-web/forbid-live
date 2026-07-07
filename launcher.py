import discord
import asyncio
import os
import time
import random 
import re
import logging
from keep_alive import keep_alive

# 1. TURN ON DISCORD X-RAY (Keeps your general boot-up info flowing)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s: %(message)s')

# 2. 🛑 THE GAG ORDER: Mutes the specific HTTP rate limit spam
logging.getLogger('discord.http').setLevel(logging.ERROR)

# 3. SMART LOG MATRIX TIMER (For your custom loops)
global_last_log = 0

# 🟢 THE SWARM REGISTRY: Tracks breathing tokens in real-time
ACTIVE_SWARM = []

# 2. Extract configuration constants
PREFIX = "^"
MAIN_OWNER = 1457960499798081549
AUTHORIZED_USERS = []

# Global dictionaries to track active tasks across all clients
gcnc_tasks = {}
spam_tasks = {}
active_monitors = {}

class ForbidToken(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.raw_session = None  # This will hold our high-speed socket

    # 🛑 ADD THIS RIGHT AT THE TOP OF YOUR CLASS
    async def on_ready(self):
        import aiohttp
        print(f"🟢 [{self.user.name}] Linked to Gateway & Operational.", flush=True)
        
        # 🟢 HEALTH MONITOR: Bot registers itself as ALIVE
        if self.user.id not in ACTIVE_SWARM:
            ACTIVE_SWARM.append(self.user.id)
            print(f"📊 [System] Swarm Capacity updated: {len(ACTIVE_SWARM)} Nodes Active.", flush=True)

        self.raw_session = aiohttp.ClientSession(headers={
            "Authorization": self.http.token,
            "Content-Type": "application/json"
        })
        self.loop.create_task(self.ram_cleaner_loop())

    # 🛑 ADD THIS RIGHT UNDER ON_READY
    async def on_disconnect(self):
        # 🛑 HEALTH MONITOR: Bot registers itself as DEAD and forces math recalculation
        if self.user.id in ACTIVE_SWARM:
            ACTIVE_SWARM.remove(self.user.id)
            print(f"⚠️ [System] {self.user.name} dropped connection! Swarm auto-healed to {len(ACTIVE_SWARM)} Nodes.", flush=True)
                
    
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
                   # print(f"⚡ [{self.user.name}] Auto-reacted on {message.author.name}", flush=True)
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
                    # 🟢 ENTERPRISE MATH: Auto-adjusts to the live swarm size!
                    current_swarm_size = max(1, len(ACTIVE_SWARM))
                    
                    try:
                        # Bot finds its exact place in the live line-up (0, 1, 2, 3...)
                        my_math_id = ACTIVE_SWARM.index(self.user.id)
                    except ValueError:
                        my_math_id = 0
                        
                    perfect_stagger = (delay / float(current_swarm_size)) * my_math_id
                    
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
                            
                            # 🚀 PURE SOCKET INJECTION INSTEAD
                            url = f"https://discord.com/api/v9/channels/{message.channel.id}/messages"
                            payload = {"content": final_content}
                            
                            async with self.raw_session.post(url, json=payload) as response:
                                if response.status == 429:
                                    rate_data = await response.json()
                                    retry_after = rate_data.get("retry_after", 1.0)
                                    
                                    # 🟢 THIS IS THE NEW PART YOU NEED TO ADD:
                                    global global_last_log
                                    if time.time() - global_last_log > 60:
                                        print(f"⚠️ [System] Network Rate Limit hit. Pausing for {retry_after}s. (Muting further logs for 60s)", flush=True)
                                        global_last_log = time.time()
                                        
                                    await asyncio.sleep(retry_after)
                                else:
                                    await asyncio.sleep(delay)
                        
                        except Exception as e:
                            print(f"⚠️ Socket Error: {e}", flush=True)
                            await asyncio.sleep(0.1)
                
                task = asyncio.create_task(spam_loop(), name=f"spam_{message.channel.id}")
                
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
                    # 🟢 ENTERPRISE MATH: Auto-adjusts to the live swarm size!
                    current_swarm_size = max(1, len(ACTIVE_SWARM))
                    
                    try:
                        # Bot finds its exact place in the live line-up (0, 1, 2, 3...)
                        my_math_id = ACTIVE_SWARM.index(self.user.id)
                    except ValueError:
                        my_math_id = 0
                        
                    perfect_stagger = (delay / float(current_swarm_size)) * my_math_id
                    
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
                            
                            # 🚀 PURE SOCKET INJECTION INSTEAD
                            url = f"https://discord.com/api/v9/channels/{message.channel.id}/messages"
                            payload = {"content": final_content}
                            
                            async with self.raw_session.post(url, json=payload) as response:
                                if response.status == 429:
                                    rate_data = await response.json()
                                    retry_after = rate_data.get("retry_after", 1.0)
                                    
                                    # 🟢 THIS IS THE NEW PART YOU NEED TO ADD:
                                    global global_last_log
                                    if time.time() - global_last_log > 60:
                                        print(f"⚠️ [System] Network Rate Limit hit. Pausing for {retry_after}s. (Muting further logs for 60s)", flush=True)
                                        global_last_log = time.time()
                                        
                                    await asyncio.sleep(retry_after)
                                else:
                                    await asyncio.sleep(delay)
                        
                        except Exception as e:
                            print(f"⚠️ Socket Error: {e}", flush=True)
                            await asyncio.sleep(0.1)
                
                task = asyncio.create_task(custom_loop(), name=f"spam_{message.channel.id}")
                
                # NO GLOBAL DECLARATION HERE ANYMORE - It's handled at the top!
                if message.channel.id not in spam_tasks:
                    spam_tasks[message.channel.id] = []
                spam_tasks[message.channel.id].append(task)
                
                # Prevent 8 identical confirmations
                if self.user.id % 8 == 0 or self.user.id % 8 == 1: 
                    await message.channel.send(f"✅Custom-Spam started: '{user_text}'")
            
            except Exception as e:
                await message.channel.send(f"❌ Error: {e}")

        # =========================================================
        # 🛑 YOU WERE MISSING THIS HEADER RIGHT HERE 🛑
        # =========================================================
        elif command == "unspam":
            
            # Direct Core Search: Find and kill tasks by their hidden registry names
            killed = False
            for task in asyncio.all_tasks():
                if task.get_name() == f"spam_{message.channel.id}":
                    task.cancel()
                    killed = True
            
            # Staggered confirmation so all 8 bots reply cleanly
            await asyncio.sleep(self.user.id % 8 * 1.0)
            if killed:
                await message.channel.send(f"🛑 FORB1D🔥 **{self.user.name}** terminated all zombie spam loops here.")
            else:
                await message.channel.send(f"⚠️ **{self.user.name}** found no active spam in this channel.")

        elif command == "serverjoin":
            # Usage: !serverjoin <link> OR !serverjoin @bot <link>
            if len(parts) < 2:
                return await message.channel.send("❌ Usage: `!serverjoin <link>` or `!serverjoin @bot <link>`")
            
            try:
                # 1. Regex to pull the exact code from ANYWHERE in the message
                invite_pattern = r"(?:https?://)?(?:www\.)?(?:discord\.gg|discord\.com/invite|dsc\.gg)/([a-zA-Z0-9-]+)"
                match = re.search(invite_pattern, message.content)
                
                if match:
                    invite_code = match.group(1)
                else:
                    invite_code = parts[-1].split("/")[-1]

                # 2. TARGET LOCKING
                if message.mentions:
                    # If this specific token is NOT in the mentions, ignore completely
                    if self.user not in message.mentions:
                        return
                    
                    stagger = random.uniform(0.2, 1.0)
                else:
                    # No mentions = ALL tokens join. Use the math Gatling stagger
                    my_math_id = self.user.id % 8 
                    stagger = (my_math_id * 1.5) + random.uniform(0.5, 1.5)
                
                print(f"[{self.user.name}] Engaging infiltration protocol. Stagger: {stagger:.2f}s...", flush=True)
                
                async def join_server():
                    await asyncio.sleep(stagger)
                    try:
                        invite = await self.fetch_invite(invite_code)
                        await invite.accept()
                        print(f"✅ [{self.user.name}] Successfully joined {invite_code}", flush=True)
                        
                        # ⚡ CHANGED: Every bot that joins will now announce it in chat
                        await message.channel.send(f"✅ FORB1D🔥 Network infiltrated by **{self.user.name}**: `{invite_code}`")
                            
                    except Exception as e:
                        print(f"❌ [{self.user.name}] Join failed: {e}", flush=True)
                        # Every bot that fails will also report its failure
                        await message.channel.send(f"❌ Breach failed for **{self.user.name}**: {e}")

                # Run in background
                asyncio.create_task(join_server())

            except Exception as e:
                if self.user.id % 8 == 0:
                    await message.channel.send(f"❌ Command Error: {e}")

        elif command == "serverleave":
            # Usage: !serverleave <link> OR !serverleave @bot <link>
            if len(parts) < 2:
                return await message.channel.send("❌ Usage: `!serverleave <link>` or `!serverleave @bot <link>`")
            
            try:
                # 1. Regex to pull the exact code from ANYWHERE in the message
                invite_pattern = r"(?:https?://)?(?:www\.)?(?:discord\.gg|discord\.com/invite|dsc\.gg)/([a-zA-Z0-9-]+)"
                match = re.search(invite_pattern, message.content)
                
                if match:
                    invite_code = match.group(1)
                else:
                    invite_code = parts[-1].split("/")[-1]

                # 2. TARGET LOCKING: Check if specific bots were mentioned
                if message.mentions:
                    if self.user not in message.mentions:
                        return
                    # Fast extraction for targeted bots
                    stagger = random.uniform(0.2, 1.0)
                    is_targeted = True
                else:
                    # Math stagger for full wave extraction to avoid API spam flags
                    my_math_id = self.user.id % 8 
                    stagger = (my_math_id * 1.0) + random.uniform(0.2, 1.0)
                    is_targeted = False
                
                print(f"[{self.user.name}] Engaging extraction protocol. Stagger: {stagger:.2f}s...", flush=True)
                
                async def leave_server():
                    await asyncio.sleep(stagger)
                    try:
                        # Fetch the invite to identify WHICH server it belongs to
                        invite = await self.fetch_invite(invite_code)
                        guild_id = invite.guild.id
                        
                        # Check if the bot is actually inside this specific server
                        guild_to_leave = self.get_guild(guild_id)
                        
                        if guild_to_leave:
                            await guild_to_leave.leave()
                            print(f"✅ [{self.user.name}] Successfully extracted from {guild_to_leave.name}", flush=True)
                            
                            # ⚡ CHANGED: Every bot that successfully leaves will now announce it
                            await message.channel.send(f"✅ FORB1D🔥 **{self.user.name}** extracted from: `{guild_to_leave.name}`")
                        else:
                            print(f"⚠️ [{self.user.name}] Aborted: Not in network {invite_code}", flush=True)
                            
                            # ⚡ CHANGED: Every bot will announce if it wasn't in the server
                            await message.channel.send(f"⚠️ **{self.user.name}** is not in that network.")
                                
                    except Exception as e:
                        print(f"❌ [{self.user.name}] Extraction failed: {e}", flush=True)
                        
                        # ⚡ CHANGED: Every bot that hits an error will report it
                        await message.channel.send(f"❌ Extraction failed for **{self.user.name}**: {e}")

                # Run in background
                asyncio.create_task(leave_server())

            except Exception as e:
                # We leave this outer one filtered so if the link itself is completely broken, 
                # you only get 1 error message instead of 8 identical ones.
                if self.user.id % 8 == 0:
                    await message.channel.send(f"❌ Command Error: {e}")

        elif command == "autoreact":
            # Usage: !autoreact @user 💀
            if not message.mentions or len(parts) < 3:
                return await message.channel.send("❌ Usage: `!autoreact @user <emoji>`")
            
            target_id = message.mentions[0].id
            chosen_emoji = parts[-1]
            
            # Lock the target and emoji into the global brain
            AUTO_REACT_TARGETS[target_id] = chosen_emoji
            
            # ⚡ ALL bots respond confirming the lock-on!
            await message.channel.send(f"✅ FORB1D🔥 **{self.user.name}** Locked on! Auto-reacting {chosen_emoji} to <@{target_id}>")

        elif command == "unautoreact":
            # Usage: !unautoreact (clears all) OR !unautoreact @user (clears one)
            if message.mentions:
                # 1. PRECISION STRIKE CANCEL: Only stop for the mentioned user
                target_id = message.mentions[0].id
                
                if target_id in AUTO_REACT_TARGETS:
                    await message.channel.send(f"🛑 FORB1D🔥 **{self.user.name}** disengaged from <@{target_id}>")
                    await asyncio.sleep(0.5)
                    
                    if target_id in AUTO_REACT_TARGETS:
                        del AUTO_REACT_TARGETS[target_id]
                else:
                    await message.channel.send(f"⚠️ **{self.user.name}** was not targeting that user.")
                    
            else:
                # 2. TOTAL SYSTEM WIPE: No mentions, so clear EVERY target
                if AUTO_REACT_TARGETS:
                    await message.channel.send(f"🛑 FORB1D🔥 **{self.user.name}** wiped ALL auto-react targets!")
                    await asyncio.sleep(0.5)
                    
                    AUTO_REACT_TARGETS.clear()
                else:
                    await message.channel.send(f"⚠️ **{self.user.name}** has no active targets to clear.")

        elif command == "gcnc":
            # Usage: !gcnc <name> <delay>
            if len(parts) < 3:
                await asyncio.sleep(random.uniform(0.1, 0.5))
                return await message.channel.send(f"❌ **{self.user.name}** Usage: `!gcnc <name> <delay>` (e.g. !gcnc testing 1)")

            # 1. Security Check: Only run this if we are actually in a Group Chat
            if not isinstance(message.channel, discord.GroupChannel):
                await asyncio.sleep(random.uniform(0.1, 0.5))
                return await message.channel.send(f"❌ FORB1D🔥 Error: **{self.user.name}** - This command only works in Group Chats.")

            try:
                # Everything in the middle is the name, the very last part is the delay
                base_name = " ".join(parts[1:-1])
                delay = float(parts[-1])
                emojis = ["💀", "👿", "🔥", "👑", "⚡", "🔱", "💎", "☠️"]
                
                # YOUR GC NAME TEMPLATES: Cycles through these infinitely!
                # YOUR GC NAME TEMPLATES: Designed to be massive and hit the 100-character hard limit!
                templates = [
                    "█▓▒░ {chosen_emoji} 【 {user_text} 】 {chosen_emoji} ░▒▓█ ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
                    "▄▀▄▀▄▀ {chosen_emoji} {user_text} {chosen_emoji} ▀▄▀▄▀▄ ────────────────────────────────────────────────────────────",
                    "【 𝙁𝙊𝙍𝘽1𝘿🔥 】 ☠️ {user_text} ☠️ ▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█",
                    "𖣘 ━━━ {chosen_emoji} {user_text} {chosen_emoji} ━━━ 𖣘 ▇▆▅▄▃▂▂▃▄▅▆▇▇▆▅▄▃▂▂▃▄▅▆▇▇▆▅▄▃▂▂▃▄▅▆▇",
                    "🔥 ╳ ╳ ╳ {user_text} ╳ ╳ ╳ 🔥 ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒",
                    "𒐫𒐫𒐫 {chosen_emoji} ＦＯＲＢ１Ｄ ꧅ {user_text} ꧅ {chosen_emoji} 𒐫𒐫𒐫 ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿",
                    "𒈙𒈙𒈙 ░▒▓█ 【 {user_text} 】 █▓▒░ 𒈙𒈙𒈙 ▆▅▄▃▂▂▃▄▅▆▇██▇▆▅▄▃▂▂▃▄▅▆▇██▇",
                    "꧅꧅꧅ 👑 𝙁 𝙊 𝙍 𝘽 1 𝘿 👑   {user_text}   ꧅꧅꧅ ▓█▓█▓█▓█▓█▓█▓█▓█▓█▓█▓",
                    "T̷̒̓Ơ̷̼P̷̏̈ {chosen_emoji} ░ {user_text} ░ {chosen_emoji} T̷̒̓Ơ̷̼P̷̏̈ ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇",
                    "████████ {chosen_emoji}   {user_text}   {chosen_emoji} ████████ 𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫𒐫"
                    
                ]
                
                # 🟢 ENTERPRISE MATH: Auto-adjusts to the live swarm size!
                async def gcnc_loop():
                    # 🟢 ENTERPRISE MATH: Auto-adjusts to the live swarm size!
                    current_swarm_size = max(1, len(ACTIVE_SWARM))
                    
                    try:
                        # Bot finds its exact place in the live line-up (0, 1, 2, 3...)
                        my_math_id = ACTIVE_SWARM.index(self.user.id)
                    except ValueError:
                        my_math_id = 0
                        
                    stagger = my_math_id * delay
                    await asyncio.sleep(stagger)
                    
                    # Use the dynamic ID for templates so they never overlap
                    emoji_index = my_math_id % len(emojis)
                    template_index = my_math_id % len(templates)
                    
                    # 🟢 DYNAMIC CYCLE WAIT: Bot waits for the exact number of ALIVE bots to take their turn
                    cycle_wait = delay * float(current_swarm_size)
                    
                    while True:
                        try:
                            # Grab current emoji and cycle
                            chosen_emoji = emojis[emoji_index]
                            emoji_index = (emoji_index + 1) % len(emojis)
                            
                            # Grab current template and cycle
                            raw_template = templates[template_index]
                            template_index = (template_index + 1) % len(templates)
                            
                            # Swap the placeholders with the actual text and emoji
                            new_gc_name = raw_template.replace("{user_text}", base_name).replace("{chosen_emoji}", chosen_emoji)
                            
                            # Discord max limit safety check (GC names cap at 100 characters)
                            if len(new_gc_name) > 100:
                                new_gc_name = new_gc_name[:100]
                            
                            await message.channel.edit(name=new_gc_name)
                        #   print(f"🔄 [{self.user.name}] Flashed GC name: {new_gc_name}", flush=True)
                            
                            # Wait for the other 7 tokens to take their turns
                            await asyncio.sleep(cycle_wait) 
                            
                        except discord.HTTPException as e:
                            if e.status == 429:
                                # If Discord blocks it, wait the exact penalty time and immediately resume
                                wait = float(e.response.headers.get("Retry-After", 2.0))
                                await asyncio.sleep(wait)
                            else:
                                await asyncio.sleep(delay)

                # Fire it in the background
                task = asyncio.create_task(gcnc_loop(), name=f"gcnc_{message.channel.id}")
                
                # SEPARATED SYSTEM: We use a brand new dictionary so !unspam ignores it
                if message.channel.id not in gcnc_tasks:
                    gcnc_tasks[message.channel.id] = []
                gcnc_tasks[message.channel.id].append(task)
                
                # ⚡ JITTER: Every bot waits a random fraction of a second before confirming
                await asyncio.sleep(random.uniform(0.1, 0.6))
                await message.channel.send(f"✅ FORB1D🔥 **{self.user.name}** GC Name Flasher running at {delay}s delay: `{base_name}`")
            
            except ValueError:
                await asyncio.sleep(random.uniform(0.1, 0.5))
                await message.channel.send(f"❌ **{self.user.name}** Error: Delay must be a number (e.g. 1.5).")
            except Exception as e:
                await asyncio.sleep(random.uniform(0.1, 0.5))
                await message.channel.send(f"❌ **{self.user.name}** Command Error: {e}")

        # =========================================================
        # 🛑 ADD THIS HEADER SO IT DOESN'T AUTO-KILL ITSELF 🛑
        # =========================================================
        elif command == "ungcnc":

            # Direct Core Search for GC tasks
            killed = False
            for task in asyncio.all_tasks():
                if task.get_name() == f"gcnc_{message.channel.id}":
                    task.cancel()
                    killed = True
            
            # Jittered confirmation
            jitter = random.uniform(0.1, 0.6)
            await asyncio.sleep(jitter)
            
            if killed:
                await message.channel.send(f"🛑 FORB1D🔥 **{self.user.name}** terminated GC Name Flasher here.")
                print(f"🛑 [{self.user.name}] Stopped gcnc tasks in GC: {message.channel.id}", flush=True)
            else:
                await message.channel.send(f"⚠️ **{self.user.name}** found no active FORB1D🔥 GC Name Flasher running here.")


        elif command == "gcleave":
            # Usage: !gcleave (this GC) | !gcleave @bot (target bot) | !gcleave all (every GC)
            mode = "current"
            if len(parts) > 1:
                if parts[1].lower() == "all":
                    mode = "all"
                elif message.mentions:
                    mode = "targeted"
            
            # Base jitter so the 8 bots don't hit Discord's message endpoint at the exact same ms
            jitter = random.uniform(0.1, 0.6)

            if mode == "targeted":
                # If this specific bot was NOT mentioned, it ignores the command completely
                if self.user not in message.mentions:
                    return
                
                if message.channel.type != discord.ChannelType.group:
                    await asyncio.sleep(jitter)
                    return await message.channel.send(f"❌ **{self.user.name}** Error: This is not a Group Chat.")
                
                # It MUST send the message BEFORE leaving, otherwise Discord blocks the message!
                await asyncio.sleep(jitter)
                await message.channel.send(f"✅ FORB1D🔥 **{self.user.name}** is extracting from this GC.")
                
                await asyncio.sleep(0.5) # Wait half a second to ensure the message sent
                await message.channel.leave()
                print(f"✅ [{self.user.name}] Left GC: {message.channel.id}", flush=True)

            elif mode == "current":
                # Standard !gcleave (all bots leave this specific GC)
                if message.channel.type != discord.ChannelType.group:
                    await asyncio.sleep(jitter)
                    return await message.channel.send(f"❌ **{self.user.name}** Error: This is not a Group Chat.")
                
                await asyncio.sleep(jitter)
                await message.channel.send(f"✅ FORB1D🔥 **{self.user.name}** is extracting from this GC.")
                
                await asyncio.sleep(0.5)
                await message.channel.leave()
                print(f"✅ [{self.user.name}] Left GC: {message.channel.id}", flush=True)

            elif mode == "all":
                # Get a list of every single GC the bot is currently inside
                gcs_to_leave = [ch for ch in self.private_channels if isinstance(ch, discord.GroupChannel)]
                
                # 200 IQ PLAY: If we are currently standing in a GC, we must leave it LAST.
                # Otherwise, the bot will lose access to the channel and can't send the final message!
                current_is_gc = isinstance(message.channel, discord.GroupChannel)
                if current_is_gc and message.channel in gcs_to_leave:
                    gcs_to_leave.remove(message.channel)
                
                leave_count = 0
                for gc in gcs_to_leave:
                    try:
                        await gc.leave()
                        leave_count += 1
                        # Stealth delay between leaves so Discord doesn't flag the account
                        await asyncio.sleep(random.uniform(0.8, 2.0))
                    except Exception as e:
                        print(f"❌ [{self.user.name}] Failed to leave GC {gc.id}: {e}", flush=True)
                
                # Now that the background wipe is done, ALL bots report their total count
                await asyncio.sleep(jitter)
                total_left = leave_count + (1 if current_is_gc else 0)
                # Creates a perfect 1-second line-up based on the bot's ID
                await asyncio.sleep(self.user.id % 8 * 1.0)
                await message.channel.send(f"✅ FORB1D🔥 **{self.user.name}** successfully extracted from {total_left} GCs.")
                print(f"✅ [{self.user.name}] Mass GC extraction complete.", flush=True)
                
                # FINALLY: Leave the current GC as the absolute last step
                if current_is_gc:
                    await asyncio.sleep(0.5)
                    await asyncio.sleep(1.0)
                    await message.channel.leave()

        elif command == "stream":
            # Usage: !stream <Text> (Turns it on) | !stream stop (Turns it off)
            if len(parts) < 2:
                await asyncio.sleep(self.user.id % 8 * 1.0)
                return await message.channel.send(f"❌ **{self.user.name}** Usage: `!stream <text>` or `!stream stop`")

            stream_text = " ".join(parts[1:])
            
            # STAGGER MATH: So all 8 bots don't hit the Discord presence API at the exact same millisecond
            stagger = (self.user.id % 8 * 1.0) + random.uniform(0.1, 0.5)
            await asyncio.sleep(stagger)

            try:
                if stream_text.lower() == "stop":
                    # Clear the rich presence (turns off the streaming status)
                    await self.change_presence(activity=None)
                    
                    await asyncio.sleep(0.5)
                    await message.channel.send(f"🛑 FORB1D🔥 **{self.user.name}** stopped streaming.")
                else:
                    # Discord requires a Twitch or YT link for the purple stream icon to appear
                    twitch_url = "https://www.twitch.tv/forb1d"
                    
                    # Lock in the Streaming status
                    activity = discord.Streaming(name=stream_text, url=twitch_url)
                    await self.change_presence(activity=activity)
                    
                    await asyncio.sleep(0.5)
                    await message.channel.send(f"🟣 FORB1D🔥 **{self.user.name}** is now streaming: `{stream_text}`")
                    
            except Exception as e:
                await message.channel.send(f"❌ **{self.user.name}** Failed to update status: {e}")

        elif command == "presence":
            # Usage: !presence <play/listen/watch> <text>
            if len(parts) < 3:
                await asyncio.sleep(self.user.id % 8 * 1.0)
                return await message.channel.send(f"❌ **{self.user.name}** Usage: `!presence <play/listen/watch> <text>`")

            activity_type = parts[1].lower()
            presence_text = " ".join(parts[2:])

            # STAGGER MATH: Perfect 1-second intervals so the API doesn't flag the sudden mass-update
            stagger = (self.user.id % 8 * 1.0) + random.uniform(0.1, 0.5)
            await asyncio.sleep(stagger)

            try:
                if activity_type == "play":
                    act = discord.Game(name=presence_text)
                    msg = f"🎮 FORB1D🔥 **{self.user.name}** is playing: `{presence_text}`"
                elif activity_type == "listen":
                    act = discord.Activity(type=discord.ActivityType.listening, name=presence_text)
                    msg = f"🎧 FORB1D🔥 **{self.user.name}** is listening to: `{presence_text}`"
                elif activity_type == "watch":
                    act = discord.Activity(type=discord.ActivityType.watching, name=presence_text)
                    msg = f"📺 FORB1D🔥 **{self.user.name}** is watching: `{presence_text}`"
                else:
                    return await message.channel.send(f"❌ **{self.user.name}** Invalid mode! Use play, listen, or watch.")

                # Lock in the new status
                await self.change_presence(activity=act)
                
                await asyncio.sleep(0.5)
                await message.channel.send(msg)

            except Exception as e:
                await message.channel.send(f"❌ **{self.user.name}** Failed to update presence: {e}")

        elif command == "help":
            # STAGGER MATH: All 8 bots respond, staggered by 1 second so Discord doesn't block them!
            stagger = (self.user.id % 8 * 1.0) + random.uniform(0.1, 0.4)
            await asyncio.sleep(stagger)
            
            # Wrapped in ```yaml to give it that colored, luxury terminal aesthetic in Discord
            help_panel = f"""```yaml
🔥 FORB1D OPS | MASTER CONTROL 🔥
=====================================
"Dominate the network. Engineered by FORB1D🔥"

[ 📡 INFILTRATION & EXTRACTION ]
> ^serverjoin <link>    (Swarm joins)
> ^serverjoin @bot      (Precision join)
> ^serverleave <link>   (Swarm leaves)
> ^serverleave @bot     (Precision leave)
> ^ping                 (Live latency)
> ^unping               (Stop live latency)

[ 👥 GROUP CHAT OPS ]
> ^gcnc <name> <delay>  (GC Name Flasher)
> ^ungcnc               (Stop flasher here)
> ^gcleave              (Swarm leaves this GC)
> ^gcleave all          (Swarm leaves ALL GCs)
> ^gcleave @bot         (Precision GC leave)

[ 🎯 TARGETING & SPAM OPS ]
> ^autoreact @user 💀   (Lock-on reactions)
> ^unautoreact          (Wipe all targets)
> ^unautoreact @user    (Unlock specific user)
> ^rs <text> <delay>    (Roast Chat Spam)
> ^cs <text> <delay>    (Custom Spam)
> ^unspam               (Stop Chat Spam)

[ 🎭 FLEX & PRESENCE OPS ]
> ^stream <text>        (Purple stream status)
> ^stream stop          (Wipe stream status)
> ^presence <mode> <msg>(play/listen/watch)

=====================================
⚡ Powered by FORB1D🔥 Network ⚡
[ {self.user.name} - System Online ]
```"""
            try:
                await message.channel.send(help_panel)
            except Exception as e:
                print(f"❌ [{self.user.name}] Help Panel failed: {e}", flush=True)

       
    async def ram_cleaner_loop(self):
        import gc
        await self.wait_until_ready()
        if self.user.id % 8 != 0:
            return
        while not self.is_closed():
            try:
                await asyncio.sleep(600)
                collected = gc.collect()
                for channel_id in list(spam_tasks.keys()):
                    if channel_id in spam_tasks and not spam_tasks[channel_id]:
                        del spam_tasks[channel_id]
                for channel_id in list(gcnc_tasks.keys()):
                    if channel_id in gcnc_tasks and not gcnc_tasks[channel_id]:
                        del gcnc_tasks[channel_id]
                print(f"🧹 [Memory Engine] Deep RAM Purge complete. Freed {collected} dead objects.", flush=True)
            except Exception as e:
                print(f"⚠️ [Memory Engine] Purge failed: {e}", flush=True)

# 🛑 PASTE IT RIGHT HERE AT THE ABSOLUTE BOTTOM OF THE CLASS 🛑
    async def close(self):
        if self.raw_session:
            await self.raw_session.close()
        await super().close()
                
# 4. Master Engine Initialization
async def main():
    raw_tokens = os.environ.get('BOT_TOKENS')
    if not raw_tokens:
        print("❌ ERROR: No BOT_TOKENS found in Render Environment Variables!", flush=True)
        return

    token_list = [t.strip() for t in raw_tokens.split(',') if t.strip()]
    clients = []

    print(f"⚡ Initializing multi-token array with {len(token_list)} targets...", flush=True)

    # Create a shielded login function so dead tokens don't crash the good ones
    async def safe_start(client, token):
        try:
            await client.start(token)
        except Exception as e:
            print(f"💀 DEAD TOKEN SKIPPED [{token[:10]}...]: {e}", flush=True)

    # Build client instances for every token WITH THE CLOUDFLARE BYPASS
    for i, token in enumerate(token_list):
        client = ForbidToken()
        clients.append(safe_start(client, token))
        
        # 🟢 THE GOD-TIER STAGGER: Spaces out logins by 15-20 seconds per token
        # This completely cloaks your Render IP from Discord's security!
        if i < len(token_list) - 1:
            boot_delay = 15.0 + random.uniform(1.0, 5.0)
            print(f"⏳ [System] Holding next token for {boot_delay:.1f}s to cloak IP footprint...", flush=True)
            await asyncio.sleep(boot_delay)

    # Fire all connections concurrently (they are already mathematically spaced out now!)
    print("🚀 Firing connections concurrently...", flush=True)
    await asyncio.gather(*clients)
    
if __name__ == "__main__":
    # 1. Start the web server in the background ONLY after everything is loaded
    keep_alive()
    
    # 2. Ignite the botnet
    asyncio.run(main())
