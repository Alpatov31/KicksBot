import vk_api
import random
import time
import sqlite3

def process(intext):
    intext = intext.lower()
    if intext == "как дела?":
        outtext = "Нормально"
    elif intext == "что делаешь?":
        outtext = "Анализирую"
    elif intext == "bruh":
        outtext = "Bruhable"
    elif intext == "помянем?":
        outtext = "Помянем"
    else:
        outtext = "Bruh"



    return outtext

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

token = "b124a9e146dd07b3164a57f7b6857f6055d1f4d325587759071c70bba36db11826650130da6cb55442135"

vk = vk_api.VkApi(token=token)
vk._auth_token()
uploader = vk_api.upload.VkUpload(vk)

value = {"count":20, "offset":0, "filter":"unanswered"}

imgs = ["maestro_2.jpg", "Bruh_2.jpg", "5doggo.jpg", "stalker.jpg", "russia.jpg", "shlyapa.jpg", "crying_cat.jpg", "metroboomin.jpg", "volk.jpg"]
imgs_links = []

for i in imgs:
    img = uploader.photo_messages("images/"+i)[0]
    link = "photo"+str(img["owner_id"])+"_"+str(img["id"])
    imgs_links.append(link)

colors = ["silver", "black", "gray", "white", "red"]
sizes = ["8", "8_5", "9", "9_5", "10", "10_5", "11", "11_5"]
users = {}
# vk.method("messages.send", {"peer_id": 182479157, "message": "Bruh", "random_id": random.randint(1, 1000)})
# messages = vk.method("messages.getConversations", value)
# print(messages["items"][0]["last_message"]["text"])
while True:
    messages = vk.method("messages.getConversations", value)

    if messages["count"] > 0:
        from_id = messages["items"][0]["last_message"]["from_id"]
        in_text = messages["items"][0]["last_message"]["text"]

        if from_id not in users:
            print(type(from_id))
            users[from_id] = {"state": "start"}

        sql = f"SELECT * FROM Users WHERE id={from_id}"
        cursor.execute(sql)
        if len(cursor.fetchall()) == 0:
            sql = f'''
            INSERT INTO Users
            VALUES ({from_id}, 'start', 'red', '10')
            '''
            cursor.execute(sql)
            conn.commit()

        sql = f"SELECT state FROM Users WHERE id={from_id} "
        cursor.execute(sql)
        state = cursor.fetchone()[0]
        print(state)


        if state == "start":
            out_text = "Привет, напиши свой размер(us)."
            users[from_id]["state"] = "size"
            kbrd = open("keyboards/keyboard.json", "r", encoding="UTF-8").read()
        elif state == "size":
            if in_text in sizes:
                users[from_id]["size"] = in_text
                kbrd = open("keyboards/keybrd.json", "r", encoding="UTF-8").read()
                out_text = "Отлично, теперь введи цвет кроссовок, которые ты хочешь по-английски."
                users[from_id]["state"] = "color"
            else:
                out_text = "Введите один из: "+", ".join(sizes)
        elif state == "color":
            if in_text.lower() in colors:
                users[from_id]["color"] = in_text.lower()
                out_text = "https://sneakerhead.ru/shoes/sneakers/" + users[from_id]["color"] + "/size-" + users[from_id]["size"] + "/"
                users[from_id]["state"] = "finish"
            else:
                out_text = "Введите один из: " + ", ".join(colors)

        # out_text = process(in_text)

        vk.method("messages.send", {"peer_id": from_id, "message": out_text, "random_id": random.randint(1, 1000),
                                    "attachment": random.choice(imgs_links), "keyboard":kbrd})
    time.sleep(1)


