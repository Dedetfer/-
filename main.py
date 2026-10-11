# --- ЗАПЛАТКА ДЛЯ PYTHON 3.13+ ---
import sys
import types
if 'audioop' not in sys.modules:
    sys.modules['audioop'] = types.ModuleType('audioop')
# ---------------------------------

import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import discord
from discord.ext import commands

# --- ВЕБ-СЕРВЕР ДЛЯ ОБХОДА ОГРАНИЧЕНИЙ RENDER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Бот работает!".encode("utf-8"))

    def log_message(self, format, *args):
        return  # Отключаем лишний спам логов веб-сервера в консоль

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Веб-сервер проверки здоровья запущен на порту {port}")
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()
# ----------------------------------------------

MOD_CHANNEL_ID = 1558487534835605595  # ID вашего канала

class TicketModal(discord.ui.Modal, title="Заполнение тикета"):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.topic = discord.ui.InputText(label="Тема обращения", placeholder=" НИК ")
        self.description = discord.ui.InputText(
            label="Сколько не будет", 
            style=discord.InputTextStyle.paragraph, 
            placeholder="Опишите вашу проблему как можно подробнее...",
            max_length=1000
        )
        self.add_item(self.topic)
        self.add_item(self.description)

    async def callback(self, interaction: discord.Interaction):
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
        super().__init__(timeout=None)

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
        synced = await bot.sync_commands()
        print("Слэш-команды успешно синхронизированы!")
    except Exception as e:
        print(e)

# Команда /send_ticket_button
@bot.slash_command(name="send_ticket_button", description="Отправить кнопку для создания тикетов")
@commands.has_permissions(administrator=True)
async def send_ticket_button(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Поддержка сервера", 
        description="Нажмите на кнопку ниже, чтобы заполнить форму и связаться с администрацией.",
        color=discord.Color.blue()
    )
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("Кнопка успешно отправлена!", ephemeral=True)

# Обычная текстовая команда !кнопка
@bot.command(name="кнопка")
@commands.has_permissions(administrator=True)
async def кнопка(ctx):
    embed = discord.Embed(
        title="Заявления на неактив", 
        description="Нажмите на кнопку ниже, чтобы заполнить форму. Данные сразу уйдут руководству.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketView())

BOT_TOKEN = os.environ.get("DISCORD_TOKEN")

if not BOT_TOKEN:
    print("КРИТИЧЕСКАЯ ОШИБКА: Переменная окружения DISCORD_TOKEN не найдена!")
else:
    bot.run('MTU1ODU0OTY1MzA0ODM5NzgzNQ.Gf2tgr.7BJoXwID1NmkP6gYke_gzU-xql6pzWrW-uBitI')

