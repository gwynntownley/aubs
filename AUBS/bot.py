# bot.py
import os

import discord
import ctx

from dotenv import load_dotenv

from discord.ext import commands
from discord.ext.commands import has_role
from discord import Member
from discord.utils import get

from pymongo import MongoClient

import random
from datetime import date

import traceback


hello_messages = ["Hi %s, my name is Aubbie !",
                  "It's a pleasure to meet you, %s. I'm Aubbie !",
                  "Hello, %s ! It's a pleasure to meet you."]

hello_commands = ["!hi", "!hello", "!hey", "!hoi", "!heyo",
                  "!howdy", "!hiya", "!hola", "!bonjour", "!heya"]

bye_messages = ["See you again soon, %s !",
                "Goodbye, %s ! Thank you for spending time with me.",
                "Bye-bye, %s ! We'll meet again, I just know it !"]

bye_commands = ["!bye", "!goodbye", "!see ya", "!adios", "!bye-bye"]

load_dotenv()

TOKEN = os.environ.get('DISCORD_TOKEN')
GUILD = os.environ.get('DISCORD_GUILD')

client = discord.Client()

cluster = MongoClient('mongodb+srv://gwynn:W0lf10293@aubs.jpd87.mongodb.net/<dbname>?retryWrites=true&w=majority')

db = cluster.aubs

currencydb = db.currency

characterdb = db.characters

