import subprocess
import time
import os
from keep_alive import keep_alive

# 1. Start the fake webserver to trick Render into 24/7 uptime
keep_alive()

print("⚡ Starting FORB1D master sequence...")

# 2. Pull tokens securely from Render's Environment Variables
raw_tokens = os.environ.get('BOT_TOKENS')

if not raw_tokens:
    print("❌ ERROR: No BOT_TOKENS found in Render Environment Variables!")
    while True: time.sleep(3600) # Keep alive so we can read the error in logs

# Split the tokens using a comma
token_list = raw_tokens.split(',')

# 3. Launch the tokens
for token in token_list:
    token = token.strip() # Cleans up any accidental spaces
    if token:
        print(f"🚀 Launching process for: {token[:10]}...")
        subprocess.Popen(['python', '2tk.py', token])
        time.sleep(2) # Stagger logins

print("✅ All tokens launched successfully. Master script holding operation...")

# 4. Prevent the launcher from closing
while True:
    time.sleep(3600)