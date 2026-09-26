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

    # Danh sách từ khóa và câu trả lời (giữ nguyên tính năng chat & gif bình thường của bạn)
    responses = {
        "ngủ ngoan nhó": {
            "text": "gút nightt",
            "gif": "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExa3p5ZTRqdmt4Ym9seHBpNnpxYnp1YjV6eDE1ZHRpNnF3Zm1rbHpwbiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ERYp5zU8seh9DvF0SH/giphy.gif"
        },
        "ngu": {
            "text": "0 toxic",
            "gif": "https://media4.giphy.com/media/jrd4qbTLztjuc6QPtJ/giphy.gif"
        },
        "ilovu": {
            "text": "iu Han thế nhò",
            "gif": "https://media4.giphy.com/media/xE8oTRMyuYLmhFMQkl/giphy.gif"
        },
        "hay": {
            "text": "=))",
            "gif": "https://media.giphy.com/media/ZDrNXDgd1sluElGuWr/giphy.gif"
        },
        "chợ lớn": {
            "text": "Chợ lớn đang được Hưng đóng chiếm.(Canh cổng)"
        }
    }

    user_text = message.content.lower().strip()
    
    if user_text in responses:
        data = responses[user_text]
        
        await message.channel.send(data['text'])
        
        if "gif" in data:
            embed = discord.Embed(color=discord.Color.green())
            embed.set_image(url=data['gif'])
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

    # Bỏ qua các bot khác
    if member.bot:
        return

    room = bot.get_channel(VOICE_CHANNEL_ID)
    if not room or not isinstance(room, discord.VoiceChannel):
        print(f"Không tìm thấy room voice với ID: {VOICE_CHANNEL_ID}")
        return

    room_name = room.name # "Chợ lớn"

    # Lấy khung chat tích hợp của phòng voice. 
    # Nếu server của bạn dùng tính năng voice chat mới, lệnh này sẽ trỏ thẳng vào đúng chỗ.
    text_chat = getattr(room, 'text_channel', None)
    
    if not text_chat:
        print(f"Cảnh báo: Phòng voice '{room_name}' không bật sẵn text_channel, đang dùng phương án dự phòng...")
        # Dự phòng: tìm kiếm kênh text thường có tên khớp với phòng voice trong server
        target_name = room_name.lower().replace(" ", "-")
        text_chat = discord.utils.get(room.guild.text_channels, name=target_name)

    if not text_chat:
        print("Lỗi: Không tìm thấy bất kỳ khung chat nào tương thích để gửi thông báo join/out!")
        return

    # Trường hợp 1: Người dùng JOIN vào phòng voice
    if before.channel != room and after.channel == room:
        try:
            await text_chat.send(f"{room_name} xin chào {member.mention}")
            print(f"Đã gửi thông báo Join cho {member.name}")
        except Exception as e:
            print(f"Lỗi khi gửi tin nhắn Join: {e}")

    # Trường hợp 2: Người dùng OUT khỏi phòng voice
    elif before.channel == room and after.channel != room:
        try:
            await text_chat.send(f"{room_name} tạm biệt {member.mention}")
            print(f"Đã gửi thông báo Out cho {member.name}")
        except Exception as e:
            print(f"Lỗi khi gửi tin nhắn Out: {e}")

# Khởi động web server ngầm
keep_alive()

# Lấy token từ Railway
token = os.environ.get('TOKEN')
if not token:
    print("LỖI: Chưa cấu hình biến TOKEN trên Railway!")
else:
    bot.run(token)
