import os
import discord
import random
import openai
import re

intents = discord.Intents().all()
client = discord.Client(intents=intents)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the global initiative variables
initiative_order = []
initiative_dict = {}
current_turn = 0
sr_initiative_order = []
sr_initiative_dict = {}
sr_current_turn = 0
sr_round_counter = 1

@client.event
async def on_ready():
    for guild in client.guilds:
        print(f'Successfully connected to server: {guild.name} ({guild.id})')
    print('Bot is ready!')

@client.event
async def on_message(message):
    global initiative_order
    global initiative_dict
    global current_turn
    global sr_initiative_order, sr_initiative_dict, sr_current_turn, sr_round_counter
    
    # Check if the message starts with "/roll"
    if message.content.startswith('/roll'):
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
    
    # Check if the message starts with "/srroll"
    elif message.content.startswith('/srroll'):
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
    
        # Check if there are any characters in the initiative tracker
        if len(initiative_order) == 0:
            response = 'Initiative tracker is empty. Use the /initiative command to start tracking initiative.'
        else:
            # Create the response message
            response = '**Initiative Order:**\n'
            for i in range(len(initiative_order)):
                response += f'{i+1}. {initiative_order[i]} ({initiative_dict[initiative_order[i]]})\n'
    
            # Get the name of the next character in initiative order
            next_character = initiative_order[current_turn % len(initiative_order)]
            current_turn += 1
    
            # Add the name of the next character to the response message
            response += f'\nNext up: **{next_character}**'
    
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
        response += '/roll [XdY[+Z]] - Roll X dice with Y sides and add a bonus of Z.\n'
        response += '/f - Roll 4 Fate dice and add them up.\n'
        response += '/w X - Roll X World of Darkness dice and count the number of successes.\n'
        response += '/sr X - Roll X Shadowrun dice and count the number of successes (5 or higher). Also checks for glitches.\n'
        response += '/str X - Calculate carrying capacity and encumbrance based on a Strength score of X.\n'
        response += '/initiative [name1=X name2=Y ...] - Start tracking initiative order. If names and initiative values are provided, they will be added to the tracker. Otherwise, the tracker will be empty.\n'
        response += '/add [name] [initiative] - Add a new combatant to the initiative tracker.\n'
        response += '/remove [target] - Remove a target from the initiative tracker or status list.\n'
        response += '/initiativeorder - Display the current initiative order.\n'
        response += '/next - Get the name of the next character in the initiative order.\n'
        response += '/endcombat - End the current combat encounter and clear the initiative tracker.\n'
        response += '/srinitiative [name1=X name2=Y ...] - Start tracking initiative order for Shadowrun. If names and initiative values are provided, they will be added to the tracker. Otherwise, the tracker will be empty.\n'
        response += '/srnext - Get the name of the next character in the initiative order for Shadowrun.\n'
        response += '/srnewround - Clear the initiative tracker and start a new round of combat for Shadowrun.\n'
        response += '/sradjust [character name] X - Adjust the initiative value of a character in the Shadowrun initiative tracker by X.\n'
        response += '/srendcombat - Clears the current initiative tracker.\n'
        response += '/ai [prompt] - Send a prompt to GPT-3.5 Turbo and get a response.\n'
        response += '/names [genre] [subject_type] - Generate a list of ten names suitable for a subject of the specified type in the current genre.\n'
        response += '/npc [genre] [npc_type] - Generate a description and an AI Image Generator instruction for an NPC of the specified type in the current genre.\n'
        response += '/location [genre] [location_info] - Generate a description of an interesting location that incorporates the specified info in the current genre.'
        
        
        # Send the response message
        await message.channel.send('```' + response + '```')

    # Check if the message starts with "/remove"
    elif message.content.startswith('/remove'):
        # Check if there are any characters in the initiative tracker
        if len(initiative_order) == 0:
            response = 'Initiative tracker is empty. Use the /initiative command to start tracking initiative.'
            await message.channel.send(response)
            return

        # Get the target to remove
        target = message.content.split(' ')[1]

        # Remove the target from the initiative tracker or status list
        if target in initiative_dict:
            initiative_order.remove(target)
            del initiative_dict[target]
        else:
            response = f'{target} is not in the initiative tracker.'
            await message.channel.send(response)
            return

        # Create the response message
        response = f'{target} has been removed from the initiative tracker.'

        # Send the response message
        await message.channel.send(response)


    # Check if the message starts with "/add"
    elif message.content.startswith('/add'):
        # Get the name and initiative of the combatant to add
        combatant_name = message.content.split(' ')[1]
        combatant_initiative = int(message.content.split(' ')[2])
    
        # Check if the combatant is already in the initiative tracker
        if combatant_name in initiative_dict:
            response = f'{combatant_name} is already in the initiative tracker.'
            await message.channel.send(response)
            return
    
        # Add the combatant to the initiative tracker
        initiative_dict[combatant_name] = combatant_initiative
    
        # Find the index to insert the new combatant
        insert_index = len(initiative_order)
        for i, character in enumerate(initiative_order):
            if combatant_initiative > initiative_dict[character]:
                insert_index = i
                break
        initiative_order.insert(insert_index, combatant_name)
    
        # Create the response message
        response = f'{combatant_name} has been added to the initiative tracker.'
    
        # Send the response message
        await message.channel.send(response)


    # Check if the message starts with "/initorder"
    elif message.content.startswith('/initorder'):
        # Check if there are any characters in the initiative tracker
        if len(initiative_order) == 0:
            response = 'Initiative tracker is empty. Use the /initiative command to start tracking initiative.'
            await message.channel.send(response)
            return
    
        # Rotate the initiative order based on the current turn
        rotated_order = initiative_order[(current_turn - 1) % len(initiative_order):] + initiative_order[:(current_turn - 1) % len(initiative_order)]
    
        # Create the response message
        response = '**Initiative Order:**\n'
        for i in range(len(rotated_order)):
            response += f'{i+1}. {rotated_order[i]} ({initiative_dict[rotated_order[i]]})\n'
        response += f'\nCurrent turn: {initiative_order[(current_turn - 1) % len(initiative_order)]} ({initiative_dict[initiative_order[(current_turn - 1) % len(initiative_order)]]})'
    
        # Send the response message
        await message.channel.send(response)

    # Check if the message starts with "/endcombat"
    elif message.content.startswith('/endcombat'):
        # Check if there are any characters in the initiative tracker
        if len(initiative_order) == 0:
            response = 'Initiative tracker is already empty.'
            await message.channel.send(response)
            return

        # Clear the initiative tracker and status list
        initiative_order = []
        initiative_dict = {}

        # Create the response message
        response = 'The combat encounter has ended. The initiative tracker has been cleared.'

        # Send the response message
        await message.channel.send(response)

    # Check if the message starts with "/srinitiative"
    if message.content.startswith('/srinitiative'):
        # Clear the initiative tracker
        sr_initiative_order = []
        sr_initiative_dict = {}
        sr_current_turn = 0
        
        # Parse the initiative values for each character
        for item in message.content.split()[1:]:
            name, value = item.split('=')
            sr_initiative_dict[name] = int(value)
            
        # Determine initiative order
        sr_initiative_order = sorted(sr_initiative_dict.keys(), key=lambda k: sr_initiative_dict[k], reverse=True)
        
        # Create the response message
        response = 'Initiative order:\n'
        for i, name in enumerate(sr_initiative_order[:4]):
            response += f'{i+1}. {name} ({sr_initiative_dict[name]})\n'
        response += f"It is now {sr_initiative_order[sr_current_turn]}'s turn."
        
        # Send the response message
        await message.channel.send(f'```{response}```')
    
    # Check if the message starts with "/srnext"
    elif message.content.startswith('/srnext'):
        # Advance to the next character in the initiative order
        sr_current_turn += 1
        
        # Check if a new round should be started
        if sr_current_turn >= len(sr_initiative_order):
            # Reduce everyone's initiative by 10
            for name in sr_initiative_dict.keys():
                sr_initiative_dict[name] -= 10
            
            # Remove characters that have initiative scores less than or equal to 0
            sr_initiative_order = [name for name in sr_initiative_order if sr_initiative_dict[name] > 0]
            
            # Determine the new initiative order
            sr_initiative_order = sorted(sr_initiative_order, key=lambda k: sr_initiative_dict[k], reverse=True)
            
            # Reset the current turn index
            sr_current_turn = 0
            
            # Check if the round is over
            if not sr_initiative_order:
                response = 'The round is over. Enter initiative values for each combatant using the format "/srinitiative [name1=X name2=Y ...]".'
                await message.channel.send(response)
                return
        
        # Create the response message
        response = 'Initiative order:\n'
        for i, name in enumerate(sr_initiative_order[:4]):
            response += f'{i+1}. {name} ({sr_initiative_dict[name]})\n'
        response += f"It is now {sr_initiative_order[sr_current_turn]}'s turn."
        
        # Send the response message
        await message.channel.send(f'```{response}```')
    
    # Check if the message starts with "/srnewround"
    elif message.content.startswith('/srnewround'):
        # Clear the initiative tracker and prompt the user for new initiative values
        sr_initiative_order = []
        sr_initiative_dict = {}
        sr_current_turn = 0
    
        # Send the response message
        response = 'Starting a new round of combat. Enter initiative values for each combatant using the format "/srinitiative [name1=X name2=Y ...]".'
        await message.channel.send(response)

    # Check if the message starts with "/sradjust"
    if message.content.startswith('/sradjust'):
        # Get the character name and the initiative adjustment value
        _, name, value = message.content.split()
        value = int(value)
    
        # Check if the character name is in the initiative tracker
        if name.lower() not in [n.lower() for n in sr_initiative_order]:
            response = f"{name} is not in the initiative tracker."
        else:
            # Adjust the character's initiative value
            for k, v in sr_initiative_dict.items():
                if k.lower() == name.lower():
                    sr_initiative_dict[k] += value
                    break
            
            # Determine the new initiative order
            sr_initiative_order = sorted(sr_initiative_dict.keys(), key=lambda k: sr_initiative_dict[k], reverse=True)
    
            # Create the response message
            response = 'Initiative order:\n'
            for i, name in enumerate(sr_initiative_order):
                response += f'{i+1}. {name} ({sr_initiative_dict[name]})\n'
            response += f"It is now {sr_initiative_order[sr_current_turn]}'s turn."
    
        # Send the response message
        await message.channel.send('```' + response + '```')

    # Check if the message starts with "/srendcombat"
    if message.content.startswith('/srendcombat'):
        # Clear the initiative tracker
        sr_initiative_order = []
        sr_initiative_dict = {}
        sr_current_turn = 0
        
        # Create the response message
        response = 'The initiative tracker has been cleared.'
        
        # Send the response message
        await message.channel.send('```' + response + '```')

    # Check if the message starts with "/ai"
    elif message.content.startswith('/ai'):
        # Get the rest of the message as the prompt
        prompt = message.content[4:]

        # Use the OpenAI API to generate a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        # Send the AI's response as a message
        await message.channel.send(response['choices'][0]['message']['content'])

    # Check if the message starts with "/names"
    elif message.content.startswith('/names'):
        # Use a regular expression to extract the genre and subject type from the message
        match = re.match(r'/names \[(.*?)\] (.*)', message.content)

        # If there is no match, send an error message
        if match is None:
            await message.channel.send("Error: The /names command requires two arguments: genre and subject type.")
            return

        # Otherwise, get the genre and subject type from the match
        genre, subject_type = match.groups()

        # Use the OpenAI API to generate a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative assistant that generates content appropriate for the given genre and subject type."},
                {"role": "user", "content": f"I need ten names for a {subject_type} in a {genre} setting. Please include markdown so that the response will be formatted well as a discord message."}
            ],
            temperature=0.75,
            max_tokens=500
        )

        # Send the AI's response as a message
        await message.channel.send(response['choices'][0]['message']['content'])

    # Check if the message starts with "/npc"
    elif message.content.startswith('/npc'):
        # Extract the genre and the npc type
        match = re.match(r'/npc \[(.*?)\] (.*)', message.content)
        if match is None:
            await message.channel.send("Invalid command format. Use: /npc [genre] prompt")
            return

        genre = match.group(1)
        npc_type = match.group(2)

        # Construct the chat message
        chat_message = [
            {"role": "system", "content": f"You are a helpful assistant that's going to generate an NPC description and a physical description for an NPC of type {npc_type} in a {genre} setting."},
            {"role": "user", "content": f"Please provide a detailed character description and a concise physical description for a(n) {npc_type} in a {genre} setting. For the character description, provide a brief overview of their background, personality, and role. For the physical description, be very concise and focus on the most notable features, do not include their name, and format the text for use with an AI image generator tool. Please format your responses as follows:\n\nCharacter Description: [Your response here]\n\nPhysical Description: [Your response here]"}
        ]

        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_message,
            max_tokens=500,
            temperature=0.75
        )
        
        # Get the AI's response
        result = response['choices'][0]['message']['content']

        # Extract the character description and physical description using regex
        match = re.search(r'Character Description: (.*?)\n\nPhysical Description: (.*?)$', result, re.DOTALL)
        if match is None:
            await message.channel.send(f"*The response was formatted incorrectly, so here is the unedited response:*\n\n{result}")
            return

        character_desc, physical_desc = match.groups()

        # Send the character description
        await message.channel.send(f"```Character Description: {character_desc.strip()}```")

        # Send the physical description
        await message.channel.send(f"```/imagine prompt: {physical_desc.strip()}, character portrait, ultra realistic --ar 2:3```")

    # Check if the message starts with "/location"
    elif message.content.startswith('/location'):
        # Use a regular expression to extract the genre and location_info from the message
        match = re.match(r'/location \[(.*?)\] (.*)', message.content)

        # If there is no match, send an error message
        if match is None:
            await message.channel.send("Error: The /location command requires two arguments: genre and location info.")
            return

        # Otherwise, get the genre and location_info from the match
        genre, location_info = match.groups()

        # Use the OpenAI API to generate a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a creative assistant that generates detailed descriptions of fantastic locations suitable for the given genre."},
                {"role": "user", "content": f"I need a description for a location that incorporates {location_info} in a {genre} setting. Please generate a detailed and interesting location and format it using markdown for readability. Be concise. In a new paragraph provide a short but detailed description of an ultra realistic digital painting of the location. Format the response as follows: ```/imagine prompt: [your description], ultra realistic --ar 16:9```"}
            ],
            temperature=0.75,
            max_tokens=500
        )

        # Send the AI's response as a message
        await message.channel.send(response['choices'][0]['message']['content'])


@client.event
async def on_guild_join(guild):
    print(f'Joined new server: {guild.name} ({guild.id})')

my_secret = os.environ['DISCORD_TOKEN']
client.run(my_secret)
