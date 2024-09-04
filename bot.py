########################################
##   --This code is Turkish--         ##
##    Support:                        ## 
##   Instagram :l1ve709               ##
##   Discord : unk709/l1ve709.com     ##
##                                    ##
##                                    ##
##     --Made By Ediz SÖNMEZ--        ##  
##                                    ##  
########################################
#   verification bot with math captcha

import discord
from discord.ext import commands
from discord.ui import Button, View
from captcha.image import ImageCaptcha
from PIL import Image, ImageDraw
import random
import io

print("dev. by ediz sonmez")
xxx709 = "YOUR_TOKEN"     # DİSCORD BOT TOKEN
intents = discord.Intents.all()
l1ve709 = commands.Bot(command_prefix='*', intents=intents, help_command=None)

deger = {
    "dogrulamakanali_id": 1279938468545560692,  # CAPTCHA CHANNEL ID
    "dogrulanmisrol": 1279851342147358781,  # VERFIED ROLE ID
    "logID": 1279857122578006097 # LOG CHANNEL ID
}

@l1ve709.event
async def on_ready():
    print(f'{l1ve709.user.name}')
    
    await l1ve709.change_presence(
        status=discord.Status.dnd,
        activity=discord.Streaming(name="dev. by Ediz Sönmez", url="http://twitch.tv/l1ve709")
    )

def metinolustur():
    numara1 = random.randint(10, 35)
    numara2 = random.randint(10, 35)
    arti = '+'
    topla = numara1 + numara2
    return f"{numara1} {arti} {numara2} =", topla

def captchagorseli(captcha_metni):
    image = ImageCaptcha(width=300, height=100)
    resim = image.generate_image(captcha_metni)
    
    xx3 = ImageDraw.Draw(resim)
    for i in range(10):  
        start_point = (random.randint(0, 300), random.randint(0, 100))
        end_point = (random.randint(0, 300), random.randint(0, 100))
        xx3.line([start_point, end_point], fill=(0, 0, 0), width=2)  
    
    buffer = io.BytesIO()
    resim.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer

class CaptchaView(View):
    def __init__(self, doğrucevap, member, dogrulamakanali, logkanali):
        super().__init__(timeout=300)
        self.doğrucevap = doğrucevap
        self.member = member
        self.dogrulamakanali = dogrulamakanali
        self.logkanali = logkanali
        self.solved = False

        options = self.randomsecenek(doğrucevap)
        for option in options:
            button = Button(label=str(option), style=discord.ButtonStyle.primary, custom_id=str(option))
            button.callback = self.check_answer
            self.add_item(button)

    def randomsecenek(self, doğrucevap):
        options = [doğrucevap]
        while len(options) < 10:
            yanlıscevap = random.randint(doğrucevap - 10, doğrucevap + 10)
            if yanlıscevap not in options:
                options.append(yanlıscevap)
        random.shuffle(options)
        return options

    async def check_answer(self, interaction: discord.Interaction):
        if self.solved:
            await interaction.response.send_message("Zaten doğrulama yapıldı.", ephemeral=True)
            return

        if interaction.user == self.member:
            chosen_answer = int(interaction.data["custom_id"])
            if chosen_answer == self.doğrucevap:
                role = discord.utils.get(self.member.guild.roles, id=deger["dogrulanmisrol"])
                if role:
                    restricted_role = discord.utils.get(self.member.guild.roles, name="Doğrulanmamış")
                    if restricted_role:
                        await self.member.remove_roles(restricted_role)
                    
                    await self.member.add_roles(role)
                    
                    await self.dogrulamakanali.send(f"Tebrikler {self.member.mention}, CAPTCHA'yı başarıyla çözdün. Artık tüm kanallara erişimin var.")
                    await self.dogrulamakanali.set_permissions(self.member, overwrite=None)
                    await self.logkanali.send(f"{self.member.mention} CAPTCHA'yı başarıyla tamamladı.")
                    self.solved = True
                    await interaction.response.send_message("Doğrulama başarılı", ephemeral=True)
                else:
                    await self.dogrulamakanali.send("Doğrulama rolü bulunamadı. Lütfen sunucu yöneticisine başvurun.")
                    self.solved = True
                    await interaction.response.send_message("Doğrulama rolü bulunamadı.", ephemeral=True)
            else:
                self.solved = True
                await self.dogrulamakanali.send(f"Yanlış CAPTCHA, {self.member.mention}. Lütfen tekrar dene.")
                await interaction.response.send_message("Yanlış seçim yaptınız. Yeni CAPTCHA gönderildi.", ephemeral=True)
                captcha_metni, captcha_sonuc = metinolustur()
                resim_buffer = captchagorseli(captcha_metni)
                embed = discord.Embed(
                    title="🚫 Yanlış Cevap",
                    description=f"Yanlış CEVAP, {self.member.mention}. Lütfen doğru cevabı seçin.",
                    color=discord.Color.red() 
                )
                embed.set_image(url="attachment://captcha.png")
                await self.dogrulamakanali.send(embed=embed, file=discord.File(resim_buffer, "captcha.png"))
                new_view = CaptchaView(doğrucevap=captcha_sonuc, member=self.member, dogrulamakanali=self.dogrulamakanali, logkanali=self.logkanali)
                await self.dogrulamakanali.send("Lütfen yeni CAPTCHA sonucunu seçin:", view=new_view)
        else:
            await interaction.response.send_message("Bu buton size ait değil.", ephemeral=True)