postaldb = db.postal

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        player = currencydb.find_one({"userid": message.author.id})
        if not player == None:
            if not "character_slots" in list(player):
                currencydb.update_one({"userid" : player["userid"]},{"$set":{"character_slots" : 2}})
            if not "characters" in list(player):
                currencydb.update_one({"userid" : player["userid"]},{"$set":{"characters" : []}})
        username = message.author.name
        if message.content in hello_commands:
            await message.channel.send(random.choice(hello_messages) % username)
        elif message.content in bye_commands:
            await message.channel.send(random.choice(bye_messages) % username)
        elif message.content == "!register":
            if player == None:
                author = {
                # player info
                "username": message.author.name,
                "userid": message.author.id,
                # currency
                "goldleaves": 0,
                "silverleaves": 5,
                "bronzeleaves" : 0,
                # characters
                "character_slots" : 2,
                "characters" : []
                    }
                
                currencydb.insert_one(author).inserted_id

                await message.channel.send("Welcome to the game, %s ! %s silverleaves have automatically been added to your account." % (author["username"], author["silverleaves"]))
            else:
                await message.channel.send("%s, it seems you already have an account. If you wish to start over, please contact @gwynn, the game admin." % (player["username"]))
        elif message.content == "!character create":
            creator = message.author.name
            if player == None:
                await message.channel.send("%s, it seems you haven't yet made an account. Please do so with !register." % (message.author.name))
            elif len(player["characters"]) == player["character_slots"]:
                await message.channel.send("%s, it seems you've reached the maximum number of character slots !" % (player["username"]))
            else:
                await message.channel.send("What will your character's name be ? Just the first name - bugs don't commonly have surnames.")

                def check(m):
                    return m.channel == message.channel and m.author.id == player["userid"]

                name = await client.wait_for('message', check=check)

                name = name.content

                validname = characterdb.find_one({"name" : name})

                while not validname == None:
                    await message.channel.send("Unfortunately, it seems that name has already been taken. Try again !")
                    
                    name = await client.wait_for('message', check=check)

                stop = False

                pronouns = []

                while stop == False:

                    await message.channel.send("Next, what about your character's pronouns ? You may enter as many as you'd like - reply 'stop' when you are ready to move on.")
                    pronoun = await client.wait_for('message', check=check)
                    pronoun = pronoun.content
                    
                    if pronoun == "stop":
                        stop = True
                    else:
                                                        
                        pronouns.append(pronoun)

                await message.channel.send("""
A bug's species is a very important aspect to their identity. Please enter your character's species, in lowercase and without superfluous characters.

The following available species are as follows :

- Ant
- Cricket
- Bee
- Wasp
- Snail
- Moth
- Butterfly
- Beetle
- Bird
- Rodent""")

                valid_species = ["ant", "cricket", "bee", "wasp", "snail", "moth", "butterfly", "beetle", "bird", "rodent"]
                                 
                def check(m):
                    return m.channel == message.channel and m.author.id == player["userid"] and m.content in valid_species

                species = await client.wait_for('message', check=check)
                species = species.content

                await message.channel.send("Now, what about your character's subspecies ? It can be any you'd like, as long as it falls under your character's species. For example, Monarch for a butterfly character, darkling for a beetle, etc.")

                def check(m):
                    return m.channel == message.channel and m.author.id == player["userid"]

                subspecies = await client.wait_for('message', check=check)
                subspecies = subspecies.content

                await message.channel.send("""
Finally, your bug must be a contributing member of the community in some way. Naturally, that means selecting a career path.

The following available careers are as follows :

- Postbug (Post Office)
- Barista (Brightwing Cafe)
- Librarian (Brightwing Library)
- Gardener (Dauber Park)
- Teacher (Arachnid Academy)
- Larvaesitter (Charlotte's Nursery)
- Cook (Redleg Diner)
- Artist (Art Museum)""")

                valid_jobs = ["postbug", "barista", "librarian", "gardener", "teacher", "larvaesitter", "cook", "artist"]
                                 
                def check(m):
                    return m.channel == message.channel and m.author.id == player["userid"] and m.content in valid_jobs

                job = await client.wait_for('message', check=check)
                job = job.content

                temp_list = player["characters"]

                temp_list.append(name)

                currencydb.update_one({"userid" : player["userid"]},{"$set":{"characters" : temp_list}})

                await message.channel.send("Your character, %s the %s %s, has been registered. You can view them using the !character view [name] command." % (name, species, job))

                new_char = {
                # creator
                    "creator" : player,
                # identity
                    "name" : name,
                    "pronouns" : pronouns,
                # description
                    "species" : species,
                    "subspecies" : subspecies,
                # career
                    "career" : job
                    }

                characterdb.insert_one(new_char).inserted_id

        elif message.content[:15] == "!character view":
            character = characterdb.find_one({"name" : message.content[16:]})
            if character == None:
                await message.channel.send("We weren't able to find a character under that name !")
            else:
                await message.channel.send("""

=== %s ===

Pronouns : %s

Species : %s
Subspecies : %s

Career : %s

Creator : %s""" % (character["name"], ",".join(character["pronouns"]), character["species"], character["subspecies"], character["career"], character["creator"]["username"]))
                
        elif message.content[:5] == "!view":
            if not message.content[6:] == "":
                player = currencydb.find_one({"username" : message.content[6:]})
            if player == None:
                await message.channel.send("It seems that user doesn't have an account yet. They can make one with !register !")
            else:
                await message.channel.send("""

=== %s ===

Goldleaves : %d g
Silverleaves : %d s
Bronzeleaves : %d b

Characters : %s""" % (player["username"], player["goldleaves"], player["silverleaves"], player["bronzeleaves"], ",".join(player["characters"])))

        elif message.content == "!daily":
            today = date.today()
            if player == None:
                await message.channel.send("%s, it seems you haven't yet made an account. Please do so with !register." % (message.author.name))
            elif not "daily" in list(player) or player["daily"] < today.strftime("%d"):
                currencydb.update_one({"userid" : player["userid"]},{"$set":{"daily" : today.strftime("%d"), "silverleaves" : player["silverleaves"] + 1}})            
                await message.channel.send("1 silverleaf has been added to your account, %s. Enjoy, and please come back tomorrow for another reward !" % (player["username"]))
            else:
                await message.channel.send("Sorry, %s, but it seems you've already collected your daily silverleaf !" % (message.author.name))
        elif message.content[:2] == "!p":
            await message.channel.send(message.content[2:])
            print(message.content[2:])
        elif message.content == "!mail register":
            account = postaldb.find_one({"userid": message.author.id})
            if account == None:
                def check(m):
                    return m.channel == message.channel and m.author.id == player["userid"]
                await message.channel.send("Before we register your account, a couple questions. First, would you like to receieve notifications for new updates and features to AUBS ? [Y/N]")
                feat_toggle = await client.wait_for('message', check=check)
                feat_toggle = feat_toggle.content
                await message.channel.send("Next and final question : would you also like notifications when other players interact with your account ? Such as purchasing one of your items or interacting with one of your characters? [Y/N]")
                inte_toggle = await client.wait_for('message', check=check)
                inte_toggle = inte_toggle.content
                account = {
                # player info
                "username": message.author.name,
                "userid": message.author.id,
                # settings
                'features' : feat_toggle,
                'interaction' : inte_toggle,
                # inbox
                'inbox_messages' : {
                    'AUBS Postal Service' : "Dear valued patron, br/ Thank you for putting your mail in our hands. We hope we will make you proud with our diligence and dedication. br/ Best, br/ Your Local Postal Service"
                }
                    }
                
                postaldb.insert_one(account).inserted_id

                await message.channel.send("You have successfully registered with the AUBS postal service.")
            else:
              await message.channel.send("It seems you've already registered with the AUBS postal service.")
        elif message.content == "!mail inbox":
            account = postaldb.find_one({"userid": message.author.id})
            if not account == None:
                id = 1
                for i in list(account['inbox_messages']):
                    await message.channel.send("[%d] : %s" % (id, i))
                if len(list(account['inbox_messages'])) == 0:
                    await message.channel.send("There are no new messages in your inbox.")
                id += 1
            else:
              await message.channel.send("It seems you haven't registered with the AUBS postal service, %s. You can do so with !mail register !" % (message.author))
        elif message.content[:10] == "!mail view":
            account = postaldb.find_one({"userid": message.author.id})
            if not account == None:
                sender = list(account['inbox_messages'])[int(message.content[11:]) - 1]
                await message.channel.send("From : %s" % (sender))
                await message.channel.send(i)
                
            else:
              await message.channel.send("It seems you haven't registered with the AUBS postal service, %s. You can do so with !mail register !" % (message.author))
        elif message.content[:12] == "!mail delete":
            account = postaldb.find_one({"userid": message.author.id})
            if not account == None:
                temp_inbox = account['inbox_messages']
                sender = list(account['inbox_messages'])[int(message.content[13:]) - 1]
                del(temp_inbox[sender])
                await message.channel.send("You have deleted a letter from %s." % (sender))
                postaldb.update_one({"userid" : player["userid"]},{"$set":{'inbox_messages' : temp_inbox}})
            else:
              await message.channel.send("It seems you haven't registered with the AUBS postal service, %s. You can do so with !mail register !" % (message.author))
        elif message.content == "!mail send":
            account = currencydb.find_one({"userid": message.author.id})
            if not account == None and message.channel.name == "post-office-game":
                def check(m):
                    return m.channel == message.channel and m.author.id == player["userid"]

                id = 1
                for i in account['characters']:
                    await message.channel.send("[%d] : %s" % (id, i))
                    id += 1
                    
                await message.channel.send("Who will be the sender of this message ?")
                sender = await client.wait_for('message', check=check)
                sender = account['characters'][int(sender.content) - 1]
                
                await message.channel.send("Who will be the receiver of this message ?")
                receiver = await client.wait_for('message', check=check)
                receiver = characterdb.find_one({"name" : receiver.content})
                
                while receiver == None:
                    await message.channel.send("Who will be the receiver of this message ?")
                    receiver = await client.wait_for('message', check=check)
                    receiver = characterdb.find_one({"name" : receiver.content})
                
                owner = postaldb.find_one({"username" : receiver['creator']['username']})
                
                if owner == None:
                    await message.channel.send("Unfortunately, %s's owner hasn't yet registered with the AUBS postal service ! They may do so with !mail register." % receiver['name'])
                    
                else:
                
                    await message.channel.send("What will the content of the message be ?")
                    body = await client.wait_for('message', check=check)
                    body = body.content

                    temp_inbox = owner['inbox_messages']
                    temp_inbox[sender] = body
                    
                    postaldb.update_one({"username" : owner['username']},{"$set":{'inbox_messages' : temp_inbox}})
                    
                    await message.channel.send("%s's message has been sent to %s !" % (sender, receiver['name']))
                
            elif account == None:
              await message.channel.send("It seems you haven't registered with the AUBS postal service, %s. You can do so with !mail register !" % (message.author))
            else:
              await message.channel.send("Sorry, %s, but you can only write & send letters in the Post Office ! Please try again in #post-office-game. " % (account["username"]))

client.run(TOKEN)

