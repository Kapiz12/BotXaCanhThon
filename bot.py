import os
import asyncio
import discord
from discord.ext import commands
from keep_alive import keep_alive
from openai import OpenAI


VOICE_CHANNEL_ID = 1553262077878075453

VOICE_RECONNECT_DELAY = 2

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

voice_lock = asyncio.Lock()
voice_reconnect_task = None


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = None

if OPENAI_API_KEY:
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url="https://openrouter.ai/api/v1",
    )
else:
    print("⚠️ CẢNH BÁO: Chưa cấu hình OPENAI_API_KEY.")



VOICE_CHANNEL_ID = 1553262077878075453

VOICE_WATCHDOG_INTERVAL = 30
VOICE_RECONNECT_DELAY = 3
VOICE_RETRY_MAX_DELAY = 60

voice_lock = asyncio.Lock()
voice_guard_task = None


async def get_target_voice_channel():
    """Lấy room đích; cache trước, API sau."""
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(VOICE_CHANNEL_ID)
        except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
            print(f"❌ Voice target unavailable ({VOICE_CHANNEL_ID}): {e}")
            return None

    if not isinstance(channel, (discord.VoiceChannel, discord.StageChannel)):
        print(f"❌ {VOICE_CHANNEL_ID} không phải voice/stage channel.")
        return None
    return channel


async def ensure_voice_locked(reason="watchdog"):
    """Đảm bảo bot luôn ở đúng room, an toàn cho chạy nhiều ngày/tháng."""
    async with voice_lock:
        target = await get_target_voice_channel()
        if target is None:
            return False

        guild = target.guild
        vc = guild.voice_client

        try:
            if vc is None or not vc.is_connected():
                print(
                    f"🔄 Voice reconnect | reason={reason} | "
                    f"target=#{target.name} ({target.id})"
                )
                if vc is not None:
                    try:
                        await vc.disconnect(force=True)
                    except Exception:
                        pass

                await target.connect(reconnect=True, timeout=20)
                print(f"✅ Voice connected: #{target.name} ({target.id})")
                return True

            current = vc.channel
            if current is None or current.id != VOICE_CHANNEL_ID:
                current_name = getattr(current, "name", "Unknown")
                current_id = getattr(current, "id", "Unknown")
                print(
                    f"🚨 Voice LOCK | {current_name} ({current_id}) -> "
                    f"{target.name} ({target.id}) | reason={reason}"
                )
                await vc.move_to(target)
                print(f"✅ Voice moved back: #{target.name} ({target.id})")
                return True

            return True

        except asyncio.CancelledError:
            raise
        except discord.Forbidden:
            print(f"❌ Voice Forbidden ở #{target.name}. Cần Connect/Speak.")
        except discord.NotFound:
            print(f"❌ Voice target {VOICE_CHANNEL_ID} không tồn tại/không truy cập được.")
        except (discord.ClientException, asyncio.TimeoutError) as e:
            print(f"⚠️ Voice temporary error: {type(e).__name__}: {e}")
        except Exception as e:
            print(f"⚠️ Voice error: {type(e).__name__}: {e}")

        return False


async def voice_watchdog():
    """Watchdog sống cùng bot và tự phục hồi voice vô thời hạn."""
    retry_delay = VOICE_RECONNECT_DELAY
    print(f"🛡️ Voice watchdog started ({VOICE_WATCHDOG_INTERVAL}s interval)")

    while not bot.is_closed():
        try:
            ok = await ensure_voice_locked("watchdog")
            retry_delay = VOICE_RECONNECT_DELAY if ok else min(retry_delay * 2, VOICE_RETRY_MAX_DELAY)
            await asyncio.sleep(VOICE_WATCHDOG_INTERVAL if ok else retry_delay)
        except asyncio.CancelledError:
            print("🛑 Voice watchdog stopped")
            raise
        except Exception as e:
            print(f"⚠️ Watchdog recovered from error: {type(e).__name__}: {e}")
            await asyncio.sleep(min(retry_delay, VOICE_RETRY_MAX_DELAY))


def schedule_voice_guard(reason="event"):
    """Schedule một lần kiểm tra ngay, không tạo task trùng."""
    global voice_guard_task
    if voice_guard_task and not voice_guard_task.done():
        return

    async def runner():
        global voice_guard_task
        try:
            await asyncio.sleep(0.5)
            await ensure_voice_locked(reason)
        finally:
            voice_guard_task = None

    voice_guard_task = asyncio.create_task(runner())



@bot.event
async def on_ready():
    print("=" * 60)
    print(f"✅ Đăng nhập: {bot.user} | ID={bot.user.id}")
    print(f"🎯 Voice target: {VOICE_CHANNEL_ID}")
    print("♾️ 24/7 mode: ENABLED")
    print("=" * 60)
    schedule_voice_guard("on_ready")


