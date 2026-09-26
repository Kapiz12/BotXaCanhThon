import os
import asyncio
import discord
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ID phòng voice của bạn
VOICE_CHANNEL_ID = 1553262077878075453 

@bot.event
async def on_ready():
    print(f'Đã đăng nhập thành công: {bot.user}')
    
    channel = bot.get_channel(VOICE_CHANNEL_ID)
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

    # Danh sách từ khóa, câu trả lời và link GIF
    responses = {
        "ngủ ngoan nhó": {
            "text": "gút nightt",
            "gif": "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExa3p5ZTRqdmt4Ym9seHBpNnpxYnp1YjV6eDE1ZHRpNnF3Zm1rbHpwbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ERYp5zU8seh9DvF0SH/giphy.gif"
        },
        "ngu": {
            "text": "0 toxic",
            "gif": "https://media4.giphy.com/media/jrd4qbTLztjuc6QPtJ/giphy.gif"
        },
        "hay": {
            "text": "=))",
            "gif": "https://media.giphy.com/media/ZDrNXDgd1sluElGuWr/giphy.gif"
        }
        "chợ lớn": {
            "text": "Chợ lớn thuộc quyền sở hữu của Hải Hưng",
        }
    }

    user_text = message.content.lower().strip()
    
    if user_text in responses:
        data = responses[user_text]
        
        # 1. Gửi tin nhắn văn bản bình thường
        await message.channel.send(data['text'])
        
        # 2. Tạo Embed để nhúng ảnh GIF (giúp ẩn link xanh rườm rà)
        embed = discord.Embed(color=discord.Color.green())
        embed.set_image(url=data['gif'])
        
        # 3. Gửi embed đi
        await message.channel.send(embed=embed)

    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    # 1. Xử lý trường hợp chính con Bot bị rớt khỏi phòng voice
    if member.id == bot.user.id:
        if before.channel is not None and after.channel is None:
            print("Bot bị rớt khỏi phòng voice, đang tự động kết nối lại...")
            await asyncio.sleep(3)
            try:
                channel = bot.get_channel(VOICE_CHANNEL_ID)
                if channel:
                    await channel.connect()
                    print("Đã kết nối lại vào phòng voice thành công!")
            except Exception as e:
                print(f"Lỗi tự động kết nối lại voice: {e}")
        return

    # Bỏ qua nếu người thay đổi trạng thái là bot khác
    if member.bot:
        return

    # 2. Xử lý thông báo User Join / Out cho phòng voice cụ thể
    room = bot.get_channel(VOICE_CHANNEL_ID)
    if not room:
        return

    # Tìm một kênh text bất kỳ trong server để bot gửi tin nhắn thông báo (thường là kênh đầu tiên gửi được)
    text_channel = next((ch for ch in room.guild.text_channels if ch.permissions_for(room.guild.me).send_messages), None)
    if not text_channel:
        return

    room_name = room.name # Lấy tên phòng voice hiện tại (ví dụ: "Chợ lớn")

    # Trường hợp 1: Người dùng JOIN vào phòng
    if before.channel != room and after.channel == room:
        await text_channel.send(f"{room_name} xin chào {member.mention}")

    # Trường hợp 2: Người dùng OUT khỏi phòng
    elif before.channel == room and after.channel != room:
        await text_channel.send(f"{room_name} tạm biệt {member.mention}")

# Khởi động web server ngầm
keep_alive()

# Lấy token từ Railway
token = os.environ.get('TOKEN')
if not token:
    print("LỖI: Chưa cấu hình biến TOKEN trên Railway!")
else:
    bot.run(token)
