import os
import discord
from discord.ext import commands
from keep_alive import keep_alive  # Gọi hàm giữ sống từ file keep_alive.py

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Đã đăng nhập thành công: {bot.user}')
    
    # ID kênh thoại bạn muốn bot treo (Nhớ bật Developer Mode trên Discord để chuột phải copy ID phòng voice)
    voice_channel_id = 1538846775853449307 # <-- Thay ID phòng voice của bạn vào đây
    
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

# Chạy web server ngầm trước khi bật bot
keep_alive()

# Lấy Token từ biến môi trường (Bảo mật tuyệt đối) hoặc dán trực tiếp token vào đây
bot.run(os.environ.get('TOKEN'))