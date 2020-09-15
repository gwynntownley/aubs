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


hello_messages = [
    "Hi %s, my name is Aubbie !",
    "It's a pleasure to meet you, %s. I'm Aubbie !",
    "Hello, %s ! It's a pleasure to meet you."]

hello_commands = [
    "!hi", "!hello", "!hey", "!hoi", "!heyo",
    "!howdy", "!hiya", "!hola", "!bonjour", "!heya"]

bye_messages = [
    "See you again soon, %s !",
    "Goodbye, %s ! Thank you for spending time with me.",
    "Bye-bye, %s ! We'll meet again, I just know it !"]
                

bye_commands = [
    "!bye", "!goodbye", "!see ya", "!adios", "!bye-bye"]
    
stamps = [
    "Worm", "Bow Worm", "Save the Spiders",
    "Ants Unite", "Bees Unite", "Beetles Unite",
    "Butterflies Unite", "Crickets Unite", "Moths Unite",
    "Snails Unite", "Wasps Unite", "Dragon"
    
]

beans = [
    "Red Bean", "Orange Bean", "Yellow Bean",
    "Green Bean", "Blue Bean", "Violet Bean"
    ]

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
            if not "characters" in list(player):
                currencydb.update_one({"userid" : player["userid"]},{"$set":{"characters" : []}})
            if not "stamps" in list(player):
                currencydb.update_one({"userid" : player["userid"]},{"$set":{"stamps" : []}})
            if not "links" in list(player):
                currencydb.update_one({"userid" : player["userid"]},{"$set":{"links" : []}})
            if not "carrd" in list(player):
                currencydb.update_one({"userid" : player["userid"]},{"$set":{"carrd" : ""}})
            if not "beans" in list(player):
                currencydb.update_one({"userid" : player["userid"]},{"$set":{"beans" : ""}})
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
                "carrd" : "",
                "links" : [],
                # currency
                "goldleaves": 0,
                "silverleaves": 5,
                "bronzeleaves" : 0,
                # characters
                "character_slots" : 2,
                "characters" : [],
                # collectibles
                "stamps" : [],
                "beans" : {},
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
                
                bean_count = 0
                for i in player["beans"]:
                    checker = False
                    if player["beans"][i]["type"] == "Red Bean":
                        bean_count += 1
                        checker = True
                    if checker == True:
                        break
                for i in player["beans"]:
                    checker = False
                    if player["beans"][i]["type"] == "Orange Bean":
                        bean_count += 1
                        checker = True
                    if checker == True:
                        break
                for i in player["beans"]:
                    checker = False
                    if player["beans"][i]["type"] == "Yellow Bean":
                        bean_count += 1
                        checker = True
                    if checker == True:
                        break
                for i in player["beans"]:
                    checker = False
                    if player["beans"][i]["type"] == "Green Bean":
                        bean_count += 1
                        checker = True
                    if checker == True:
                        break
                for i in player["beans"]:
                    checker = False
                    if player["beans"][i]["type"] == "Blue Bean":
                        bean_count += 1
                        checker = True
                    if checker == True:
                        break
                for i in player["beans"]:
                    checker = False
                    if player["beans"][i]["type"] == "Violet Bean":
                        bean_count += 1
                        checker = True
                    if checker == True:
                        break
                await message.channel.send("""

=== %s ===

= Currency =

Goldleaves : %d g
Silverleaves : %d s
Bronzeleaves : %d b

= Creations =

Characters : %s

= Collections =

Stamps : %d / %d

Beans : %s / %d""" % (player["username"], player["goldleaves"], player["silverleaves"], player["bronzeleaves"], ",".join(player["characters"]), len(player['stamps']), len(stamps), bean_count, len(beans)))

                if not player["carrd"] == "" or len(player["links"]) > 0:
                    await message.channel.send("= Social =")
                    if not player["carrd"] == "":
                        await message.channel.send("Carrd : %s" % player["carrd"])
                    if len(player["links"]) > 0:
                        await message.channel.send("Links -")
                        for i in player["links"]:
                            await message.channel.send(i)
        elif message.content == "!daily":
            today = date.today()
            if player == None:
                await message.channel.send("%s, it seems you haven't yet made an account. Please do so with !register." % (message.author.name))
            elif not "daily" in list(player) or player["daily"] < today.strftime("%d"):
                currencydb.update_one({"userid" : player["userid"]},{"$set":{"daily" : today.strftime("%d"), "silverleaves" : player["silverleaves"] + 1}})            
                await message.channel.send("1 silverleaf has been added to your account, %s. Enjoy, and please come back tomorrow for another reward !" % (player["username"]))
            else:
                await message.channel.send("Sorry, %s, but it seems you've already collected your daily silverleaf !" % (message.author.name))
        elif message.content[:3] == "!p ":
            await message.channel.send(message.content[2:])
            print(message.content[3:])
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
              
        elif message.content == "!stamps":
            if message.channel.name == "post-office-game" and not player == None:
                valid = True
                
                temp_bronze = player['bronzeleaves']
                
                temp_silver = player['silverleaves']
                
                temp_gold = player['goldleaves']
                
                temp_stamps = player['stamps']
                
                if player['bronzeleaves'] >= 3:
                    temp_bronze -= 3
                elif player['silverleaves'] > 0:
                    temp_silver -= 1
                    temp_bronze += 7
                elif player['goldleaves'] > 0:
                    temp_gold -= 1
                    temp_silver += 9
                    temp_bronze += 7
                else:
                    valid = False
                
                if valid == True:
                    await message.channel.send("Here's your stamp, %s. Enjoy !" % player['username'])
                    new_stamp = (random.choice(stamps))
                    if not new_stamp in player['stamps']:
                        temp_stamps.append(new_stamp)
                    await message.channel.send(file=discord.File('stamps/%s.png' % new_stamp))
                    await message.channel.send("You spent three bronzeleaves.")
                    currencydb.update_one({"userid" : player['userid']},{"$set":{'bronzeleaves' : temp_bronze, 'silverleaves' : temp_silver, 'goldleaves' : temp_gold, 'stamps' : temp_stamps}})
                else:
                    await message.channel.send("You do not have enough leaves ! It costs three bronzeleaves to spin for a stamp.")
                    
            elif player == None:
                await message.channel.send("%s, it seems you haven't yet made an account. Please do so with !register." % (message.author.name))
            else:
              await message.channel.send("Sorry, %s, but you can only spin for a stamp in the Post Office ! Please try again in #post-office-game. " % (player["username"]))
        elif message.content == "!collections stamp":
            if not player == None:
                for i in stamps:
                    if i in player['stamps']:
                        await message.channel.send("%s - ✅" % i)
                    else:
                        await message.channel.send("%s - ❌" % i)
            else:
                await message.channel.send("%s, it seems you haven't yet made an account. Please do so with !register." % (message.author.name))
        elif message.content == "!help":
            await message.channel.send("""
**Registration Commands**

Please do this in #registration only !

!register - create your 'currency' account. your username will be your display name, so dm @gwynn if you would like a different name !

!mail register - register your account with the AUBS Postal Service. Requires an AUBS account.

!character create - create a character under your account. Requires an AUBS account

**Currency Commands**

!view [username] - display one's account information. if the username field is left blank, the message author's account will be displayed.

!daily - collect your daily silverleaf !

!pay [user] [amount][type of currency : b, s, or g] - transfer some of your leaves to another account

**Character Commands**

!character view [name] - view the bio of a certain character

**Post Office Commands**

!mail inbox - view your inbox

!mail view [id] - read a specific message

!mail delete [id] - delete a specific message

!mail send - sends a custom message

!stamp - spin for a stamp

**Brightwing Cafe Commands**

!beans - lists all your beans. if you don't have any beans, you will get your first one for free

!beans [id] - view a specific bean, and harvest/grind if you are able to

!beans plant [id] - plant an unplanted bean

**Test / Update Commands (use these if the other commands aren't working)**

!p - make Aubbie repeat what you say

!hello - say hi to Aubbie !

!bye - say bye to Aubbie !
            """)
        elif message.content[:4] == "!pay":
            if player == None:
                await message.channel.send("%s, it seems you haven't yet made an account. Please do so with !register." % (message.author.name))
            else:
                payment = message.content.split()
                target = currencydb.find_one({"username": payment[1]})
                if target == None:
                    await message.channel.send("We couldn't find a user under the name '%s' in our database." % message.content[5:])
                amount = int(payment[2][:-1])
                method = payment[2][-1:]
                
                if method == "g":
                    method = "goldleaves"
                elif method == "s":
                    method = "silverleaves"
                else:
                    method = "bronzeleaves"
                
                bal = target[method]
                
                bal += amount
                
                sub = player[method]
                
                sub -= amount
                
                currencydb.update_one({"username" : target["username"]},{"$set":{method : bal}})
                
                currencydb.update_one({"userid" : player["userid"]},{"$set":{method : sub}})
                
                await message.channel.send("%d %s was taken from your account, and added to %s's." % (amount, method, target["username"]))
        elif message.content[:9] == "!link add":  
            if player == None:
                await message.channel.send("%s, it seems you haven't yet made an account. Please do so with !register." % (message.author.name))
            else:
                links = player["links"]
                if "carrd" in message.content:
                    currencydb.update_one({"userid" : player["userid"]},{"$set":{"carrd" : message.content[10:]}})
                    await message.channel.send("Your carrd has been registered as : %s." % (message.content[10:]))
                else:
                    links.append(message.content[10:])
                    currencydb.update_one({"userid" : player["userid"]},{"$set":{"links" : links}})
                    
                    await message.channel.send("The following has been linked to your account : %s." % (message.content[10:]))
        elif message.content[:12] == "!link remove":  
            if player == None:
                await message.channel.send("%s, it seems you haven't yet made an account. Please do so with !register." % (message.author.name))
            else:
                links = player["links"]
                if "carrd" in message.content:
                    currencydb.update_one({"userid" : player["userid"]},{"$set":{"carrd" : ""}})
                    await message.channel.send("Your carrd has been removed." % (message.content[13:]))
                else:
                    links.remove(message.content[13:])
                    currencydb.update_one({"userid" : player["userid"]},{"$set":{"links" : links}})
                    
                    await message.channel.send("The following link has been removed from your account : %s." % (message.content[13:]))
        elif message.content == "!beans":
            if player == None:
                await message.channel.send("%s, it seems you haven't yet made an account. Please do so with !register." % (message.author.name))
            elif not message.channel.name == "brightwing-cafe-game":
                await message.channel.send("Sorry, %s, but you can only tend to your beans in the Brightwing Cafe greenhouse ! Please try again in #brightwing-cafe-game. " % (player["username"]))

            elif len(player["beans"]) < 1:
                new_bean = (random.choice(beans))
                        
                bean_code = str((random.randint(0,9)))
                for i in range(10):
                    bean_code = bean_code + str((random.randint(0,9)))
                                
                await message.channel.send(file=discord.File('beans/%s.png' % new_bean))
                await message.channel.send("Your free bean is %s . This is your last free bean - from now on, you will have to grow more yourself." % new_bean)
                currencydb.update_one({"userid" : player["userid"]},{"$set":{"beans" : {str(bean_code) : {"type" : new_bean, "stage" : -1}}}})
            else:
                await message.channel.send("= Unplanted Beans =")
                for i in list(player["beans"]):
                    if player["beans"][i]["stage"] == -1:
                        await message.channel.send("[%d] %s" % (list(player["beans"]).index(i), player["beans"][i]["type"]))
                await message.channel.send("= Planted Beans =")
                for i in list(player["beans"]):
                    if player["beans"][i]["stage"] > -1:
                        await message.channel.send("[%d] %s" % (list(player["beans"]).index(i), player["beans"][i]["type"]))
        elif message.content[:6] == "!beans":
            def check(m):
                return m.channel == message.channel and m.author.id == player["userid"]
            if player == None:
                await message.channel.send("%s, it seems you haven't yet made an account. Please do so with !register." % (message.author.name))
            elif not message.channel.name == "brightwing-cafe-game":
                await message.channel.send("Sorry, %s, but you can only tend to your beans in the Brightwing Cafe greenhouse ! Please try again in #brightwing-cafe-game. " % (player["username"]))
            else:
                target = list(player["beans"])[int(message.content[7:])]
                today = date.today()

                temp_beans = player["beans"]

                if player["beans"][target]["stage"] == -1:
                    await message.channel.send(file=discord.File('beans/%s.png' % player["beans"][target]["type"]))
                    
                    await message.channel.send("Your %s can be ground into coffee ! Please reply 'grind' to make some coffee !" % player["beans"][target]["type"])
                    grind = await client.wait_for('message', check=check)
                    grind = grind.content
                    
                    if grind == "grind":
                        
                        await message.channel.send(file=discord.File('beans/coffee_%s.png' % player["beans"][target]["type"]))

                        del temp_beans[target]
                        
                        await message.channel.send("You have made a cup of coffee ! The cafe will collect your coffee in exchange for 5 bronzeleaves.")
                        
                        currencydb.update_one({"userid" : player["userid"]},{"$set":{"beans" : temp_beans, "bronzeleaves" : player["bronzeleaves"] + 5}}) 
                        
                if not player["beans"][target]["date"] == today.strftime("%d"):
                    temp_beans[target]["stage"] += 1
                    temp_beans[target]["date"] = today.strftime("%d")


                if player["beans"][target]["stage"] == 0:
                    await message.channel.send(file=discord.File('beans/day_0.png'))
                elif player["beans"][target]["stage"] == 1:
                    await message.channel.send(file=discord.File('beans/day_1.png'))
                elif player["beans"][target]["stage"] == 2:
                    rando = (random.randint(1, 10))
                    if rando == 9:
                        if player["beans"][target]["type"] == "Red Bean":
                            player["beans"][target]["type"] = "Violet Bean"
                        elif player["beans"][target]["type"] == "Orange Bean":
                            player["beans"][target]["type"] = "Red Bean"
                        elif player["beans"][target]["type"] == "Yellow Bean":
                            player["beans"][target]["type"] = "Orange Bean"
                        elif player["beans"][target]["type"] == "Green Bean":
                            player["beans"][target]["type"] = "Yellow Bean"
                        elif player["beans"][target]["type"] == "Blue Bean":
                            player["beans"][target]["type"] = "Green Bean"
                        else:
                            player["beans"][target]["type"] = "Blue Bean"
                    elif rando == 10:
                        if player["beans"][target]["type"] == "Red Bean":
                            player["beans"][target]["type"] = "Orange Bean"
                        elif player["beans"][target]["type"] == "Orange Bean":
                            player["beans"][target]["type"] = "Yellow Bean"
                        elif player["beans"][target]["type"] == "Yellow Bean":
                            player["beans"][target]["type"] = "Green Bean"
                        elif player["beans"][target]["type"] == "Green Bean":
                            player["beans"][target]["type"] = "Blue Bean"
                        elif player["beans"][target]["type"] == "Blue Bean":
                            player["beans"][target]["type"] = "Violet Bean"
                        else:
                            player["beans"][target]["type"] = "Red Bean"
                                
                    await message.channel.send(file=discord.File('beans/day_2_%s.png' % player["beans"][target]["type"]))
                    
                elif player["beans"][target]["stage"] == 3:

                    await message.channel.send(file=discord.File('beans/day_3_%s.png' % player["beans"][target]["type"]))
                    await message.channel.send("Your %s is ready to harvest ! Please reply 'harvest' to claim your beans !" % player["beans"][target]["type"])
                    harvest = await client.wait_for('message', check=check)
                    harvest = harvest.content
                    
                    if harvest == "harvest":
                        
                        for i in range((random.randint(2,4))):
                        
                            bean_code = str((random.randint(0,9)))
                            for i in range(10):
                                bean_code = bean_code + str((random.randint(0,9)))
                                
                            temp_beans[str(bean_code)] = {"stage" : -1, "type" : player["beans"][target]["type"]}
                            
                        del temp_beans[target]
                        
                        await message.channel.send("Congrats on a successful harvest !")

                currencydb.update_one({"userid" : player["userid"]},{"$set":{"beans" : temp_beans}})
                    
        elif message.content[:12] == "!beans plant":
            target = list(player["beans"])[int(message.content[13:])]
            today = date.today()
            if player == None:
                await message.channel.send("%s, it seems you haven't yet made an account. Please do so with !register." % (message.author.name))
            elif not message.channel.name == "brightwing-cafe-game":
                await message.channel.send("Sorry, %s, but you can only tend to your beans in the Brightwing Cafe greenhouse ! Please try again in #brightwing-cafe-game. " % (player["username"]))
            elif player["beans"][target]["stage"] > -1:
                await message.channel.send("It seems this bean has already been planted !")
            else:
                temp_beans = player["beans"]
                temp_beans[target]["stage"] = 0
                temp_beans[target]["date"] = today.strftime("%d")
                currencydb.update_one({"userid" : player["userid"]},{"$set":{"beans" : temp_beans}})
                await message.channel.send("Your %s has been planted!" % player["beans"][target]["type"])
                    
                
client.run(TOKEN)
