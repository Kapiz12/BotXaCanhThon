import os
import asyncio
import discord
from discord.ext import commands
from keep_alive import keep_alive
# import thư viện AI (Ví dụ ở đây dùng google-generativeai)
import google.generativeai as genai

intents = discord.Intents.default()
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ID phòng voice của bạn
VOICE_CHANNEL_ID = 1553262077878075453 

# Cấu hình Google Gemini AI (Bạn cần lưu API Key vào biến môi trường GEMINI_API_KEY trên Railway)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel('gemini-1.5-flash') # Hoặc gemini-pro
else:
    print("CẢNH BÁO: Chưa cấu hình GEMINI_API_KEY trên Railway!")

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

@bot.event
async def on_message(message):
    # Không để bot tự trả lời tin nhắn của chính nó
    if message.author == bot.user:
        return

    # KIỂM TRA XEM BOT CÓ ĐƯỢC TAG TRONG TIN NHẮN KHÔNG
    if bot.user in message.mentions:
        if not GEMINI_API_KEY:
            await message.channel.send("Chưa cấu hình API Key cho AI trên hệ thống bạn ơi!")
            return

        # Lấy nội dung câu hỏi (lọc bỏ phần @mention của bot cho sạch chữ)
        user_query = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()
        
        if not user_query:
            await message.channel.send("Bạn muốn hỏi gì nào? Hãy tag kèm câu hỏi nhé!")
            return

        # Gửi trạng thái "Đang suy nghĩ..." (Typing) vào đúng khung chat hiện tại
        async with message.channel.typing():
            try:
                # Gọi AI để sinh câu trả lời
                response = ai_model.generate_content(user_query)
                bot_reply = response.text
                
                # Gửi câu trả lời trực tiếp vào chính cái channel/khung chat đang hỏi
                await message.channel.send(bot_reply)
            except Exception as e:
                print(f"Lỗi AI trả lời: {e}")
                await message.channel.send("Hic, AI đang lú quá chưa nghĩ ra câu trả lời!")
        
        return # Thoát luôn, không chạy tiếp phần từ khóa cũ nữa (hoặc bạn có thể giữ lại nếu muốn)

    # (Tùy chọn) Vẫn giữ lại kho từ khóa cũ của bạn nếu muốn kết hợp cả hai
    responses = {
        "ngủ ngoan nhó": {"text": "gút nightt", "gif": "https://media4.giphy.com/media/ERYp5zU8seh9DvF0SH/giphy.gif"},
        "ngu": {"text": "0 toxic", "gif": "https://media4.giphy.com/media/jrd4qbTLztjuc6QPtJ/giphy.gif"},
        "ilovu": {"text": "iu thíi", "gif": "https://media4.giphy.com/media/xE8oTRMyuYLmhFMQkl/giphy.gif"},
        "hay": {"text": "=))", "gif": "https://media.giphy.com/media/ZDrNXDgd1sluElGuWr/giphy.gif"},
        "chợ lớn": {"text": "Chợ lớn đang được Hưng đóng chiếm.(Canh cổng)"}
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
    if member.id == bot.user.id:
        if before.channel is not None and after.channel is None:
            await asyncio.sleep(3)
            try:
                channel = bot.get_channel(VOICE_CHANNEL_ID)
                if channel:
                    await channel.connect()
            except Exception as e:
                print(f"Lỗi kết nối lại voice: {e}")

keep_alive()

token = os.environ.get('TOKEN')
if token:
    bot.run(token)
