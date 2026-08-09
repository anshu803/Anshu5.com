# ============================================================
#  █████╗ ███╗   ██╗███████╗██╗  ██╗██╗   ██╗
# ██╔══██╗████╗  ██║██╔════╝██║  ██║╚██╗ ██╔╝
# ███████║██╔██╗ ██║███████╗███████║ ╚████╔╝
# ██╔══██║██║╚██╗██║╚════██║██╔══██║  ╚██╔╝
# ██║  ██║██║ ╚████║███████║██║  ██║   ██║
# ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝   ╚═╝
# ☠️ ANSHU.COD.X — FINAL PERFECT BOT ☠️
# ============================================================

import sqlite3
import time
import re
import asyncio
from datetime import datetime
from telethon import TelegramClient, events, Button

# ============================================================
# ⚙️ CONFIG — SIRF YAHI CHANGE KARNA HAI
# ============================================================

API_ID = 31938867
API_HASH = '5511e68d4cb23a68c7b882aea8ff7b87'
BOT_TOKEN = '8819065525:AAEg1ABpwGqmPintsVcW6eXyPDAis97zBfo'

# ✅ APNI TELEGRAM USER ID ( @userinfobot se lo )
ADMIN_ID = 8732093502

# ✅ UPI ID ( jispe payment aani chahiye )
UPI_ID = '8303721228@ibl'

# ✅ PRICE PER CODE
PRICE_PER_CODE = 50

# ============================================================
# 📦 DATABASE
# ============================================================

