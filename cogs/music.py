import pomice
import datetime
import asyncio
from contextlib import suppress
import settings
from nextcord.ext import commands
import nextcord
import math
import random

class MusicButton(nextcord.ui.View):
    def __init__(self,bot):
        self.bot = bot
        super().__init__(timeout=None)

    @nextcord.ui.button(
        label=' ⏯ ', 
        style=nextcord.ButtonStyle.green,
        custom_id="pause_stop",
        row=0)
    async def pause_stop_button(self, button: nextcord.ui.Button, interaction : nextcord.Interaction):
        await Music.handle_click(self,button, interaction)
    
    
    @nextcord.ui.button(
        label =" ⏭ ",
        style=nextcord.ButtonStyle.secondary,
        custom_id="skip_song",
        row=0)
    async def skip_button(self , button : nextcord.ui.Button, interaction: nextcord.Interaction):
        await Music.handle_click(self,button, interaction)

    @nextcord.ui.button(
        label =" ⏹ ",
        style=nextcord.ButtonStyle.red,
        custom_id="stop_song",
        row=0)
    async def stop_button(self , button : nextcord.ui.Button, interaction: nextcord.Interaction):
        await Music.handle_click(self,button, interaction)
    @nextcord.ui.button(
        label=" 🔂 ",
        style=nextcord.ButtonStyle.secondary ,
        custom_id="repeat_song",
        row=0)
    async def repeat_button(self , button : nextcord.ui.Button, interaction: nextcord.Interaction):
        await Music.handle_click(self,button, interaction)

    @nextcord.ui.button(
        label=" 🔁 ",
        style=nextcord.ButtonStyle.secondary ,
        custom_id="loop_playlist",
        row=0)
    async def loop_button(self , button : nextcord.ui.Button, interaction: nextcord.Interaction):
        await Music.handle_click(self,button, interaction)

    @nextcord.ui.button(
        label=" 🔊 เพิ่มเสียง ",
        style=nextcord.ButtonStyle.primary ,
        custom_id="increase_volume",
        row=1)
    async def vol_up_btn(self , button : nextcord.ui.Button, interaction: nextcord.Interaction):
        await Music.handle_click(self,button, interaction)

    @nextcord.ui.button(
        label=" 🔈 ลดเสียง ",
        style=nextcord.ButtonStyle.primary ,
        custom_id="decrease_volume",
        row=1)
    async def vol_down_btn(self , button : nextcord.ui.Button, interaction: nextcord.Interaction):
        await Music.handle_click(self,button, interaction)

    @nextcord.ui.button(
        label=" 🔇 เปิด/ปิดเสียง ",
        style=nextcord.ButtonStyle.primary ,
        custom_id="mute_unmute_volume",
        row=1)
    async def vol_mute_btn(self , button : nextcord.ui.Button, interaction: nextcord.Interaction):
        await Music.handle_click(self,button, interaction)

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.pomice = pomice.NodePool()
        bot.loop.create_task(self.start_nodes())
    
    async def setnewserver(self,ctx):
        newserver = {"guild_id":ctx.guild.id,
                    "welcome_id":"None",
                    "leave_id":"None",
                    "webhook_url":"None",
                    "webhook_channel_id":"None",
                    "webhook_status":"None",
                    "introduce_channel_id":"None",
                    "introduce_frame":"None",
                    "introduce_role_give_id":"None",
                    "introduce_role_remove_id":"None",
                    "introduce_status":"YES",
                    "level_system":"NO",
                    "economy_system":"NO",
                    "currency":"$",
                    "verification_system":"NO",
                    "verification_time":10,
                    "verification_channel_id":"None",
                    "verification_role_give_id":"None",
                    "verification_role_remove_id":"None",
                    "log_voice_system":"NO",
                    "log_delete_system":"NO",
                    "log_name_system":"NO",
                    "log_channel_id":"None",
                    "scam":"warn",
                    "Music_channel_id":"None",
                    "Embed_message_id":"None",
                    "Music_message_id":"None"
                    }
        return newserver

    async def start_nodes(self):
        await self.bot.wait_until_ready()
        await self.pomice.create_node(
            bot=self.bot,
            host=settings.lavalinkip,
            port=settings.lavalinkport,
            password=settings.lavalinkpass,
            identifier=settings.lavalinkindentifier,
            region=settings.lavalinkregion
        )
        print(f"Node is ready!")

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: pomice.player, track , _):
        await Music.do_next(self,player)

    @commands.Cog.listener()
    async def on_pomice_track_stuck(self, player: pomice.player , track , _):
        await Music.do_next(self,player)

    @commands.Cog.listener()
    async def on_pomice_track_exception(self, player: pomice.player, track , _):
        await Music.do_next(self,player)
    
    async def do_next(self,player : pomice.player):
        data = await settings.collection.find_one({"guild_id":player.guild.id})
        message = await self.bot.get_channel(data["Music_channel_id"]).fetch_message(data["Embed_message_id"])
        server = await settings.collectionmusic.find_one({"guild_id":player.guild.id})
        if server["Mode"] == "Default":
            await settings.collectionmusic.update_one({"guild_id": player.guild.id}, {'$pop': {'Queue': -1}})
            server = await settings.collectionmusic.find_one({"guild_id":player.guild.id})
            if server["Queue"] == []:
                await settings.collectionmusic.delete_one({"guild_id": player.guild.id})
                embed=nextcord.Embed(description="[❯ Invite](https://smilewinnextcord-th.web.app/invitebot.html) | [❯ Website](https://smilewinnextcord-th.web.app) | [❯ Support](https://nextcord.com/invite/R8RYXyB4Cg)",
                                colour = 0xffff00)
                embed.set_author(name="❌ ไม่มีเพลงที่เล่นอยู่ ณ ตอนนี้", icon_url=self.bot.user.avatar.url)
                embed.set_image(url ="https://i.imgur.com/XwFF4l6.png")
                embed.set_footer(text=f"server : {player.guild.name}")
                await message.edit(content="__รายการเพลง:__\n🎵 ไม่มีเพลงที่กำลังเล่นในขณะนี้ ",embed=embed)
            else:
                list_song = [] 
                num = 1
                for song in server["Queue"]:
                    list_song.append(f"> [{num}] " + song["song_title"] + "\n")
                    num = num +1
                list_song = "".join(list_song)
                tracks = await self.pomice._nodes[settings.lavalinkindentifier].build_track(server["Queue"][0]["song_id"])
                nu = "None" if len(server["Queue"]) == 1 else server["Queue"][1]["song_title"]
                embed=nextcord.Embed(description="[❯ Invite](https://smilewinnextcord-th.web.app/invitebot.html) | [❯ Website](https://smilewinnextcord-th.web.app) | [❯ Support](https://nextcord.com/invite/R8RYXyB4Cg)",
                    colour = 0xffff00)
                embed.set_author(name=f"กําลังเล่น " + tracks.title, icon_url=self.bot.user.avatar.url, url=tracks.uri)
                embed.set_image(url =tracks.thumbnail)
                embed.set_footer(text=f"next up : {nu}")
                await message.edit(content=f"__รายการเพลง:__🎵\n {list_song} ",embed=embed)
                await player.play(tracks)

        elif server["Mode"] == "Repeat":
            await player.play(player.Track)

        else:
            pass

    @commands.command(aliases=['joi', 'j', 'summon', 'su', 'con'])
    async def join(self, ctx: commands.Context, *, channel: nextcord.VoiceChannel = None) -> None:
        if not channel:
            channel = getattr(ctx.author.voice, "channel", None)
            if not channel:
                return await ctx.send("You must be in a voice channel in order to use this command!")

        await ctx.author.voice.channel.connect(cls=pomice.Player)
        await ctx.send(f"Joined the voice channel `{channel.name}`", delete_after=3)

    @commands.command(aliases=['disconnect', 'dc', 'disc', 'lv'])
    async def leave(self, ctx: commands.Context):
        if not (player := ctx.voice_client):
            return await ctx.send("You must have the bot in a channel in order to use this command", delete_after=7)

        await player.destroy()
        await ctx.send("Player has left the channel.")

    async def handle_click(self, button: nextcord.ui.Button, interaction : nextcord.Interaction):
        embed = nextcord.Embed(
            title = button.custom_id,
            colour = 0xFED000
        )
        
        player = self.bot.get_guild(interaction.guild.id).voice_client
        if not player is None:
            if interaction.user == player.dj or interaction.user.guild_permissions.administrator:
                if button.custom_id == "pause_stop":
                    if player.is_paused and player.is_connected:
                        await player.set_pause(False)
                    
                    elif not player.is_paused and player.is_connected:
                        await player.set_pause(True)

                elif button.custom_id == "increase_volume":
                    if player.volume < 100:
                        await player.set_volume(player.volume + 10)
                
                elif button.custom_id == "decrease_volume":
                    if player.volume > 0:
                        await player.set_volume(player.volume - 10)
                
                elif button.custom_id == "mute_unmute_volume":
                    if player.volume == 0:
                        await player.set_volume(80)
                    
                    else:
                        await player.set_volume(0)
            else:
                embed= nextcord.embeds(
                    title = f"{interaction.user.mention} ไม่มีสิทธิ์ตั้งค่า",
                    colour = 0x983925
                )
                await interaction.send
        else:
            pass
    
    async def song_embed(self, track : pomice.Track):
        pass
    @commands.command(aliases=['pla', 'p'])
    async def play(self, ctx: commands.Context, *, search: str):
        data = await settings.collection.find_one({"guild_id":ctx.guild.id})
        if data is not None:
            music_channel = data["Music_channel_id"]
            music_embed = data["Embed_message_id"]
            music_message = data["Music_message_id"]
            if music_channel != "None":
                if music_embed != "None" and music_message != "None":
                    if ctx.channel.id == music_channel:
                        player : pomice.player = self.pomice._nodes[settings.lavalinkindentifier].get_player(ctx.guild.id)
                        if player is None:
                            await ctx.invoke(self.join)   
                            player = ctx.voice_client
                        results = await player.get_tracks(search, ctx=ctx)   
                        if not results:
                            return await ctx.send("No results were found for that search term", delete_after=7)
                        
                        Queue = await settings.collectionmusic.find_one({"guild_id":ctx.guild.id}) 
                        if isinstance(results, pomice.Playlist):
                            if Queue is None and not player.is_playing:
                                if len(results.tracks) > 20:
                                    results.tracks = results.tracks[:21]

                                num = 1
                                list_song = []
                                await player.play(results.tracks[0])
                                for track in results.tracks:
                                    list_song.append(f"> [{num}] " + track.title + "\n")
                                    data["Queue"].append({
                                            "position":num,
                                            "song_title":track.title,
                                            "song_id":track.track_id,
                                            "requester":ctx.author.id})
                                    num = num+1
                                nu = track if len(Queue["Queue"]) < 2 else Queue["Queue"][1]["song_title"]
                                embed=nextcord.Embed(
                                    description="[❯ Invite](https://smilewinnextcord-th.web.app/invitebot.html) | [❯ Website](https://smilewinnextcord-th.web.app) | [❯ Support](https://nextcord.com/invite/R8RYXyB4Cg)",
                                    colour = 0xffff00)
                                embed.set_author(name=f"กําลังเล่น {results.tracks[0].title}", icon_url=self.bot.user.avatar.url , url=results.tracks[0].uri)
                                embed.set_image(url =results.tracks[0].thumbnail)
                                embed.set_footer(text=f"next up : {nu}")
                                message = await self.bot.get_channel(music_channel).fetch_message(music_embed)
                                await message.edit(content=f"__รายการเพลง:__🎵\n {list_song} ",embed=embed)
                                await settings.collectionmusic.insert_one(data)
                            
                            else:
                                if not len(Queue["Queue"]) > 20:
                                    availble = 21 - len(Queue["Queue"])
                                    if len(results.tracks) > availble:
                                        results.tracks = results.tracks[:availble]
                                    num = len(Queue["Queue"]) + 1
                                    list_song = []
                                    for track in results.tracks:
                                        s_title = track.title
                                        s_id = track.track_id
                                        s_thumb = track.thumbnail
                                        s_uri  = track.uri
                                        list_song.append(f"> [{num}] " + track.title + "\n")
                                        await settings.collectionmusic.update_one({
                                            'guild_id': ctx.guild.id}, {
                                                '$push': {
                                                    'Queue': {
                                                        "position":num,
                                                        "song_title":s_title,
                                                        "song_id":s_id,
                                                        "requester":ctx.author.id
                                                        }
                                                    }
                                                })
                                        num = num+1
                                    nu = track if len(Queue["Queue"]) < 2 else Queue["Queue"][1]["song_title"]
                                    embed=nextcord.Embed(
                                        description="[❯ Invite](https://smilewinnextcord-th.web.app/invitebot.html) | [❯ Website](https://smilewinnextcord-th.web.app) | [❯ Support](https://nextcord.com/invite/R8RYXyB4Cg)",
                                        colour = 0xffff00)
                                    embed.set_author(name=f"กําลังเล่น {player.current.title}", icon_url=self.bot.user.avatar.url , url=player.current.uri)
                                    embed.set_image(url =player.current.thumbnail)
                                    embed.set_footer(text=f"next up : {nu}")
                                    message = await self.bot.get_channel(music_channel).fetch_message(music_embed)
                                    await message.edit(content=f"__รายการเพลง:__🎵\n {list_song} ",embed=embed)
                        else: 
                            track : pomice.Track= results[0]
                            s_title = track.title
                            s_id = track.track_id
                            s_thumb = track.thumbnail
                            s_uri  = track.uri
                            if Queue is None and not player.is_playing:
                                embed=nextcord.Embed(
                                    description="[❯ Invite](https://smilewinnextcord-th.web.app/invitebot.html) | [❯ Website](https://smilewinnextcord-th.web.app) | [❯ Support](https://nextcord.com/invite/R8RYXyB4Cg)",
                                    colour = 0xffff00)
                                embed.set_author(name=f"กําลังเล่น {track}", icon_url=self.bot.user.avatar.url , url=track.uri)
                                embed.set_image(url =track.thumbnail)
                                embed.set_footer(text=f"server : {ctx.guild.name}")
                                data = {
                                    "guild_id":ctx.guild.id,
                                    "Mode":"Default",
                                    "Request_channel":ctx.channel.id,
                                    "Queue":[]
                                }
                                data["Queue"].append({
                                        "position":1,
                                        "song_title":s_title,
                                        "song_id":s_id,
                                        "song_thum":s_thumb,
                                        "song_url":s_uri,
                                        "requester":ctx.author.id})
                                await player.play(track)

                                message = await self.bot.get_channel(music_channel).fetch_message(music_embed)
                                await message.edit(content=f"__รายการเพลง:__🎵\n [1]. {track} ",embed=embed)
                                await settings.collectionmusic.insert_one(data)

                            else:
                                if not len(Queue["Queue"]) > 20:
                                    nu = track if len(Queue["Queue"]) < 2 else Queue["Queue"][1]["song_title"]
                                    list_song = []
                                    num = 1
                                    embed=nextcord.Embed(description="[❯ Invite](https://smilewinnextcord-th.web.app/invitebot.html) | [❯ Website](https://smilewinnextcord-th.web.app) | [❯ Support](https://nextcord.com/invite/R8RYXyB4Cg)",
                                        colour = 0xffff00)
                                    embed.set_author(name=f"กําลังเล่น " + player.current.title, icon_url=self.bot.user.avatar.url, url=player.current.uri)
                                    embed.set_image(url =player.current.thumbnail)
                                    embed.set_footer(text=f"next up : {nu}")
                                    await settings.collectionmusic.update_one({
                                        "guild_id":ctx.guild.id}, {
                                            '$push': {
                                                'Queue': {
                                                    "position":len(Queue["Queue"])+1,
                                                    "song_title":s_title,
                                                    "song_id":s_id,
                                                    "song_thum":s_thumb,
                                                    "requester":ctx.author.id}}})

                                    for song in Queue["Queue"]:
                                        list_song.append(f"> [{num}] " + song["song_title"] + "\n")
                                        num = num +1
                                    list_song.append(f"> [{num}] " + s_title + "\n")
                                    list_song = "".join(list_song)

                                    message = await self.bot.get_channel(music_channel).fetch_message(music_embed)
                                    await message.edit(content=f"__รายการเพลง:__🎵\n {list_song} ",embed=embed)
                                                             
    @commands.command()
    async def musicsetup(self,ctx):
        data = await settings.collection.find_one({"guild_id":ctx.guild.id})
        if data is None:
            newserver = await Music.setnewserver(self,ctx)
            await settings.collection.insert_one(newserver)
            channel = await ctx.guild.create_text_channel(name = '😁│Smilewin Music',topic= ":play_pause: หยุด/เล่นเพลง:track_next: ข้ามเพลง:stop_button: หยุดและลบคิวในเพลง:arrows_counterclockwise: เริ่มเพลงที่กำลังเล่นใหม่:repeat: เปลี่ยนโหมดการวนเล่นเพลง:twisted_rightwards_arrows: สุ่มเพลงในคิว:sound: ลดเสียงขึ้นทีล่ะ 10%:loud_sound: เพิ่มเสียงทีล่ะ 10%:mute: ปิดเสียงเพลง")

            embed=nextcord.Embed(description="[❯ Invite](https://smilewinnextcord-th.web.app/invitebot.html) | [❯ Website](https://smilewinnextcord-th.web.app) | [❯ Support](https://nextcord.com/invite/R8RYXyB4Cg)",
                                colour = 0xffff00)
            embed.set_author(name="❌ ไม่มีเพลงที่เล่นอยู่ ณ ตอนนี้", icon_url=self.bot.user.avatar.url)
            embed.set_image(url ="https://i.imgur.com/XwFF4l6.png")
            embed.set_footer(text=f"server : {ctx.guild.name}")
            try:
                embed_message = await channel.send(content="__รายการเพลง:__\n🎵 ไม่มีเพลงที่กำลังเล่นในขณะนี้ " ,embed=embed, view = MusicButton(self))
            except Exception as e:
                print(e)
            music_message = await channel.send("กรุณาเข้า Voice Channel เเละเพิ่มเพลงโดยพิมพ์ชื่อเพลงหรือลิ้งเพลง")
            await settings.collection.update_one({"guild_id":ctx.guild.id},{"$set":{"Music_channel_id":channel.id,"Embed_message_id":embed_message.id,"Music_message_id":music_message.id}})

        else:
            if data["Music_channel_id"] == "None":
                channel = await ctx.guild.create_text_channel(name = '😁│Smilewin Music',topic= ":play_pause: หยุด/เล่นเพลง:track_next: ข้ามเพลง:stop_button: หยุดและลบคิวในเพลง:arrows_counterclockwise: เริ่มเพลงที่กำลังเล่นใหม่:repeat: เปลี่ยนโหมดการวนเล่นเพลง:twisted_rightwards_arrows: สุ่มเพลงในคิว:sound: ลดเสียงขึ้นทีล่ะ 10%:loud_sound: เพิ่มเสียงทีล่ะ 10%:mute: ปิดเสียงเพลง")

                embed=nextcord.Embed(description="[❯ Invite](https://smilewinnextcord-th.web.app/invitebot.html) | [❯ Website](https://smilewinnextcord-th.web.app) | [❯ Support](https://nextcord.com/invite/R8RYXyB4Cg)",
                                    colour = 0xffff00)
                embed.set_author(name="❌ ไม่มีเพลงที่เล่นอยู่ ณ ตอนนี้", icon_url=self.bot.user.avatar.url)
                embed.set_image(url ="https://i.imgur.com/XwFF4l6.png")
                embed.set_footer(text=f"server : {ctx.guild.name}")
                embed_message = await channel.send(embed=embed, view =  MusicButton(self.bot))
                music_message = await channel.send("กรุณาเข้า Voice Channel เเละเพิ่มเพลงโดยพิมพ์ชื่อเพลงหรือลิ้งเพลง")
                await settings.collection.update_one({"guild_id":ctx.guild.id},{"$set":{"Music_channel_id":channel.id,"Embed_message_id":embed_message.id,"Music_message_id":music_message.id}})

            else:
                if data["Music_channel_id"] not in ctx.guild.text_channels:
                    channel = await ctx.guild.create_text_channel(name = '😁│Smilewin Music',topic= ":play_pause: หยุด/เล่นเพลง:track_next: ข้ามเพลง:stop_button: หยุดและลบคิวในเพลง:arrows_counterclockwise: เริ่มเพลงที่กำลังเล่นใหม่:repeat: เปลี่ยนโหมดการวนเล่นเพลง:twisted_rightwards_arrows: สุ่มเพลงในคิว:sound: ลดเสียงขึ้นทีล่ะ 10%:loud_sound: เพิ่มเสียงทีล่ะ 10%:mute: ปิดเสียงเพลง")

                    embed=nextcord.Embed(description="[❯ Invite](https://smilewinnextcord-th.web.app/invitebot.html) | [❯ Website](https://smilewinnextcord-th.web.app) | [❯ Support](https://nextcord.com/invite/R8RYXyB4Cg)",
                                        colour = 0xffff00)
                    embed.set_author(name="❌ ไม่มีเพลงที่เล่นอยู่ ณ ตอนนี้", icon_url=self.bot.user.avatar.url)
                    embed.set_image(url ="https://i.imgur.com/XwFF4l6.png")
                    embed.set_footer(text=f"server : {ctx.guild.name}")
                    embed_message = await channel.send(content="__รายการเพลง:__\n🎵 ไม่มีเพลงที่กำลังเล่นในขณะนี้ " ,embed=embed, view =  MusicButton(self.bot))
                    music_message = await channel.send("กรุณาเข้า Voice Channel เเละเพิ่มเพลงโดยพิมพ์ชื่อเพลงหรือลิ้งเพลง")
                    await settings.collection.update_one({"guild_id":ctx.guild.id},{"$set":{"Music_channel_id":channel.id,"Embed_message_id":embed_message.id,"Music_message_id":music_message.id}})

                else:
                    channel = self.bot.get_channel(data["Music_channel_id"])
                    try:
                        embed_message = await channel.fetch_message(data["Embed_message_id"])
                        music_message = await channel.fetch_message(data["Music_message_id"])
                        embed = nextcord.embeds(title= "มีห้องเล่นเพลงเเล้ว",colour =0xffff00 , description= channel.mention)
                        await ctx.send(embed=embed)
                    except nextcord.NotFound:
                        try:
                            embed_message = await channel.fetch_message(data["Embed_message_id"])

                        except nextcord.NotFound:
                            embed=nextcord.Embed(description="[❯ Invite](https://smilewinnextcord-th.web.app/invitebot.html) | [❯ Website](https://smilewinnextcord-th.web.app) | [❯ Support](https://nextcord.com/invite/R8RYXyB4Cg)",
                                colour = 0xffff00)
                            embed.set_author(name="❌ ไม่มีเพลงที่เล่นอยู่ ณ ตอนนี้", icon_url=self.bot.user.avatar.url)
                            embed.set_image(url ="https://i.imgur.com/XwFF4l6.png")
                            embed.set_footer(text=f"server : {ctx.guild.name}")
                            embed_message = await channel.send(embed=embed, view =  MusicButton(self.bot))
                            await settings.collection.update_one({"guild_id":ctx.guild.id},{"$set":{"Embed_message_id":embed_message.id}})
                        
                        try:
                            music_message = await channel.fetch_message(data["Music_message_id"])
                        except nextcord.NotFound:
                            music_message = await channel.send("กรุณาเข้า Voice Channel เเละเพิ่มเพลงโดยพิมพ์ชื่อเพลงหรือลิ้งเพลง")
                            await settings.collection.update_one({"guild_id":ctx.guild.id},{"$set":{"Music_message_id":music_message.id}})


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))
    bot.add_view(MusicButton(bot))