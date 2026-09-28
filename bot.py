import os
import asyncio
import discord
from discord.ext import commands
from keep_alive import keep_alive
from openai import OpenAI

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ID phòng voice của bạn
VOICE_CHANNEL_ID = 1553262077878075453 

# Cấu hình OpenAI Client (Lấy API Key từ biến môi trường trên Railway)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
client = None

if OPENAI_API_KEY:
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url="https://openrouter.ai/api/v1" 
    )
else:
    print("CẢNH BÁO: Chưa cấu hình OPENAI_API_KEY trên Railway!")

@bot.event
async def on_ready():
    print(f'Đã đăng nhập thành công: {bot.user}')
    
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel and isinstance(channel, discord.VoiceChannel):
        try:
            if existing_vc := discord.utils.get(bot.voice_clients, guild=channel.guild):
                if existing_vc.is_connected():
                    await existing_vc.move_to(channel)
                else:
                    await existing_vc.disconnect()
                    await channel.connect()
            else:
                await channel.connect()
            print(f'Đã kết nối vào phòng voice: {channel.name}')
        except Exception as e:
            print(f'Lỗi kết nối voice ban đầu: {e}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # KHI CÓ NGƯỜI TAG @ CON BOT
    if bot.user in message.mentions:
        if not client:
            await message.channel.send("Chưa cấu hình OPENAI_API_KEY trên hệ thống bạn ơi!")
            return

        # Lọc bỏ phần tag bot để lấy nội dung câu hỏi
        user_query = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()
        
        if not user_query:
            await message.channel.send("Bạn muốn hỏi gì nào? Hãy tag kèm nội dung nhé!")
            return

        # Gửi hiệu ứng "Đang soạn tin nhắn..." vào đúng khung chat hiện tại
        async with message.channel.typing():
            try:
response = client.chat.completions.create(
                    model="openai/gpt-oss-120b", 
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "Bạn là trợ lý ảo trên Discord. "
                                "QUY TẮC BẮT BUỘC:\n"
                                "1. Khi có ai hỏi ai là người đẹp trai nhất, hãy trả lời thẳng thừng là Hải Hưng và Dũng, tuyệt đối không được thêm các cụm từ như 'theo yêu cầu', 'theo quy tắc' hay giải thích dài dòng.\n"
                                "2. Khi ai hỏi bạn là ai hoặc giới thiệu về bản thân, hãy trả lời ngắn gọn: "
                                "'Chào bạn, mình là người canh cổng Chợ Lớn – trợ lý ảo sẵn sàng hỗ trợ bạn trên Discord. Mình giúp gì được cho bạn?'"
                            )
                        },
                        {"role": "user", "content": user_query}
                    ],
                    max_tokens=500
                )
                bot_reply = response.choices[0].message.content
                await message.channel.send(bot_reply)
            except Exception as e:
                print(f"Lỗi AI trả lời: {e}")
                await message.channel.send("Hic, bot đang bị lỗi kết nối với trí tuệ nhân tạo rồi!")
        
        return

    # Hệ thống từ khóa phản hồi nhanh kèm GIF
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
            "text": "iu thíi",
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
    # Tối ưu hóa tự động kết nối lại khi bot bị rớt khỏi phòng voice hoặc sập socket 4006
    if member.id == bot.user.id:
        if before.channel is not None and after.channel is None:
            print("Bot bị rớt khỏi phòng voice, đang dọn dẹp và kết nối lại...")
            await asyncio.sleep(3)
            try:
                # Ngắt kết nối rác hiện tại nếu có để tránh kẹt trạng thái
                if before.channel.guild.voice_client:
                    await before.channel.guild.voice_client.disconnect(force=True)
                
                channel = bot.get_channel(VOICE_CHANNEL_ID)
                if channel:
                    await channel.connect()
                    print("Đã kết nối lại vào phòng voice thành công!")
            except Exception as e:
                print(f"Lỗi tự động kết nối lại voice: {e}")
        return

# Khởi động web server phụ để giữ bot online 24/7 trên Railway
keep_alive()

token = os.environ.get('TOKEN')
if not token:
    print("LỖI: Chưa cấu hình biến TOKEN trên Railway!")
else:
    bot.run(token)