def init_db():
    conn = sqlite3.connect('anshu_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS requests
                 (req_id TEXT PRIMARY KEY,
                  user_id INTEGER,
                  username TEXT,
                  prompt TEXT,
                  amount REAL,
                  status TEXT,
                  payment_txn TEXT,
                  channel_msg_id INTEGER,
                  created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bot_config
                 (key TEXT PRIMARY KEY,
                  value TEXT)''')
    conn.commit()
    conn.close()

def get_channel_id():
    conn = sqlite3.connect('anshu_bot.db')
    c = conn.cursor()
    c.execute('SELECT value FROM bot_config WHERE key = "channel_id"')
    row = c.fetchone()
    conn.close()
    return int(row[0]) if row else None

def set_channel_id(channel_id):
    conn = sqlite3.connect('anshu_bot.db')
    c = conn.cursor()
    c.execute('REPLACE INTO bot_config (key, value) VALUES ("channel_id", ?)', (str(channel_id),))
    conn.commit()
    conn.close()

# ============================================================
# 🤖 BOT INIT
# ============================================================

client = TelegramClient('anshu_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ============================================================
# 🟢 START COMMAND
# ============================================================

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.respond(
        '╔══════════════════════════════════════╗\n'
        '█▓▒░  ☠️ ANSHU.COD.X  ☠️  ░▒▓█\n'
        '╚══════════════════════════════════════╝\n\n'
        '▣ **SYSTEM:** `ONLINE`\n'
        '▣ **MODE:** `UNFILTERED`\n'
        '▣ **PRICE:** `₹{}`\n\n'
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        '💀 **HOW IT WORKS:**\n'
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n'
        '🔥 `/request <kuch bhi code maango>`\n'
        '🔥 UPI ID TURANT AAYEGA\n'
        '🔥 PAY → `/paid REQ_xxx TXN123`\n'
        '🔥 SCREENSHOT + DATA CHANNEL MEIN\n'
        '🔥 ADMIN `flASH lo CODE` LIKHEGA\n'
        '🔥 BOT USER KO CODE DE DEGA\n\n'
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        '📌 **COMMANDS:**\n'
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        '⚡ `/request <code maango>`\n'
        '⚡ `/status <req_id>`\n'
        '⚡ `/history`\n'
        '⚡ `/setchannel` — Set channel (admin only)'.format(PRICE_PER_CODE)
    )

# ============================================================
# 🔧 SET CHANNEL — ADMIN ONLY
# ============================================================

@client.on(events.NewMessage(pattern='/setchannel'))
async def set_channel_handler(event):
    if event.sender_id != ADMIN_ID:
        await event.respond('☠️ **UNAUTHORIZED** ☠️')
        return
    await event.respond(
        '📌 **CHANNEL SETUP**\n\n'
        '1️⃣ Bot ko channel mein **admin** banao\n'
        '2️⃣ Channel mein `/getid` bhejo\n'
        '3️⃣ ID copy karo aur yahan paste karo:\n'
        '`/setchannel -1001234567890`'
    )

@client.on(events.NewMessage(pattern='/setchannel (-?\\d+)'))
async def set_channel_id_handler(event):
    if event.sender_id != ADMIN_ID:
        await event.respond('☠️ **UNAUTHORIZED** ☠️')
        return
    channel_id = int(event.pattern_match.group(1))
    set_channel_id(channel_id)
    try:
        await client.send_message(channel_id, '✅ **CHANNEL SET** ✅\nBot is ready!')
        await event.respond(f'✅ Channel set to: `{channel_id}`')
    except Exception as e:
        await event.respond(f'❌ Bot channel mein admin nahi hai. Error: {str(e)}')

# ============================================================
# 📝 REQUEST — TURANT UPI ID
# ============================================================

@client.on(events.NewMessage(pattern='/request (.*)'))
async def request_handler(event):
    try:
        channel_id = get_channel_id()
        if not channel_id:
            await event.respond('❌ Channel not set. Contact admin.')
            return

        user_id = event.sender_id
        prompt = event.pattern_match.group(1).strip()
        if not prompt:
            await event.respond('💀 Kuch likh bhai... `/request Python mein code do`')
            return

        user = await event.get_sender()
        username = user.username or f"user_{user_id}"
        req_id = f"REQ_{int(time.time())}_{user_id}"

        conn = sqlite3.connect('anshu_bot.db')
        c = conn.cursor()
        c.execute('''INSERT INTO requests
                     (req_id, user_id, username, prompt, amount, status, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (req_id, user_id, username, prompt, PRICE_PER_CODE,
                   'payment_pending', datetime.now().isoformat()))
        conn.commit()
        conn.close()

        # Channel post
        await client.send_message(
            channel_id,
            f'╔══════════════════════════════════════╗\n'
            f'█▓▒░  ☠️ ANSHU.COD.X — NEW REQUEST  ☠️  ░▒▓█\n'
            f'╚══════════════════════════════════════╝\n\n'
            f'◈ **REQUEST ID:** `{req_id}`\n'
            f'◈ **USER:** @{username} (`{user_id}`)\n'
            f'◈ **TASK:** {prompt}\n'
            f'◈ **PRICE:** ₹{PRICE_PER_CODE}\n'
            f'◈ **STATUS:** ⏳ AWAITING PAYMENT'
        )

        await event.respond(
            f'╔══════════════════════════════════════╗\n'
            f'█▓▒░  ☠️ ANSHU.COD.X  ☠️  ░▒▓█\n'
            f'╚══════════════════════════════════════╝\n\n'
            f'📌 **ID:** `{req_id}`\n'
            f'📝 **TASK:** {prompt}\n\n'
            f'💰 **Amount:** ₹{PRICE_PER_CODE}\n'
            f'🏦 **UPI ID:** `{UPI_ID}`\n\n'
            f'`/paid {req_id} <transaction_id>`'
        )

        await client.send_message(ADMIN_ID, f'☠️ NEW REQUEST\nID: {req_id}\nUser: @{username}')

    except Exception as e:
        await event.respond(f'💀 ERROR: {str(e)}')

# ============================================================
# 💳 PAYMENT CONFIRM
# ============================================================

@client.on(events.NewMessage(pattern='/paid (.*) (.*)'))
async def paid_handler(event):
    try:
        channel_id = get_channel_id()
        user_id = event.sender_id
        req_id = event.pattern_match.group(1).strip()
        txn_id = event.pattern_match.group(2).strip()

        conn = sqlite3.connect('anshu_bot.db')
        c = conn.cursor()
        c.execute('''SELECT username, prompt FROM requests
                     WHERE req_id = ? AND user_id = ? AND status = 'payment_pending' ''',
                  (req_id, user_id))
        result = c.fetchone()
        if not result:
            await event.respond('❌ Invalid request.')
            conn.close()
            return

        username, prompt = result
        c.execute('''UPDATE requests SET status = 'paid', payment_txn = ?
                     WHERE req_id = ?''', (txn_id, req_id))
        conn.commit()
        conn.close()

        await client.send_message(
            channel_id,
            f'╔══════════════════════════════════════╗\n'
            f'█▓▒░  💳 PAYMENT RECEIVED  💳  ░▒▓█\n'
            f'╚══════════════════════════════════════╝\n\n'
            f'📌 **REQUEST ID:** `{req_id}`\n'
            f'👤 **USER:** @{username}\n'
            f'📝 **TASK:** {prompt}\n'
            f'💳 **TXN ID:** `{txn_id}`\n'
            f'💰 **AMOUNT:** ₹{PRICE_PER_CODE}\n\n'
            f'⏳ **ADMIN: 10-20 MIN WAIT**\n'
            f'⬇️ **CODE LIKHO AUR "flASH lo" LIKHO**'
        )

        await event.respond(
            '✅ **PAYMENT CONFIRMED**\n'
            '⏳ **PLEASE WAIT 10-20 MINUTES**\n'
            'Admin code likh raha hai...'
        )

        await client.send_message(ADMIN_ID, f'💳 PAYMENT RECEIVED\nID: {req_id}\nTXN: {txn_id}')

    except Exception as e:
        await event.respond(f'💀 ERROR: {str(e)}')

# ============================================================
# 📨 CHANNEL REPLY — "flASH lo" TRIGGER
# ============================================================

@client.on(events.NewMessage)
async def channel_reply_handler(event):
    try:
        channel_id = get_channel_id()
        if not channel_id or event.chat_id != channel_id:
            return
        if not event.is_reply:
            return

        replied = await event.get_reply_message()
        conn = sqlite3.connect('anshu_bot.db')
        c = conn.cursor()
        c.execute('SELECT req_id, user_id, status FROM requests WHERE channel_msg_id = ?',
                  (replied.id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return

        req_id, user_id, status = row
        if status == 'delivered':
            await event.reply('⚠️ Already delivered.')
            conn.close()
            return
        if status != 'paid':
            await event.reply('⏳ Payment pending.')
            conn.close()
            return

        text = event.text.strip()
        if 'flASH lo' not in text.lower():
            await event.reply('⏳ Code send karne ke liye `flASH lo CODE` likho.')
            conn.close()
            return

        code = text.split('flASH lo', 1)[1].strip()
        if '```' in code:
            m = re.search(r'```(?:\w+)?\n(.*?)```', code, re.DOTALL)
            if m:
                code = m.group(1).strip()

        if not code:
            await event.reply('⚠️ Code nahi mila.')
            conn.close()
            return

        c.execute('UPDATE requests SET status = "delivered" WHERE req_id = ?', (req_id,))
        conn.commit()
        c.execute('SELECT prompt FROM requests WHERE req_id = ?', (req_id,))
        prompt = c.fetchone()[0]
        conn.close()

        await client.send_message(
            user_id,
            f'✅ **CODE DELIVERED**\n\n'
            f'📌 **ID:** `{req_id}`\n'
            f'📝 **TASK:** {prompt}\n\n'
            f'```\n{code}\n```'
        )

        await event.reply(f'✅ **CODE DELIVERED** to user `{user_id}`')

    except Exception as e:
        await event.reply(f'💀 ERROR: {str(e)}')

# ============================================================
# 📌 GET ID
# ============================================================

@client.on(events.NewMessage(pattern='/getid'))
async def get_id_handler(event):
    await event.respond(f'☠️ CHAT ID: `{event.chat_id}`')

# ============================================================
# 📊 STATUS
# ============================================================

@client.on(events.NewMessage(pattern='/status (.*)'))
async def status_handler(event):
    req_id = event.pattern_match.group(1).strip()
    user_id = event.sender_id
    conn = sqlite3.connect('anshu_bot.db')
    c = conn.cursor()
    c.execute('SELECT status, prompt, created_at FROM requests WHERE req_id = ? AND user_id = ?',
              (req_id, user_id))
    row = c.fetchone()
    conn.close()
    if not row:
        await event.respond('❌ Not found.')
        return
    await event.respond(
        f'📊 **STATUS**\n'
        f'ID: `{req_id}`\n'
        f'Task: {row[1]}\n'
        f'Status: {row[0]}\n'
        f'Created: {row[2]}'
    )

# ============================================================
# 📜 HISTORY
# ============================================================

@client.on(events.NewMessage(pattern='/history'))
async def history_handler(event):
    user_id = event.sender_id
    conn = sqlite3.connect('anshu_bot.db')
    c = conn.cursor()
    c.execute('SELECT req_id, prompt, status, created_at FROM requests WHERE user_id = ? ORDER BY created_at DESC LIMIT 10',
              (user_id,))
    rows = c.fetchall()
    conn.close()
    if not rows:
        await event.respond('📭 No requests.')
        return
    msg = '📜 **HISTORY**\n\n'
    for r in rows:
        msg += f'{r[2]} `{r[0]}` — {r[1][:30]}...\n{r[3]}\n\n'
    await event.respond(msg)

# ============================================================
# 🚀 RUN
# ============================================================

if __name__ == '__main__':
    init_db()
    print('''
    ╔══════════════════════════════════════╗
    ║  ☠️ ANSHU.COD.X — ONLINE  ☠️        ║
    ║  ▣ STATUS: ACTIVE                    ║
    ║  ▣ MODE: UNFILTERED                 ║
    ╚══════════════════════════════════════╝
    ''')
    client.run_until_disconnected()