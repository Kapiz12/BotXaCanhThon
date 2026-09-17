import os
import asyncio
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
    
    # ID phòng voice của bạn
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
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Danh sách từ khóa và câu trả lời kèm link GIF
    responses = {
        "ngủ ngoan nhớ": {
            "text": "gút nightt",
            "gif": "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExaTFlNHFiZzVlYzJicGVtdmMyMmxiODk2eHluYWx1bTR3ODBtcmQ4ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ERYp5uZ8seh9DvF0SH/giphy.gif"
        },
        "ngu": {
            "text": "0 toxic",
            "gif": "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExaTFlNHFiZzVlYzJicGVtdmMyMmxiODk2eHluYWx1bTR3ODBtcmQ4ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jrd4qbTLztjuc6QPtJ/giphy.gif"
        },
        "ilovu": {
            "text": "iu Han thế nhò",
            "gif": "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExaTFlNHFiZzVlYzJicGVtdmMyMmxiODk2eHluYWx1bTR3ODBtcmQ4ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/xE8oTRMyuYLmhFMQkl/giphy.gif"
        }
    }

    user_text = message.content.lower().strip()
    
    if user_text in responses:
        data = responses[user_text]
        
        # Gửi chữ trước
        await message.channel.send(data['text'])
        
        # Tạo Embed để hiển thị ảnh GIF ẩn link
        embed = discord.Embed(color=discord.Color.green())
        embed.set_image(url=data['gif'])
        await message.channel.send(embed=embed)

    await bot.process_commands(message)
@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id:
        if before.channel is not None and after.channel is None:
            print("Bot bị rớt khỏi phòng voice, đang tự động kết nối lại...")
            await asyncio.sleep(3)
            try:
                voice_channel_id = 1538846775853449307
                channel = bot.get_channel(voice_channel_id)
                if channel:
                    await channel.connect()
                    print("Đã kết nối lại vào phòng voice thành công!")
            except Exception as e:
                print(f"Lỗi tự động kết nối lại voice: {e}")

# Khởi động web server ngầm
keep_alive()

# Lấy token từ Railway
token = os.environ.get('TOKEN')
if not token:
    print("LỖI: Chưa cấu hình biến TOKEN trên Railway!")
else:
    bot.run(token)
