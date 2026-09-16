
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

# Khởi động web server ngầm
keep_alive()

# Lấy token từ Railway (bắt buộc tên biến môi trường ở Railway phải là TOKEN)
token = os.environ.get('TOKEN')
if not token:
    print("LỖI: Chưa cấu hình biến TOKEN trên Railway!")
else:
    bot.run(token)
