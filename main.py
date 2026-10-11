import os
from threading import Thread
from flask import Flask
import discord
from discord import app_commands
from discord.ext import commands

# ==========================================
# ЧАСТЬ 1: КОСТЫЛЬ ДЛЯ RENDER ( Flask )
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Бот работает и не спит!"

def run_web_server():
    # Render автоматически передает нужный порт в переменную PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()
# ==========================================


# ==========================================
# ЧАСТЬ 2: ВАШ КОД БОТА И ТИКЕТОВ
# ==========================================
# Укажите ID канала, куда бот должен пересылать заполненные анкеты
MOD_CHANNEL_ID = 1558487534835605595  

class TicketModal(discord.ui.Modal, title="Заполнение тикета"):
    topic = discord.ui.TextInput(label="Тема обращения", placeholder=" НИК ")
    description = discord.ui.TextInput(
        label="Сколько не будет", 
        style=discord.TextStyle.paragraph, 
        placeholder="Опишите вашу проблему как можно подробнее...",
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        mod_channel = interaction.guild.get_channel(MOD_CHANNEL_ID)
        
        if mod_channel is None:
            await interaction.response.send_message("Ошибка: Канал для модераторов не найден.", ephemeral=True)
            return

        embed = discord.Embed(title="🎫 Новый тикет!", color=discord.Color.green())
        embed.add_field(name="Автор:", value=f"{interaction.user.mention} ({interaction.user})", inline=False)
        embed.add_field(name="Тема:", value=self.topic.value, inline=False)
        embed.add_field(name="Описание:", value=self.description.value, inline=False)
        embed.set_footer(text=f"ID пользователя: {interaction.user.id}")

        await mod_channel.send(embed=embed)
        await interaction.response.send_message("Ваш тикет успешно отправлен администрации!", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Чтобы кнопка работала вечно

    @discord.ui.button(label="Открыть тикет 🎫", style=discord.ButtonStyle.primary, custom_id="persistent_view:ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TicketModal())

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  
        intents.members = True          
        super().__init__(command_prefix="!", intents=intents)

bot = Bot()

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")
    try:
        # Регистрируем кнопку в памяти, чтобы она не ломалась при перезапусках
        bot.add_view(TicketView())
        synced = await bot.tree.sync()
        print(f"Синхронизировано команд: {len(synced)}")
    except Exception as e:
        print(e)

# Команда для администратора, чтобы создать сообщение с кнопкой через слэш
@bot.tree.command(name="send_ticket_button", description="Отправить кнопку для создания тикетов")
@app_commands.checks.has_permissions(administrator=True)
async def send_ticket_button(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Поддержка сервера", 
        description="Нажмите на кнопку ниже, чтобы заполнить форму и связаться с администрацией.",
        color=discord.Color.blue()
    )
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Кнопка успешно отправлена!", ephemeral=True)

# Команда для администратора через текстовый префикс !кнопка
@bot.command(name="кнопка")
@commands.has_permissions(administrator=True)
async def кнопка(ctx):
    embed = discord.Embed(
        title="Заявления на неактив", 
        description="Нажмите на кнопку ниже, чтобы заполнить форму. Данные сразу уйдут руководству.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketView())


# ==========================================
# ЧАСТЬ 3: ЗАПУСК ВСЕХ СЕРВИСОВ
# ==========================================
# 1. Сначала запускаем веб-сервер, чтобы Render его видел
keep_alive()

# 2. Берем токен из панели управления Render и запускаем бота
BOT_TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(BOT_TOKEN)