async def create_or_get_restricted_role(guild):
    role_name = "Doğrulanmamış"
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        role = await guild.create_role(name=role_name)
        
        for channel in guild.channels:
            if channel.id != deger["dogrulamakanali_id"]:
                await channel.set_permissions(role, read_messages=False, send_messages=False)
                
    return role

@l1ve709.event
async def on_member_join(member):
    if not deger["dogrulamakanali_id"] or not deger["dogrulanmisrol"] or not deger["logID"]:
        return
    
    dogrulamakanali = l1ve709.get_channel(deger["dogrulamakanali_id"])
    logkanali = l1ve709.get_channel(deger["logID"])
    
    if not dogrulamakanali or not logkanali:
        print("Geçici veya log kanalı bulunamadı.")
        return

    role = await create_or_get_restricted_role(member.guild)
    await member.add_roles(role)
    
    captcha_metni, captcha_sonuc = metinolustur()
    resim_buffer = captchagorseli(captcha_metni)

    embed = discord.Embed(
        title=f"Hoşgeldin {member.guild.name}",
        description=f"{member.mention}, sunucuya hoş geldin. Tam erişim sağlamak için işlemi çöz."
    )
    embed.set_image(url="attachment://captcha.png")
    embed.set_footer(text=member.guild.name, icon_url=member.guild.icon.url)  
    
    await dogrulamakanali.send(embed=embed, file=discord.File(resim_buffer, "captcha.png"))

    view = CaptchaView(doğrucevap=captcha_sonuc, member=member, dogrulamakanali=dogrulamakanali, logkanali=logkanali)
    await dogrulamakanali.send("Lütfen doğru sonucu seçin:", view=view)



@l1ve709.command()
async def ayar(ctx, kanal: discord.TextChannel, rol: discord.Role, logkanali: discord.TextChannel):
    deger["dogrulamakanali_id"] = kanal.id
    deger["dogrulanmisrol"] = rol.id
    deger["logID"] = logkanali.id
    await ctx.send(f"✅ CAPTCHA kanalı **{kanal.name}**, doğrulama rolü **{rol.name}** ve log kanalı **{logkanali.name}** olarak ayarlandı.")

@l1ve709.command()
async def ayarkanal(ctx, kanal: discord.TextChannel):
    deger["dogrulamakanali_id"] = kanal.id
    await ctx.send(f"🖊️ Geçici CAPTCHA kanalı **{kanal.name}** olarak ayarlandı.")

@l1ve709.command()
async def ayarrol(ctx, rol: discord.Role):
    deger["dogrulanmisrol"] = rol.id
    await ctx.send(f"🎫 Doğrulama rolü **{rol.name}** olarak ayarlandı.")

@l1ve709.command()
async def ayarlog(ctx, kanal: discord.TextChannel):
    deger["logID"] = kanal.id
    await ctx.send(f"📝 Log kanalı **{kanal.name}** olarak ayarlandı.")       

l1ve709.run(xxx709)
