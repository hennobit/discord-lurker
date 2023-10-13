import discord
from database_controller import update_heartbeat, user_exists, insert_user, update_user_data, update_mute_data, update_online_status_time
from logger import log
from discord.ext import tasks

# create intents allowing the bot to see members and their statuses
intents = discord.Intents.default()
intents.presences = True
intents.members = True

client = discord.Client(intents=intents)

SCAN_SERVER_INTERVAL = 5
initial_scan = True

# Funktion zum Scannen des Servers und Aktualisieren der Benutzerdaten. insert bzw. update muss hier einmal ausgeführt werden.
@tasks.loop(seconds=SCAN_SERVER_INTERVAL)
async def scan_server():
    global initial_scan
    for guild in client.guilds:
        for member in guild.members:
            if not user_exists(member.id, member.guild.id):
                insert_user(
                    member)
            else:
                voice_channel = member.voice.channel if member.voice else None
                update_user_data(
                    member=member, before=voice_channel, after=voice_channel, update_join_time=False, initial_scan=initial_scan)

    log('Server scan completed')
    initial_scan = False
    update_heartbeat()

@client.event
async def on_ready():
    log(f"{client.user.name} is ready")
    scan_server.start()

@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None:
        log(f'{member} joined {after.channel.name} on {member.guild.name}')
        # Sollte immer getriggert werden, sobald jemand dem Discord joint. Deswegen nur hier prüfen ob der Benutzer schon in der Datenbank ist
        if not user_exists(member.id, member.guild.id):
            insert_user(member, after.channel)
        else:
            update_user_data(
                member, before=before.channel, after=after.channel)
        return

    if after.channel is None:
        log(f'{member} left {before.channel.name} and {member.guild.name}')
        update_user_data(member, before=before.channel, after=after.channel)
        return

    if before.channel != after.channel:
        log(f'{member} moved from {before.channel.name} to {after.channel.name}')
        update_user_data(member, before=before.channel, after=after.channel)
        return

    if before.self_deaf != after.self_deaf:
        if before.self_deaf:
            log(f'{member} sound unmuted themselves')
        elif after.self_deaf:
            log(f'{member} sound muted themselves')
        update_mute_data(member, before, after)
        return

    if before.self_mute != after.self_mute:
        if before.self_mute:
            log(f'{member} unmuted themselves')
        elif after.self_mute:
            log(f'{member} muted themselves')
        update_mute_data(member, before, after)
        return


@client.event
async def on_member_update(before, after):
    if str(before.status) != str(after.status):
        update_online_status_time(before=before, after=after)

with open('dc_api_key.txt', 'r') as f:
    api_key = f.read().strip()
    
client.run(api_key)
