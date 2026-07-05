import discord, json, asyncio, random, sys
import re

# Load config
with open('config.json', 'r') as f: config = json.load(f)

# Use the token passed from the launcher
TOKEN = sys.argv[1] 
PREFIX = config['prefix']
AUTHORIZED_USERS = config.get('authorized_users', [])
MAIN_OWNER = 1457960499798081549 

client = discord.Client()
active_monitors = {}
spam_tasks = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name} | System Ready.')


@client.event
async def on_message(message):
    # 1. Bot ignores its own messages to prevent infinite loops
    if message.author == client.user:
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
                my_math_id = client.user.id % 8
                await asyncio.sleep((my_math_id * 0.15) + random.uniform(0.01, 0.05))
                
                await message.add_reaction(emoji_to_react)
                print(f"⚡ [{client.user.name}] Auto-reacted on {message.author.name}")
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
    command = parts[0].lower()

  

    if command == "ping":
        if not isinstance(message.channel, discord.DMChannel):
            try: await message.delete()
            except: pass

        msg = await message.channel.send("`[!] FORBID // INITIALIZING...`")
        active_monitors[message.channel.id] = msg
        
        try:
            while active_monitors.get(message.channel.id) == msg:
                latency = round(client.latency * 1000)
                status_emoji = "🟢" if latency < 50 else "🟡" if latency < 150 else "🔴"
                status_text = "OPTIMAL" if latency < 50 else "STABLE" if latency < 150 else "LAGGY"
                
                await msg.edit(content=
                    f"**FORBID // SYSTEM PANEL**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚡ **GATEWAY:** `{latency}ms`\n"
                    f"{status_emoji} **STATUS:** `{status_text}`\n"
                    f"🛠️ **INTERFACE:** `ACTIVE`\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"Use `{PREFIX}unping` to terminate."
                )
                await asyncio.sleep(random.uniform(4.5, 5.5))
        except: 
            if message.channel.id in active_monitors: del active_monitors[message.channel.id]

    elif command == "unping":
        if message.channel.id in active_monitors:
            msg = active_monitors.pop(message.channel.id)
            await msg.edit(content="`[!] FORBID // SHUTTING DOWN...`")
            await asyncio.sleep(1.5)
            await msg.delete()

    
    elif command == "rs":
        # Usage: !rs <text> <delay>
        if len(parts) < 3:
            return await message.channel.send("❌ Usage: `!rs <text> <delay>`")
        
        try:
            user_text = " ".join(parts[1:-1])
            delay = float(parts[-1])
            
            emojis = ["🔱", "👑", "🔥", "⚡", "💀", "💎", "⚔️"]
            
            # YOUR TEMPLATES LIST: Add as many as you want here!
            # Use {user_text} and {chosen_emoji} wherever you want them to appear.
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
                # ADVANCED MATH: Perfect Gatling gun stagger
                my_math_id = client.user.id % 8 
                perfect_stagger = (delay / 8.0) * my_math_id
                
                # Assign a unique starting emoji AND a unique starting template based on account ID
                emoji_index = client.user.id % len(emojis)
                template_index = client.user.id % len(templates)
                
                await asyncio.sleep(perfect_stagger)

                while True:
                    try:
                        # Grab current emoji and cycle to next
                        chosen_emoji = emojis[emoji_index]
                        emoji_index = (emoji_index + 1) % len(emojis)
                        
                        # Grab current template and cycle to next
                        raw_template = templates[template_index]
                        template_index = (template_index + 1) % len(templates)
                        
                        # Swap the placeholders with your actual text and emoji
                        base_text = raw_template.replace("{user_text}", user_text).replace("{chosen_emoji}", chosen_emoji)
                        
                        # Invisible space treatment
                        spaced_text = base_text.replace(" ", " \u200B")
                        
                        # Math: Calculate fit for Discord's limit
                        line_length = len(spaced_text) + 2
                        multiplier = 1950 // line_length
                        if multiplier < 1: multiplier = 1
                        
                        # Combine
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
            if message.channel.id not in spam_tasks:
                spam_tasks[message.channel.id] = []
            spam_tasks[message.channel.id].append(task)
            
            if client.user.id % 8 == 0 or client.user.id % 8 == 1: 
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
                # This guarantees no race conditions and perfectly spaces all tokens.
                my_math_id = client.user.id % 8 
                perfect_stagger = (delay / 8.0) * my_math_id
                
                # Start at a unique color based on the account ID 
                color_index = client.user.id % len(hearts)
                
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
                        
                        # Wait the full delay (safe from IP ban), while maintaining the Gatling gun weave
                        await asyncio.sleep(delay)
                    
                    except discord.HTTPException as e:
                        if e.status == 429:
                            wait = float(e.response.headers.get("Retry-After", 1.0))
                            await asyncio.sleep(wait)
                        else:
                            await asyncio.sleep(0.3)
            
            task = asyncio.create_task(custom_loop())
            if message.channel.id not in spam_tasks:
                spam_tasks[message.channel.id] = []
            spam_tasks[message.channel.id].append(task)
            
            # Prevent 8 identical confirmations by only letting one specific ID send it
            if client.user.id % 8 == 0 or client.user.id % 8 == 1: 
                await message.channel.send(f"✅Custom-Spam started: '{user_text}'")
            
        except Exception as e:
            await message.channel.send(f"❌ Error: {e}")

    elif command == "unspam":
        # Check if the channel has any tasks running
        if message.channel.id in spam_tasks:
            # Cancel every task in this channel's list
            for task in spam_tasks[message.channel.id]:
                task.cancel()
            
            # Remove the channel from the dictionary so it doesn't try to cancel again
            del spam_tasks[message.channel.id]
            await message.channel.send("✅ All spam processes in this channel terminated.")
        else:
            await message.channel.send("❌ No active spam in this channel.")

    elif command == "join":
        # Usage: !join <link> OR !join @bot1 @bot2 <link>
        if len(parts) < 2:
            return await message.channel.send("❌ Usage: `!join <link>` or `!join @bot <link>`")
        
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
                if client.user not in message.mentions:
                    return
                
                # Since it's targeted (fewer bots), we use a very fast, short stagger
                stagger = random.uniform(0.2, 1.0)
                is_targeted = True
            else:
                # No mentions = ALL tokens join. Use the math Gatling stagger to prevent Anti-Raid
                my_math_id = client.user.id % 8 
                stagger = (my_math_id * 1.5) + random.uniform(0.5, 1.5)
                is_targeted = False
            
            print(f"[{client.user.name}] Engaging infiltration protocol. Stagger: {stagger:.2f}s...")
            
            async def join_server():
                await asyncio.sleep(stagger)
                try:
                    invite = await client.fetch_invite(invite_code)
                    await invite.accept()
                    print(f"✅ [{client.user.name}] Successfully joined {invite_code}")
                    
                    # If targeted, the bot speaks for itself. 
                    # If it's the full wave, only Token 0/1 speak to keep chat clean.
                    if is_targeted or (client.user.id % 8 == 0 or client.user.id % 8 == 1):
                        await message.channel.send(f"✅ FORB1D🔥 Network infiltrated by **{client.user.name}**: `{invite_code}`")
                        
                except Exception as e:
                    print(f"❌ [{client.user.name}] Join failed: {e}")
                    if is_targeted or client.user.id % 8 == 0:
                        await message.channel.send(f"❌ Breach failed for **{client.user.name}**: {e}")

            # Run in background
            asyncio.create_task(join_server())

        except Exception as e:
            if client.user.id % 8 == 0:
                await message.channel.send(f"❌ Command Error: {e}")

    elif command == "leave":
        # Usage: !leave <link> OR !leave @bot <link>
        if len(parts) < 2:
            return await message.channel.send("❌ Usage: `!leave <link>` or `!leave @bot <link>`")
        
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
                if client.user not in message.mentions:
                    return
                # Fast extraction for targeted bots
                stagger = random.uniform(0.2, 1.0)
                is_targeted = True
            else:
                # Math stagger for full wave extraction to avoid API spam flags
                my_math_id = client.user.id % 8 
                stagger = (my_math_id * 1.0) + random.uniform(0.2, 1.0)
                is_targeted = False
            
            print(f"[{client.user.name}] Engaging extraction protocol. Stagger: {stagger:.2f}s...")
            
            async def leave_server():
                await asyncio.sleep(stagger)
                try:
                    # Fetch the invite to identify WHICH server it belongs to
                    invite = await client.fetch_invite(invite_code)
                    guild_id = invite.guild.id
                    
                    # Check if the bot is actually inside this specific server
                    guild_to_leave = client.get_guild(guild_id)
                    
                    if guild_to_leave:
                        await guild_to_leave.leave()
                        print(f"✅ [{client.user.name}] Successfully extracted from {guild_to_leave.name}")
                        
                        # Clean chat output
                        if is_targeted or (client.user.id % 8 == 0 or client.user.id % 8 == 1):
                            await message.channel.send(f"✅ FORB1D🔥 **{client.user.name}** extracted from: `{guild_to_leave.name}`")
                    else:
                        print(f"⚠️ [{client.user.name}] Aborted: Not in network {invite_code}")
                        if is_targeted or client.user.id % 8 == 0:
                            await message.channel.send(f"⚠️ **{client.user.name}** is not in that network.")
                            
                except Exception as e:
                    print(f"❌ [{client.user.name}] Extraction failed: {e}")
                    if is_targeted or client.user.id % 8 == 0:
                        await message.channel.send(f"❌ Extraction failed for **{client.user.name}**: {e}")

            # Run in background
            asyncio.create_task(leave_server())

        except Exception as e:
            if client.user.id % 8 == 0:
                await message.channel.send(f"❌ Command Error: {e}")

    elif command == "autoreact":
        # Usage: !autoreact @user 💀 (Add emoji to start, send without emoji to stop)
        if not message.mentions:
            return await message.channel.send("❌ Usage: `!autoreact @user <emoji>`")
        
        target_id = message.mentions[0].id
        
        # If you didn't provide an emoji, we assume you want to STOP auto-reacting
        if len(parts) < 3:
            if target_id in AUTO_REACT_TARGETS:
                del AUTO_REACT_TARGETS[target_id]
                if client.user.id % 8 == 0:
                    await message.channel.send(f"🛑 FORB1D🔥 Auto-React disabled for <@{target_id}>")
            return
            
        # If you provided an emoji, lock it in
        chosen_emoji = parts[-1]
        AUTO_REACT_TARGETS[target_id] = chosen_emoji
        
        if client.user.id % 8 == 0:
            await message.channel.send(f"✅ FORB1D🔥 Locked on! Auto-reacting {chosen_emoji} to all messages from <@{target_id}>")

    elif command == "gcnc":
        # Usage: !gcnc <name> <delay>
        if len(parts) < 3:
            if client.user.id % 8 == 0:
                return await message.channel.send("❌ Usage: `!gcnc <name> <delay>` (e.g. !gcnc testing 1)")
            return

        # 1. Security Check: Only run this if we are actually in a Group Chat
        if not isinstance(message.channel, discord.GroupChannel):
            if client.user.id % 8 == 0:
                return await message.channel.send("❌ FORB1D🔥 Error: This command only works in Group Chats.")
            return

        try:
            # Everything in the middle is the name, the very last part is the delay
            base_name = " ".join(parts[1:-1])
            delay = float(parts[-1])
            emojis = ["💀", "👿", "🔥", "👑", "⚡", "🔱", "💎", "☠️"]
            
            async def gcnc_loop():
                # ADVANCED MATH: Use your exact delay to stagger the start
                my_math_id = client.user.id % 8 
                stagger = my_math_id * delay
                await asyncio.sleep(stagger)
                
                emoji_index = client.user.id % len(emojis)
                
                # To keep the exact 1-second pace, each bot waits 8x the delay between its own turns
                cycle_wait = delay * 8.0
                
                while True:
                    try:
                        chosen_emoji = emojis[emoji_index]
                        emoji_index = (emoji_index + 1) % len(emojis)
                        
                        new_gc_name = f"{chosen_emoji} {base_name} {chosen_emoji}"
                        
                        await message.channel.edit(name=new_gc_name)
                        print(f"🔄 [{client.user.name}] Flashed GC name: {new_gc_name}")
                        
                        # Wait for the other 7 tokens to take their 1-second turns
                        await asyncio.sleep(cycle_wait) 
                        
                    except discord.HTTPException as e:
                        if e.status == 429:
                            # If Discord blocks it, wait the exact penalty time and immediately resume
                            wait = float(e.response.headers.get("Retry-After", 2.0))
                            await asyncio.sleep(wait)
                        else:
                            await asyncio.sleep(delay)

            # Fire it in the background
            task = asyncio.create_task(gcnc_loop())
            if message.channel.id not in spam_tasks:
                spam_tasks[message.channel.id] = []
            spam_tasks[message.channel.id].append(task)
            
            # Only Token 0 confirms it
            if client.user.id % 8 == 0:
                await message.channel.send(f"✅ FORB1D🔥 GC Name Flasher running at {delay}s delay: `{base_name}`")

        except Exception as e:
            if client.user.id % 8 == 0:
                await message.channel.send(f"❌ Error: {e}")

    elif command == "stopgcnc":
        # Usage: !stopgcnc (Kills ONLY the active name flasher loops in this specific GC)
        global gcnc_tasks
        if "gcnc_tasks" not in globals():
            gcnc_tasks = {}
            
        # Check if there is an active name flasher running in this specific chat
        if message.channel.id in gcnc_tasks and gcnc_tasks[message.channel.id]:
            
            # Extract and cancel only the name flasher tasks
            for task in gcnc_tasks[message.channel.id]:
                task.cancel() # Kills the loop instantly
                
            # Clear the tracking list for this channel
            gcnc_tasks[message.channel.id] = []
            
            if client.user.id % 8 == 0:
                await message.channel.send("🛑 FORB1D🔥 GC Name Flasher terminated in this chat.")
                print(f"🛑 [{client.user.name}] Stopped gcnc tasks in GC: {message.channel.id}")
        else:
            if client.user.id % 8 == 0:
                await message.channel.send("⚠️ No active FORB1D🔥 GC Name Flasher running here.")


client.run(TOKEN)