import discord
from discord import app_commands
from discord.ext import commands

MOD_CHANNEL_ID = 1558487534835605595  # ID канала модераторов

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
        synced = await bot.tree.sync()
        print(f"Синхронизировано команд: {len(synced)}")
    except Exception as e:
        print(e)

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

@bot.command(name="кнопка")
@commands.has_permissions(administrator=True)
async def кнопка(ctx):
    embed = discord.Embed(
        title="Заявления на неактив", 
        description="Нажмите на кнопку ниже, чтобы заполнить форму. Данные сразу уйдут руководству.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=TicketView())

# Запуск бота с вашим рабочим токеном
bot.run('MTU1ODU0OTY1MzA0ODM5NzgzNQ.GXGtsi.wdhyuuHuI973BiQAVK82e1PNxBFqee0RLlJyXM')




