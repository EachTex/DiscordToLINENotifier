from discord.ui import Select, View, Button, Modal
from discord.commands import Option, slash_command
from discord.ext import commands, tasks
import discord, json, datetime, requests, pytz, random

channel_id = 0 # <- LINE Notifyが未設定だった場合に通知を送信するチャンネルID

class RemindCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop.start()

    def cog_unload(self):
        self.loop.cancel()

    @tasks.loop(seconds=5)
    async def loop(self):
        jst = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
        now = datetime.datetime.now(tz = jst)

        with open(f"./remind_line.json", "r") as f:
            userdata = json.load(f)
            f.close()

        with open(f"./remind.json", "r") as f:
            data = json.load(f)
            f.close()

        for remind_id in list(data.keys()):
            _remind = data[remind_id]
            if int(_remind['time']) >= float(now.timestamp()):
                usr = self.bot.get_user(int(_remind['user']))
                if str(_remind['user']) not in userdata.keys():
                    channel = self.bot.get_channel(channel_id)
                    if _remind['title'] == "":
                        e = discord.Embed(title = "リマインド", description = _remind['description'], color = 0xfa0909)
                    else:
                        e = discord.Embed(title = _remind['title'], description = _remind['description'], color = 0xfa0909)
                    await channel.send(embed = e, content = usr.mention)

                else:
                    token = userdata[f"{_remind['user']}"]
                    headers = {'Authorization': f'Bearer {token}'}
                    if _remind['title'] == "":
                        head = {'message': f"リマインダー by Discord\n{_remind['description']}"}
                    else:
                        head = {'message': f"{_remind['title']}\n{_remind['description']}"}
                    requests.post(f"https://notify-api.line.me/api/notify", headers = headers, data = head)
                    del data[str(remind_id)]
                    with open(f"./remind.json", "w") as f:
                        json.dump(data, f, indent = 4, ensure_ascii = False)
                        f.close()

    @loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    rem = discord.SlashCommandGroup('reminder')
    @rem.command(name = "setup", description = f"リマインドのセットアップを行います。")
    async def rem_setup(self, ctx):
        with open(f"./remind_line.json", "r") as f:
            data = json.load(f)
            f.close()

        if str(ctx.author.id) not in data.keys():
            e = discord.Embed(title = "LINE Notifyの設定", description = f"LINEを使用して、お使いのスマートフォンからリマインドを受信できます。\nLINEで通知を受け取るには、緑のボタンを押してください。", color = 0x39375B)
            v = View()
            b1 = Button(
                label = "LINEで受信する(推奨)",
                style = discord.ButtonStyle.green,
                custom_id = f"remind:setup_line"
            )
            b2 = Button(
                label = "Discordで受信する",
                style = discord.ButtonStyle.blurple,
                custom_id = f"remind:setup_discord"
            )
            v.add_item(b1)
            v.add_item(b2)
            await ctx.respond(embed = e, view = v)

        else:
            e = discord.Embed(title = "リマインドを設定する", description = f"通知したい内容と通知タイトル、通知したい時間を設定してください。", color = 0x33aabb)
            v = View()
            b = Button(
                label = "通知を設定する",
                custom_id = f"remind:setup_remind",
                style = discord.ButtonStyle.blurple
            )
            v.add_item(b)
            await ctx.respond(embed = e, view = v)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        if interaction.custom_id == None:
            return

        if interaction.custom_id == "remind:setup_line":
            e = discord.Embed(title = "LINE Notifyを設定する", description = f"１．[LINE Notify](https://notify-bot.line.me/ja/)に、お使いのLINEアカウントでログインします。\n２．[マイページ](https://notify-bot.line.me/my/)から、\"アクセストークンの発行(開発者向け)\"の、\n\"トークンを発行する\"を押して、新しいアクセストークンを発行します。\n３．発行されたトークンを、下のボタンを押して貼り付けます。", color = 0xC4D6B0)
            v = View()
            b = Button(
                label = "LINE Notifyトークンを設定する",
                custom_id = f"remind:setup_line_token",
                style = discord.ButtonStyle.green
            )
            v.add_item(b)
            await interaction.response.edit_message(embed = e, view = v)

        elif interaction.custom_id == "remind:setup_line_token":
            m = Modal(
                title = "LINE Notifyトークンを設定する",
                custom_id = f"remind:set_token"
            )
            m.add_item(
                discord.ui.InputText(
                    label = f"トークンを入力：",
                    placeholder = f"ABCDEFGabcdefg0123456789...",
                    required = True
                )
            )
            await interaction.response.send_modal(m)

        elif interaction.custom_id == "remind:set_token":
            with open(f"./remind_line.json", "r") as f:
                userdata = json.load(f)
                f.close()

            userdata[f"{interaction.user.id}"] = interaction.data['components'][0]['components'][0]['value']

            with open(f"./remind_line.json", "w") as f:
                json.dump(userdata, f, indent = 4, ensure_ascii = False)
                f.close()

            e = discord.Embed(title = "LINE Notifyトークンの設定完了", description = f"LINE Notifyのトークンを設定しました。\n以降はこのトークン宛てに通知が送信されます。", color = 0x3bd37b)
            e2 = discord.Embed(title = "リマインドを設定する", description = f"通知したい内容と通知タイトル、通知したい時間を設定してください。", color = 0x33aabb)
            v = View()
            b = Button(
                label = "通知を設定する",
                custom_id = f"remind:setup_remind",
                style = discord.ButtonStyle.blurple
            )
            v.add_item(b)
            await interaction.response.edit_message(embeds = [e, e2], view = v)

        elif interaction.custom_id == "remind:setup_discord":
            e = discord.Embed(title = "リマインドを設定する", description = f"通知したい内容と通知タイトル、通知したい時間を設定してください。", color = 0x33aabb)
            v = View()
            b = Button(
                label = "通知を設定する", 
                custom_id = f"remind:setup_remind",
                style = discord.ButtonStyle.blurple
            )
            v.add_item(b)
            await interaction.response.edit_message(embed = e, view = v)

        elif interaction.custom_id == "remind:setup_remind":
            m = Modal(
                title = "リマインドを登録する",
                custom_id = f"remind:setting_remind"
            )
            m.add_item(
                discord.ui.InputText(
                    label = "通知タイトル(Discordで通知する際のみ使用)",
                    style = discord.InputTextStyle.short,
                    required = False,
                    custom_id = "remind:title"
                )
            )
            m.add_item(
                discord.ui.InputText(
                    label = "通知内容",
                    style = discord.InputTextStyle.long,
                    required = True,
                    custom_id = f"remind:description"
                )
            )
            m.add_item(
                discord.ui.InputText(
                    label = "通知したい時間",
                    required = True,
                    placeholder = f"YYYY/MM/DD HH:MMで表記してください(1990/01/01 00:00)",
                    custom_id = f"remind:time"
                )
            )
            await interaction.response.send_modal(m)

        elif interaction.custom_id == "remind:setting_remind":
            data = interaction.data['components']
            for item in data:
                item = item['components'][0]
                if item['custom_id'] == "remind:title":
                    _title = item['value']
                elif item['custom_id'] == "remind:description":
                    _description = item['value']
                elif item['custom_id'] == "remind:time":
                    _time = item['value']

            tsp = _time.split("/")
            yy = tsp[0]
            mm = tsp[1]
            d_t = tsp[2].split(" ")
            dd = d_t[0]
            tt_sp = d_t[1].split(":")
            hh = tt_sp[0]
            minu = tt_sp[1]
            jst = pytz.timezone('Asia/Tokyo')
            _datetime = datetime.datetime(int(yy), int(mm), int(dd), int(hh), int(minu), second = 00)
            _time = jst.localize(_datetime)
            _timestamp = int(_time.timestamp())

            now = datetime.datetime.now().timestamp()
            if _timestamp <= now:
                e = discord.Embed(title = "エラー", description = f"通知時間は現在よりも後を指定してください！", color = 0xfa0909)
                await interaction.response.edit_message(embed = e, view = None)
            else:
                if _title != "":
                    e = discord.Embed(title = _title, description = _description, color = 0x50C5B7, timestamp = _time)
                else:
                    e = discord.Embed(title = "通知プレビュー", description = _description, color = 0x50C5B7, timestamp = _time)

                with open(f"./remind.json", "r") as f:
                    rmdata = json.load(f)
                    f.close()

                rmid = random.randint(10000000, 99999999)
                while str(rmid) in rmdata.keys():
                    rmid = random.randint(10000000, 99999999)

                rmdata[rmid] = {
                    "user": interaction.user.id,
                    "title": _title, 
                    "description": _description,
                    "time": _timestamp
                }

                with open(f"./remind.json", "w") as f:
                    json.dump(rmdata, f, indent = 4, ensure_ascii = False)
                    f.close()

                await interaction.response.edit_message(content = f"リマインドが保存されました。\n<t:{_timestamp}>に次の内容で通知します。", embed = e, view = None)

def setup(bot):
    bot.add_cog(RemindCog(bot))