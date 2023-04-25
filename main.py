import os
import discord
import random

intents = discord.Intents().all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    for guild in client.guilds:
        print(f'Successfully connected to server: {guild.name} ({guild.id})')
    print('Bot is ready!')

@client.event
async def on_message(message):
    global initiative_order, initiative_dict, current_turn
    
    # Check if the message starts with "/r"
    if message.content.startswith('/r'):
        # Split the message into the number of dice, sides, and bonus
        dice_str = message.content.split(' ')[1]
        if '+' in dice_str:
            dice_count, dice_sides_and_bonus = dice_str.split('d')
            dice_sides, bonus = dice_sides_and_bonus.split('+')
        else:
            dice_count, dice_sides = dice_str.split('d')
            bonus = 0
    
        dice_count, dice_sides, bonus = int(dice_count), int(dice_sides), int(bonus)
    
        # Roll the dice and create a response message
        rolls = [random.randint(1, dice_sides) for i in range(dice_count)]
        rolls_str = '{' + ', '.join([str(r) for r in rolls]) + '}'
        total = sum(rolls) + bonus
        response = f'{message.author.mention} rolled {dice_count} dice with {dice_sides} sides and a bonus of {bonus}: {rolls_str} + {bonus} = **{total}**'
    
        # Send the response message
        await message.channel.send(response)   

    # Check if the message starts with "/f"
    elif message.content.startswith('/f'):
        # Roll 4 Fate dice and add them up
        fate_rolls = [random.choice([-1, 0, 1]) for i in range(4)]
        fate_total = sum(fate_rolls)
        response = f'{message.author.mention} rolled 4 Fate dice: {fate_rolls} = **{fate_total}**'
    
        # Send the response message
        await message.channel.send(response)

    # Check if the message starts with "/w"
    elif message.content.startswith('/w'):
        # Get the number of dice to roll
        dice_count = int(message.content.split(' ')[1])
    
        # Roll the dice and count the number of successes (8 or higher)
        rolls = [random.randint(1, 10) for i in range(dice_count)]
        successes = len([r for r in rolls if r >= 8])
        rolls_str = '{' + ', '.join([str(r) for r in rolls]) + '}'
        response = f'{message.author.mention} rolled {dice_count} World of Darkness dice: {rolls_str} = **{successes}** successes'
    
        # Send the response message
        await message.channel.send(response)
    
    # Check if the message starts with "/sr"
    elif message.content.startswith('/sr'):
        # Get the number of dice to roll
        dice_count = int(message.content.split(' ')[1])
    
        # Roll the dice and count the number of successes (5 or higher)
        rolls = [random.randint(1, 6) for i in range(dice_count)]
        successes = len([r for r in rolls if r >= 5])
    
        # Check for glitches
        glitches = 0
        if rolls.count(1) >= (dice_count / 2):
            glitches = 1
    
        rolls_str = '{' + ', '.join([str(r) for r in rolls]) + '}'
        if glitches == 1:
            response = f'{message.author.mention} rolled {dice_count} Shadowrun dice: {rolls_str} = **{successes} successes and a glitch**'
        else:
            response = f'{message.author.mention} rolled {dice_count} Shadowrun dice: {rolls_str} = **{successes}** successes'
    
        # Send the response message
        await message.channel.send(response)

    # Check if the message starts with "/str"
    elif message.content.startswith('/str'):
        # Get the user's strength score from the command
        str_score = int(message.content.split(' ')[1])
    
        # Calculate the character's carrying capacity and encumbrance
        carrying_capacity = str_score * 15
        encumbered_weight = carrying_capacity / 2
    
        # Calculate the character's maximum weights for light and medium loads
        encumbered_at = encumbered_weight
        maximum_carrying_capacity = carrying_capacity
    
        # Calculate the character's maximum weight for pushing, dragging, and lifting
        push_drag_max = carrying_capacity * 5
        lift_max = carrying_capacity * 2
    
        response = (f'{message.author.mention}, your carrying capacity is **{carrying_capacity} lbs**. '
                    f'If you carry more than **{encumbered_weight} lbs**, you are encumbered and your speed is reduced. '
                    f'Your maximum carry weights are:\n'
                    f'Encumbered At: **{encumbered_at} lbs**.\n'
                    f'Maximum Carrying Capacity: **{maximum_carrying_capacity} lbs**.\n'
                    f'Push/Drag: **{push_drag_max} lbs**.\n'
                    f'Lift: **{lift_max} lbs**.')
    
        # Send the response message
        await message.channel.send(response)

    # Check if the message starts with "/initiative"
    elif message.content.startswith('/initiative'):
        # Clear the initiative tracker
        initiative_order = []
        initiative_dict = {}
        current_turn = 0
    
        # Get the list of characters and their initiatives
        character_list = message.content.split(' ')[1:]
        for i in range(len(character_list)):
            character_initiative = int(character_list[i].split('=')[1])
            character_name = character_list[i].split('=')[0]
    
            # Add the character to the initiative tracker
            initiative_dict[character_name] = character_initiative
    
        # Sort the characters in initiative order
        initiative_order = sorted(initiative_dict, key=lambda x: initiative_dict[x], reverse=True)
    
        # Create the response message
        response = '**Initiative Order:**\n'
        for i in range(len(initiative_order)):
            response += f'{i+1}. {initiative_order[i]} ({initiative_dict[initiative_order[i]]})\n'
    
        # Send the response message
        await message.channel.send(response)
    
        # Check if there are any characters in the initiative tracker
        if len(initiative_order) == 0:
            response = 'Initiative tracker is empty. Use the /initiative command to start tracking initiative.'
        else:
            # Get the name of the next character in initiative order
            next_character = initiative_order[current_turn % len(initiative_order)]
            current_turn += 1
    
            # Create the response message
            response = f'Next up: **{next_character}**'
    
        # Send the response message
        await message.channel.send(response)    

    # Check if the message starts with "/next"
    elif message.content.startswith('/next'):
        # Check if there are any characters in the initiative tracker
        if len(initiative_order) == 0:
            response = 'Initiative tracker is empty. Use the /initiative command to start tracking initiative.'
        else:
            # Get the name of the next character in initiative order
            next_character = initiative_order[current_turn % len(initiative_order)]
            current_turn += 1
    
            # Create the response message
            response = f'Next up: **{next_character}**'
    
        # Send the response message
        await message.channel.send(response)   

    # Check if the message starts with "/commands"
    elif message.content.startswith('/commands'):
        # Create the response message
        response = 'Available commands:\n'
        response += '/r [XdY[+Z]] - Roll X dice with Y sides and add a bonus of Z.\n'
        response += '/f - Roll 4 Fate dice and add them up.\n'
        response += '/w X - Roll X World of Darkness dice and count the number of successes.\n'
        response += '/sr X - Roll X Shadowrun dice and count the number of successes (5 or higher). Also checks for glitches.\n'
        response += '/str X - Calculate carrying capacity and encumbrance based on a Strength score of X.\n'
        response += '/initiative [name1=X name2=Y ...] - Start tracking initiative order. If names and initiative values are provided, they will be added to the tracker. Otherwise, the tracker will be empty.\n'
        response += '/next - Get the name of the next character in the initiative order.\n'
        response += '/commands - Display this message.'
    
        # Send the response message
        await message.channel.send('```' + response + '```')

@client.event
async def on_guild_join(guild):
    print(f'Joined new server: {guild.name} ({guild.id})')

my_secret = os.environ['DISCORD_TOKEN']
client.run(my_secret)
