from flask import Flask, request
import requests

app = Flask(__name__)

# ── Credentials ─────────────────────────
VERIFY_TOKEN = "spicebox123"
ACCESS_TOKEN = "EAAW66CLlGCsBRWxKx52Q7ZBSg3aZCAESrLd7EKt47jw4YF11UkA6buV4GqRozdS8oS7a2Ww60s7vfypTvOxyne4p4MC11kCJk49WoKbzQ8ZCC4ZA77WZBha3ZCzZCqPQ3zdJXBVm1hpdiXr9ysApkZBkKnKOOjXyHVfIXi3zVSmxj2dMuFyCQ1kREOZCJZCyqnthx8YZCOualx0MxqUkabZB7JpApSdd7EKlLtJ3otdAxcqoI6ZAUmbqRvAwQ8FcFW1ToZAnz0hZA4bqB2YPvLjxxSOqEqyGgj0m8XU0ADZC8gZDZD"
PHONE_NUMBER_ID = "1138025436056275"

# ── MENU WITH IMAGES ───────────────────
MENU = {
    "desi": {
        "Chicken Karahi": {"price": 700, "img": "https://i.ibb.co/hR3bJgT3/Fries.png"},
        "Chicken Handi": {"price": 1250, "img": "https://i.ibb.co/hR3bJgT3/Fries.png"},
    },
    "chinese": {
        "Chicken Chowmein": {"price": 750, "img": "https://i.ibb.co/hR3bJgT3/Fries.png"},
    },
    "fries": {
        "Pizza Fries": {"price": 470, "img": "https://i.ibb.co/hR3bJgT3/Fries.png"},
    }
}

sessions = {}

# ── SEND FUNCTIONS ─────────────────────
def send_text(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp","to": to,"type": "text","text": {"body": text}}
    requests.post(url, headers=headers, json=data)

def send_buttons(to, text, buttons):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text},
            "action": {
                "buttons": [
                    {"type": "reply","reply": {"id": b["id"],"title": b["title"][:20]}}
                    for b in buttons[:3]
                ]
            }
        }
    }
    requests.post(url, headers=headers, json=data)

def send_list(to, text, sections):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": text},
            "action": {"button": "View Options","sections": sections}
        }
    }
    requests.post(url, headers=headers, json=data)

def send_image(to, image_url, caption=""):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {"link": image_url, "caption": caption}
    }
    requests.post(url, headers=headers, json=data)

# ── HELPERS ────────────────────────────
def get_session(phone):
    if phone not in sessions:
        sessions[phone] = {"step": "welcome","cart": [],"current_cuisine": ""}
    return sessions[phone]

def cart_total(cart):
    return sum(i["price"] for i in cart)

def cart_text(cart):
    return "\n".join([f"• {i['name']} — Rs {i['price']}" for i in cart])

# ── MAIN FLOW ─────────────────────────
def handle_message(phone, text, button_id=None):
    s = get_session(phone)
    msg = (button_id or text).lower()

    # WELCOME
    if msg in ["hi","hello","start"] or s["step"]=="welcome":
        s["step"] = "main"
        send_buttons(phone,"Welcome! Choose:",
            [{"id":"order","title":"Order"},{"id":"menu","title":"Menu"}])
        return

    # MAIN
    if s["step"]=="main":
        if msg=="order":
            s["step"]="cuisine"
            send_buttons(phone,"Select cuisine:",
                [{"id":"desi","title":"Desi"},{"id":"chinese","title":"Chinese"},{"id":"fries","title":"Fries"}])
            return

    # CUISINE
    if s["step"]=="cuisine":
        s["current_cuisine"]=msg
        s["step"]="item"

        rows=[]
        for i,(name,data) in enumerate(MENU[msg].items()):
            rows.append({"id":f"item_{i}","title":name,"description":f"Rs {data['price']}"})

        send_list(phone,"Select item:",[{"title":"Menu","rows":rows}])
        return

    # ITEM SELECT
    if s["step"]=="item":
        if msg.startswith("item_"):
            idx=int(msg.split("_")[1])
            items=list(MENU[s["current_cuisine"]].items())
            name,data=items[idx]

            s["selected"]={"name":name,"price":data["price"],"img":data["img"]}
            s["step"]="action"

            send_buttons(phone,
                f"{name} — Rs {data['price']}",
                [{"id":"view","title":"View Image"},{"id":"add","title":"Order Now"}])
            return

    # ACTION
    if s["step"]=="action":
        if msg=="view":
            send_image(phone,s["selected"]["img"],s["selected"]["name"])
            send_buttons(phone,"Next?",
                [{"id":"add","title":"Order Now"},{"id":"back","title":"Back"}])
            return

        if msg=="add":
            s["cart"].append(s["selected"])
            s["step"]="more"
            send_buttons(phone,
                f"Added!\n{cart_text(s['cart'])}\nTotal: {cart_total(s['cart'])}",
                [{"id":"more","title":"Add More"},{"id":"checkout","title":"Checkout"}])
            return

        if msg=="back":
            s["step"]="cuisine"
            send_buttons(phone,"Select cuisine:",
                [{"id":"desi","title":"Desi"},{"id":"chinese","title":"Chinese"},{"id":"fries","title":"Fries"}])
            return

    # MORE
    if s["step"]=="more":
        if msg=="more":
            s["step"]="cuisine"
            send_buttons(phone,"Select cuisine:",
                [{"id":"desi","title":"Desi"},{"id":"chinese","title":"Chinese"},{"id":"fries","title":"Fries"}])
            return

        if msg=="checkout":
            send_text(phone,"Order placed! ✅")
            sessions.pop(phone)
            return

# ── WEBHOOK ───────────────────────────
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token")==VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "error"

@app.route("/webhook", methods=["POST"])
def webhook():
    data=request.get_json()
    try:
        msg=data["entry"][0]["changes"][0]["value"]["messages"][0]
        phone=msg["from"]

        if msg["type"]=="interactive":
            if "button_reply" in msg["interactive"]:
                handle_message(phone,msg["interactive"]["button_reply"]["id"],msg["interactive"]["button_reply"]["id"])
            elif "list_reply" in msg["interactive"]:
                handle_message(phone,msg["interactive"]["list_reply"]["id"],msg["interactive"]["list_reply"]["id"])
        elif msg["type"]=="text":
            handle_message(phone,msg["text"]["body"])
    except:
        pass

    return "ok"

if __name__=="__main__":
    app.run(port=5000)