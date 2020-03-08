import vk_api
import random
import time
import sqlite3
import os


def set_state(state, id):
    sql = f'''UPDATE Users SET state='{state}' WHERE id={id} '''
    cursor.execute(sql)
    conn.commit()
def set_property(name, value, id):
    sql = f'''UPDATE Users SET {name}='{value}' WHERE id={id} '''
    cursor.execute(sql)
    conn.commit()
def get_property(name, id):
    sql = f"SELECT {name} FROM Users WHERE id={from_id} "
    cursor.execute(sql)
    return cursor.fetchone()[0]




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

token = os.environ['VK_TOKEN']

vk = vk_api.VkApi(token=token)
vk._auth_token()
uploader = vk_api.upload.VkUpload(vk)

value = {"count": 20, "offset": 0, "filter": "unanswered"}

imgs = ["maestro_2.jpg", "Bruh_2.jpg", "5doggo.jpg", "stalker.jpg", "russia.jpg", "shlyapa.jpg", "crying_cat.jpg",
        "metroboomin.jpg", "volk.jpg"]
imgs_links = []

for i in imgs:
    img = uploader.photo_messages("images/" + i)[0]
    link = "photo" + str(img["owner_id"]) + "_" + str(img["id"])
    imgs_links.append(link)

colors = ["silver", "black", "gray", "white", "red"]
sizes = ["8", "8_5", "9", "9_5", "10", "10_5", "11", "11_5"]

# vk.method("messages.send", {"peer_id": 182479157, "message": "Bruh", "random_id": random.randint(1, 1000)})
# messages = vk.method("messages.getConversations", value)
# print(messages["items"][0]["last_message"]["text"])
while True:
    messages = vk.method("messages.getConversations", value)

    if messages["count"] > 0:
        from_id = messages["items"][0]["last_message"]["from_id"]
        in_text = messages["items"][0]["last_message"]["text"]

        sql = f"SELECT * FROM Users WHERE id={from_id}"
        cursor.execute(sql)
        if len(cursor.fetchall()) == 0:
            sql = f'''
            INSERT INTO Users (id, state)
            VALUES ({from_id}, 'start')
            '''
            cursor.execute(sql)
            conn.commit()

        sql = f"SELECT state FROM Users WHERE id={from_id} "
        cursor.execute(sql)
        state = cursor.fetchone()[0]
        print(state)

        if state == "start":
            out_text = "Привет, напиши свой размер(us)."
            set_state("size", from_id)
            kbrd = open("keyboards/keyboard.json", "r", encoding="UTF-8").read()
        elif state == "size":
            if in_text in sizes:
                set_property("size", in_text, from_id)
                kbrd = open("keyboards/keybrd.json", "r", encoding="UTF-8").read()
                out_text = "Отлично, теперь введи цвет кроссовок, которые ты хочешь по-английски."
                set_state("color", from_id)
            else:
                out_text = "Введите один из: " + ", ".join(sizes)
        elif state == "color":
            if in_text.lower() in colors:
                set_property("color", in_text.lower(), from_id)
                out_text = "https://sneakerhead.ru/shoes/sneakers/" + get_property("color", from_id) + "/size-" + \
                           get_property("size", from_id) + "/"
                set_state("finish", from_id)
            else:
                out_text = "Введите один из: " + ", ".join(colors)

        # out_text = process(in_text)

        vk.method("messages.send", {"peer_id": from_id, "message": out_text, "random_id": random.randint(1, 1000),
                                    "attachment": random.choice(imgs_links), "keyboard": kbrd})
    time.sleep(1)