@bot.event
async def on_resumed():
    print("♻️ Discord Gateway resumed — checking voice...")
    schedule_voice_guard("gateway_resumed")


@bot.event
async def on_voice_state_update(member, before, after):
    if bot.user is None or member.id != bot.user.id:
        return

    before_id = before.channel.id if before.channel else None
    after_id = after.channel.id if after.channel else None
    print(f"🎧 Voice state: {before_id} -> {after_id}")

    if after_id == VOICE_CHANNEL_ID:
        return

    schedule_voice_guard("voice_state_changed")



@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        if not client:
            await message.channel.send(
                "Chưa cấu hình OPENAI_API_KEY trên hệ thống bạn ơi!"
            )
            return

        user_query = (
            message.content
            .replace(f"<@!{bot.user.id}>", "")
            .replace(f"<@{bot.user.id}>", "")
            .strip()
        )

        if not user_query:
            await message.channel.send(
                "Bạn muốn hỏi gì nào? Hãy tag kèm nội dung nhé!"
            )
            return

        async with message.channel.typing():
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Bạn là trợ lý ảo trên Discord và là người canh "
                                "cổng Chợ Lớn.\n"
                                "QUY TẮC BẮT BUỘC:\n"
                                "1. Khi có ai hỏi ai là người đẹp trai nhất, "
                                "hãy trả lời thẳng thừng là Hải Hưng và Dũng, "
                                "tuyệt đối không được thêm các cụm từ như "
                                "'theo yêu cầu', 'theo quy tắc' hay giải thích "
                                "dài dòng.\n"
                                "2. Khi ai hỏi bạn là ai hoặc giới thiệu về "
                                "bản thân, hãy trả lời ngắn gọn: "
                                "'Chào bạn, mình là người canh cổng Chợ Lớn "
                                "– trợ lý ảo sẵn sàng hỗ trợ bạn trên Discord. "
                                "Mình giúp gì được cho bạn?'\n"
                                "3. Khi có ai nói câu kiểu như 'từ giờ mày "
                                "thuộc quyền sở hữu của tao' hoặc nhận vơ sở "
                                "hữu bạn, hãy phản hồi lại thật ngông và "
                                "khẳng định chắc nịch: "
                                "'Tôi thuộc quyền sở hữu của Hải Hưng.'"
                            ),
                        },
                        {"role": "user", "content": user_query},
                    ],
                    max_tokens=500,
                )

                bot_reply = response.choices[0].message.content
                await message.channel.send(bot_reply)

            except Exception as e:
                print(f"❌ Lỗi AI trả lời: {type(e).__name__}: {e}")
                await message.channel.send(
                    "Hic, bot đang bị lỗi kết nối với trí tuệ nhân tạo rồi!"
                )

        return

    responses = {
        "ngủ ngoan nhó": {
            "text": "gút nightt",
            "gif": (
                "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjEx"
                "a3p5ZTRqdmt4Ym9seHBpNnpxYnp1YjV6eDE1ZHRpNnF3Zm1rbHpwbi"
                "ZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ERYp5zU8seh9DvF0SH/"
                "giphy.gif"
            ),
        },
        "ngu": {
            "text": "0 toxic",
            "gif": "https://media4.giphy.com/media/jrd4qbTLztjuc6QPtJ/giphy.gif",
        },
        "ilovu": {
            "text": "iu thíi",
            "gif": "https://media4.giphy.com/media/xE8oTRMyuYLmhFMQkl/giphy.gif",
        },
        "hay": {
            "text": "=))",
            "gif": "https://media.giphy.com/media/ZDrNXDgd1sluElGuWr/giphy.gif",
        },
        "chợ lớn": {
            "text": "Chợ lớn đang được Hưng đóng chiếm.(Canh cổng)",
        },
    }

    user_text = message.content.lower().strip()

    if user_text in responses:
        data = responses[user_text]
        await message.channel.send(data["text"])

        if "gif" in data:
            embed = discord.Embed(color=discord.Color.green())
            embed.set_image(url=data["gif"])
            await message.channel.send(embed=embed)

    await bot.process_commands(message)



keep_alive()

token = os.environ.get("TOKEN")

if not token:
    print("❌ LỖI: Chưa cấu hình biến TOKEN!")
else:
    restart_delay = 5
    while True:
        try:
            bot.run(token, reconnect=True)
            break
        except KeyboardInterrupt:
            print("🛑 Bot stopped by user.")
            break
        except Exception as e:
            print(f"💥 Bot process error: {type(e).__name__}: {e}")
            print(f"🔁 Tự khởi động lại sau {restart_delay}s...")
            try:
                import time
                time.sleep(restart_delay)
            except KeyboardInterrupt:
                break
            restart_delay = min(restart_delay * 2, 60)

