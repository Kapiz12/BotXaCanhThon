
import os
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Đã đăng nhập thành công: {bot.user}')
    
    # THAY ID PHÒNG VOICE CỦA BẠN VÀO ĐÂY (giữ nguyên dạng số)
    voice_channel_id = 1538846775853449307
    
    channel = bot.get_channel(voice_channel_id)
    if channel and isinstance(channel, discord.VoiceChannel):
        try:
            if existing_vc := discord.utils.get(bot.voice_clients, guild=channel.guild):
                await existing_vc.move_to(channel)
            else:
                await channel.connect()
            print(f'Đã kết nối vào phòng voice: {channel.name}')
        except Exception as e:
            print(f'Lỗi kết nối voice: {e}')
    else:
        print('Không tìm thấy kênh thoại hợp lệ!')
else:
        print('Không tìm thấy kênh thoại hợp lệ!')

else:
            print('Không tìm thấy kênh thoại hợp lệ!')

# --- DÁN ĐOẠN CODE NÀY VÀO ĐÂY ---
@bot.event
async def on_voice_state_update(member, before, after):
    # Kiểm tra xem người bị thay đổi trạng thái có phải là bot của mình không
    if member.id == bot.user.id:
        # Nếu bot bị ngắt kết nối khỏi phòng voice mà không chủ động rời đi
        if before.channel is not None and after.channel is None:
            print("Bot bị rớt khỏi phòng voice, đang tự động kết nối lại...")
            await asyncio.sleep(3) # Đợi 3 giây ổn định mạng
            try:
                voice_channel_id = 1538846775853449307 # ID phòng voice của bạn
                channel = bot.get_channel(voice_channel_id)
                if channel:
                    await channel.connect()
                    print("Đã kết nối lại vào phòng voice thành công!")
            except Exception as e:
                print(f"Lỗi tự động kết nối lại voice: {e}")
# ----------------------------------

# Khởi động web server ngầm
keep_alive()
# --- DÁN ĐOẠN CODE NÀY VÀO ĐÂY ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    responses = {
        "xin chào": "Chào bạn nhé! Chúc bạn một ngày tốt lành.",
        "luật server là gì": "Bạn vui lòng đọc kỹ nội quy ở kênh #rules nhé!",
        "bot ơi": "Dạ, mình đây! Mình đang túc trực 24/7 nè.",
    }

    user_text = message.content.lower().strip()
    if user_text in responses:
        await message.channel.send(responses[user_text])

    await bot.process_commands(message)
# ----------------------------------

# Khởi động web server ngầm
keep_alive()
# Khởi động web server ngầm
keep_alive()

# Lấy token từ Railway (bắt buộc tên biến môi trường ở Railway phải là TOKEN)
token = os.environ.get('TOKEN')
if not token:
    print("LỖI: Chưa cấu hình biến TOKEN trên Railway!")
else:
    bot.run(token)
