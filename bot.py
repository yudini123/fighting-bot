import os
import sqlite3

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------------
# 데이터베이스
# -------------------------

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS cheer(
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    count INTEGER DEFAULT 0
)
""")

conn.commit()


# -------------------------
# 봇 실행
# -------------------------

@bot.event
async def on_ready():
    print("=" * 40)
    print(f"{bot.user} 로그인 완료!")
    print("=" * 40)


# -------------------------
# 영신이형 화이팅
# -------------------------

@bot.command(name="영신이형화이팅")
async def cheer(ctx):

    cur.execute(
        "SELECT count FROM cheer WHERE user_id=?",
        (ctx.author.id,)
    )

    row = cur.fetchone()

    if row is None:

        my_count = 1

        cur.execute("""
        INSERT INTO cheer(user_id,username,count)
        VALUES(?,?,?)
        """,
        (
            ctx.author.id,
            ctx.author.display_name,
            my_count
        ))

    else:

        my_count = row[0] + 1

        cur.execute("""
        UPDATE cheer
        SET count=?,
            username=?
        WHERE user_id=?
        """,
        (
            my_count,
            ctx.author.display_name,
            ctx.author.id
        ))

    conn.commit()

    cur.execute("SELECT SUM(count) FROM cheer")
    total = cur.fetchone()[0]

    await ctx.reply(
        f"""
🔥 **영신이형 화이팅!!**

📢 총 응원 : **{total}회**

🙋 {ctx.author.display_name} : **{my_count}회**
"""
    )


# -------------------------
# 응원 랭킹
# -------------------------

@bot.command(name="응원랭킹")
async def ranking(ctx):

    cur.execute("""
    SELECT username,count
    FROM cheer
    ORDER BY count DESC
    LIMIT 10
    """)

    rows = cur.fetchall()

    if len(rows) == 0:
        await ctx.send("아직 응원이 없습니다.")
        return

    medal = ["🥇", "🥈", "🥉"]

    msg = "## 🔥 응원 랭킹\n\n"

    for i, row in enumerate(rows):

        icon = medal[i] if i < 3 else f"{i+1}."

        msg += f"{icon} {row[0]} - **{row[1]}회**\n"

    await ctx.send(msg)


try:
    bot.run(TOKEN)
except Exception as e:
    print("ERROR:", e)