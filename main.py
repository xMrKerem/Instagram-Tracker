import instaloader
import threading
from datetime import datetime
import discord
from pickledb import PickleDB
import pytz
from dotenv import load_dotenv
import os
import asyncio
import random

load_dotenv()
l = instaloader.Instaloader()
db = PickleDB("db.json")
intents = discord.Intents.default()
intents.messages = True
client = discord.Client(intents = intents)

token = os.getenv("DISCORD_TOKEN")
username = os.getenv("INSTAGRAM_USERNAME")
password = os.getenv("INSTAGRAM_PASSWORD")
channel_id = int(os.getenv("CHANNEL_ID"))
track = os.getenv("TRACK")
fail = 0
main_delay = 600
max_delay = 4 * 3600

if "giris_" + username in db.all():
    giris = db.get("giris_" + username)
else:
    giris = 0

if giris == 0:
    l.context.log("Giriş Yapılıyor...")

    try:
        l.login(username, password)
        l.save_session_to_file()
        print("Başarıyla giriş yapıldı ve oturum kaydedildi.")
        giris = 1
        db.set("giris_" + username, giris)
        db.save()
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        code = input("Lütfen Güvenlik Kodunu Giriniz:   ")
        l.two_factor_login(code)
        l.save_session_to_file()
        print("2FA kodu doğru, giriş yapıldı ve oturum kaydedildi.")
        giris = 1
        db.set("giris_" + username, giris)
        db.save()
else:
    l.load_session_from_file(username)

def tracker():
    tz_tr = pytz.timezone("Europe/Istanbul")
    delay = main_delay
    global fail

    try:
        profil = instaloader.Profile.from_username(l.context, track)

        new_profile_data = {
            "username": profil.username,
                "fullname": profil.full_name,
                "biography": profil.biography,
                "followers": profil.followers,
                "followees": profil.followees,
                "profile_pic": "", # geçici olarak bu özellik devre dışı
                "posts": profil.mediacount
        }

        old_profile_data = db.get("old_profile_data_" + track) or {}

        if old_profile_data != new_profile_data:
            yazdir(new_profile_data, profil)
            print(f"{datetime.now(tz_tr):%Y-%m-%d %H:%M:%S} | Verilerde Değişiklik Oldu.")
        else:
            print(f"{datetime.now(tz_tr):%Y-%m-%d %H:%M:%S} | Verilerde Değişiklik Yok.")

        fail = 0
        delay = main_delay

    except instaloader.exceptions.ConnectionException as e:
        msg = str(e)

        print(f"{datetime.now(tz_tr):%Y-%m-%d %H:%M:%S} | Bağlantı/rate-limit Hatası: ", msg)

        fail += 1
        delay = min(max_delay, int(main_delay * (2 ** fail)))
        delay += random.randint(30, 120)

        refresh_session()

    except Exception as e:
        print(f"{datetime.now(tz_tr):%Y-%m-%d %H:%M:%S} | Beklenmeyen Bir Hata Oluştu: ", e)

        fail += 1
        delay = min(max_delay, int(main_delay * (2 ** fail)))

    finally:
        threading.Timer(delay, tracker).start()


def yazdir(new_profile_data, profil):
    tz_tr = pytz.timezone("Europe/Istanbul")
    old_profile_data = db.get("old_profile_data_" + track)

    async def send():
        embed = discord.Embed(
            title = f"{new_profile_data['username']}, {new_profile_data['fullname']}",
            description = f"{new_profile_data['biography']}",
            colour = discord.Color(0x2F3136),
            timestamp = datetime.now(tz_tr)
        )

        embed.set_thumbnail(url=new_profile_data["profile_pic"])
        embed.add_field(name = "**Post**", value = new_profile_data["posts"], inline = True)
        embed.add_field(name = "**Takipçi**", value = new_profile_data["followers"], inline = True)
        embed.add_field(name = "**Takip**", value = new_profile_data["followees"], inline = True)

        channel = client.get_channel(channel_id)

        if channel:
            await channel.send(embed = embed)

            for i in new_profile_data:
                if i in old_profile_data and old_profile_data[i] != new_profile_data[i]:
                    await channel.send(f"{i} Verisi Değişti: {old_profile_data[i]} → {new_profile_data[i]}")
                    db.set("old_profile_data_" + track, new_profile_data)
                    db.save()

    if not client.is_ready():
        threading.Timer(2, yazdir, args = [new_profile_data, profil]).start()
        return

    asyncio.run_coroutine_threadsafe(send(), client.loop)

def refresh_session():
    global l
    try:
        l = instaloader.Instaloader(quiet = True)
        try:
            l.load_session_from_file(username)
            print("Session Başarıyla Güncellendi")
        except FileNotFoundError:
            l.login(username, password)
            l.save_session_to_file()
    except instaloader.exceptions.TwoFactorAuthRequiredException:
        print("2FA Hatası giriş yapılamıyor.")

tracker()
client.run(token)