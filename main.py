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


def url_sneakerhead(id):
    g = get_property("gender", id)
    c = get_property("color", id)
    s = get_property("size", id)
    return "https://sneakerhead.ru/shoes/sneakers/" + g + "/" + c + "/size-" + \
           s + "/"


def url_brandshop(id):
    g = get_property("gender", id)
    c = get_property("color", id)
    s = get_property("size", id)
    trans_g = { "men": "muzhskoe",
                'women': "zhenskoe",
    }
    trans_c = {"black": "черный",
               "white": "белый",
               "green": "зеленый",
    }
    trans_s = {"8": "40",
               "8_5": "40.5",
                "9": "41",
               }
    g = trans_g[g]
    c = trans_c[c]
    s = trans_s[s]

    return "https://brandshop.ru/" + g +"/obuv/krossovki/?mfp=16-tsvet[" + c + "],13o-razmer[" + s + "%20EU]/"



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

colors = ["silver", "black", "gray", "white", "red", "orange", "yellow", "green", "purple"]
sizes = ["8", "8_5", "9", "9_5", "10", "10_5", "11", "11_5"]
genders = ["men", "women", "kids"]

kbrd = open("keyboards/empty.json", "r", encoding="UTF-8").read()

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

        if in_text == "Home":
            set_state("start", from_id)

        sql = f"SELECT state FROM Users WHERE id={from_id} "
        cursor.execute(sql)
        state = cursor.fetchone()[0]
        print(state)

        if state == "start":
            out_text = "Привет, напиши свой размер(us)."
            set_state("size", from_id)
            kbrd = open("keyboards/sizes.json", "r", encoding="UTF-8").read()
        elif state == "size":
            if in_text in sizes:
                set_property("size", in_text, from_id)
                kbrd = open("keyboards/genders.json", "r", encoding="UTF-8").read()
                out_text = "Теперь введите ваш пол."
                set_state("gender", from_id)
            else:
                out_text = "Введите один из: " + ", ".join(sizes)
        elif state == "gender":
            if in_text.lower() in genders:
                set_property("gender", in_text.lower(), from_id)
                out_text = "Отлично, теперь введи цвет кроссовок, которые ты хочешь."
                kbrd = open("keyboards/colors.json", "r", encoding="UTF-8").read()
                set_state("color", from_id)
        elif state == "color":
            if in_text.lower() in colors:
                set_property("color", in_text.lower(), from_id)
                out_text = url_sneakerhead(from_id)+"\n"+url_brandshop(from_id)
                kbrd = open("keyboards/home.json", "r", encoding="UTF-8").read()
                set_state("finish", from_id)

            else:
                out_text = "Введите один из: " + ", ".join(colors)

        # out_text = process(in_text)

        vk.method("messages.send", {"peer_id": from_id, "message": out_text, "random_id": random.randint(1, 1000),
                                    "attachment": random.choice(imgs_links), "keyboard": kbrd})
    time.sleep(1)
