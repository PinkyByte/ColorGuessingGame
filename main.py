import os
import discord
import game
import img_gen
from states import State
import requests
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

bot = commands.Bot(command_prefix = '!', intents = discord.Intents.all())

client = MongoClient('localhost', 27017)
db = client['users']
collection = db['levels']

user_games = {}

@bot.event
async def on_ready() -> None:
    print('Bot is Up and Ready!')
    await bot.change_presence(status = discord.Status.online, activity = discord.Game("/rules"))
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)

@bot.tree.command(name = 'rules', description = 'Having issues? Read this.')
async def rules(interaction: discord.Interaction) -> None:
    await interaction.response.send_message('**\U0001F3A8 CGG - The Ultimate Color Guessing Game** based on the famous rage game Színözön (without the voice recognition). The bot generates four colors, and the goal is to guess all of them in a limited amount of tries. If you don\'t get them, the bot will give you some clues based on your guess. Have fun! \U0001F3A8\n**Commands:**\n**/start_game**: Start a new game.\n**/guess**: Guess a color.\nThe color options are: \U0001F534 Red, \U000026AA White, \U0001F535 Blue, \U0001F338 Pink, \U0001F7E0 Orange, \U0001F7E3 Purple, \U0001F7E1 Yellow, \U0001F7E2 Green.\nYou get four colors as a result of your guess. Meaning of colors:\n\U000026AB Right color\n\U000026AA Right color, but on wrong place\n\U0000274C Wrong color\n**/reset**: Reset your current game in progress.\n**/tell_solution**: Tells the solution of your active game.\n**/get_level**: Get your current level and exp needed to level up. (Long usernames won\'t be fully displayed due to not fitting into the name box.)\n**/leaderboard**: Check the top 10 players on the server.\n**/change_color**: Change the color of your profile card. You can pick from eight colors. (The default color is white.)', ephemeral = True)

@bot.tree.command(name = 'start_game', description = 'Start a new game!')
async def start_game(interaction: discord.Interaction) -> None:
    if not collection.find_one({'user': interaction.user.id}):
        collection.insert_one({'user': interaction.user.id, 'level': 1, 'exp': 100, 'total': 0, 'color': 'white'})
    user_games[interaction.user.id] = game.Game()
    await interaction.response.send_message(f'You can start guessing! ({user_games[interaction.user.id].get_tries()}/11 guess(es) left)')

@bot.tree.command(name = 'reset', description = 'Reset your game in progress.')
async def reset(interaction: discord.Interaction) -> None:
    if interaction.user.id in user_games:
        del user_games[interaction.user.id]
    await interaction.response.send_message(f'Game has been reseted.')

@bot.tree.command(name = 'tell_solution', description = 'Tells the solution.')
async def tell_solution(interaction: discord.Interaction) -> None:
    if interaction.user.id in user_games:
        solution = user_games[interaction.user.id].get_solution()
        del user_games[interaction.user.id]
        await interaction.response.send_message(f'Solution:\n{solution[0]} {solution[1]} {solution[2]} {solution[3]}')
    else:
        await interaction.response.send_message(f'You haven\'t started a game yet! Start a new game using **/start_game**.')

choices = [app_commands.Choice(name = '\U0001F534 Red', value = 'Red'), app_commands.Choice(name = '\U000026AA White', value = 'White'), app_commands.Choice(name = '\U0001F535 Blue', value = 'Blue'), app_commands.Choice(name = '\U0001F338 Pink', value = 'Pink'), app_commands.Choice(name = '\U0001F7E0 Orange', value = 'Orange'), app_commands.Choice(name = '\U0001F7E3 Purple', value = 'Purple'), app_commands.Choice(name = '\U0001F7E1 Yellow', value = 'Yellow'), app_commands.Choice(name = '\U0001F7E2 Green', value = 'Green')]

@bot.tree.command(name = 'guess', description = 'Submit a guess.')
@app_commands.choices(color_1 = choices, color_2 = choices, color_3 = choices, color_4 = choices)
async def guess(interaction: discord.Interaction, color_1: app_commands.Choice[str], color_2: app_commands.Choice[str], color_3: app_commands.Choice[str], color_4: app_commands.Choice[str]) -> None:
    if not interaction.user.id in user_games:
        await interaction.response.send_message(f'You haven\'t started a game yet! Start a new game using **/start_game**.')
    else:
        result, solution, state = user_games[interaction.user.id].evaluate([color_1.value, color_2.value, color_3.value, color_4.value])
        if state == State.WON:
            exp = user_games[interaction.user.id].return_exp()
            del user_games[interaction.user.id]
            exp_to_next = collection.find_one({'user': interaction.user.id}, {'exp': 1})
            level = collection.find_one({'user': interaction.user.id}, {'level': 1})
            if level.get('level') < 31622: 
                if exp_to_next.get('exp') - exp > 0:
                    collection.update_one({'user': interaction.user.id}, {'$set': {'exp': exp_to_next.get('exp') - exp, 'total': collection.find_one({'user': interaction.user.id}, {'total': 1}).get('total') + exp}})
                    await interaction.response.send_message(f'{solution[0]} {solution[1]} {solution[2]} {solution[3]}\nCongratulations, you won!')
                else:
                    collection.update_one({'user': interaction.user.id}, {'$set': {'level': level.get('level') + 1}})
                    level = collection.find_one({'user': interaction.user.id}, {'level': 1})
                    if level.get('level') < 31622:
                        collection.update_one({'user': interaction.user.id}, {'$set': {'exp': int(pow(((level.get('level')) / 0.1), 2)) + ((exp_to_next.get('exp') - exp)), 'total': collection.find_one({'user': interaction.user.id}, {'total': 1}).get('total') + exp}})
                        await interaction.response.send_message(f'{solution[0]} {solution[1]} {solution[2]} {solution[3]}\nCongratulations, you won! Your new level is: {level.get('level')}.')
                    else:
                        await interaction.response.send_message(f'{solution[0]} {solution[1]} {solution[2]} {solution[3]}\nCongratulations, you won... Level 31622? Please touch some grass bro.')
            else:
                await interaction.response.send_message(f'{solution[0]} {solution[1]} {solution[2]} {solution[3]}\nCongratulations, you won... Level 31622? Please touch some grass bro.')
        elif state == State.WRONG_GUESS:
            await interaction.response.send_message(f'{solution[0]} {solution[1]} {solution[2]} {solution[3]}\n{result[0]} {result[1]} {result[2]} {result[3]}\n({user_games[interaction.user.id].get_tries()}/11 guess(es) left)')
        else:
            await interaction.response.send_message(f'{solution[0]} {solution[1]} {solution[2]} {solution[3]}\nGame over!')
            del user_games[interaction.user.id]

@bot.tree.command(name = 'get_level', description = 'Get your level.')
async def get_level(interaction: discord.Interaction) -> None:
    if collection.find_one({'user': interaction.user.id}):
        username = bot.get_user(interaction.user.id).name
        level = collection.find_one({'user': interaction.user.id}).get('level')
        exp = collection.find_one({'user': interaction.user.id}).get('exp')
        total = collection.find_one({'user': interaction.user.id}).get('total')
        color = collection.find_one({'user': interaction.user.id}).get('color')
        img = requests.get(interaction.user.display_avatar.url)
        buffer = img_gen.create_card(username, level, exp, total, img, color)  
        await interaction.response.send_message(file = discord.File(fp = buffer, filename = 'card.png'))
    else:
        await interaction.response.send_message('You don\'t have a profile yet. Start a game using **/start_game** to register a profile and start leveling up.')

@bot.tree.command(name = 'leaderboard', description = 'Check the top players on your server.')
async def leaderboard(interaction: discord.Interaction) -> None:
    users = collection.find({'user': {'$in': [member.id for member in interaction.guild.members]}}).sort([('level', -1), ('exp', 1)]).limit(10)
    if users is None:
        await interaction.response.send_message('No players found on the server.')
    else:
        usernames = []
        for user in users:
            usernames.append((bot.get_user(user.get('user')).name, user.get('level'), user.get('exp')))
        buffer = img_gen.create_leaderboard(usernames)
        await interaction.response.send_message(file = discord.File(fp = buffer, filename = 'leaderboard.png'))

@bot.tree.command(name = 'change_color', description = 'Change the color of your card.')
@app_commands.choices(color = choices)
async def change_color(interaction: discord.Interaction, color: app_commands.Choice[str]) -> None:
    if collection.find_one({'user': interaction.user.id}):
        collection.update_one({'user': interaction.user.id}, {'$set': {'color': color.value}})
        await interaction.response.send_message(f'Color changed to {color.value}.')
    else:
        await interaction.response.send_message('You don\'t have a profile yet. Start a game using **/start_game** to register a profile and start leveling up.')

bot.run(os.getenv('DISCORD_TOKEN'))
