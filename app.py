from flask import Flask, request
import requests

app = Flask(__name__)

# ── Credentials ─────────────────────────
VERIFY_TOKEN = "spicebox123"
ACCESS_TOKEN = "PUT_NEW_TOKEN_HERE"
PHONE_NUMBER_ID = "1138025436056275"

IMG = "https://i.ibb.co/hR3bJgT3/Fries.png"

# ── FULL MENU ─────────────────────────
MENU = {
    "seekh": {
        "Beef Seekh": {"price": 7, "img": IMG},
        "Beef Seekh Combo": {"price": 20, "img": IMG},
        "Chicken Seekh": {"price": 6, "img": IMG},
        "Chicken Seekh Combo": {"price": 6, "img": IMG},
        "Seekh Platter": {"price": 22, "img": IMG},
    },
    "tikka": {
        "Afghani Tikka": {"price": 8, "img": IMG},
        "Red Tikka": {"price": 8, "img": IMG},
        "Hariyali Tikka": {"price": 8, "img": IMG},
        "Tikka Combo": {"price": 10, "img": IMG},
        "Tikka Small Platter": {"price": 22, "img": IMG},
        "Tikka Large Platter": {"price": 40, "img": IMG},
    },
    "galawti": {
        "Kabab": {"price": 2.5, "img": IMG},
        "Kabab Paratha": {"price": 5, "img": IMG},
        "Bun Kabab": {"price": 4, "img": IMG},
    },
    "rolls": {
        "Kabab Roll": {"price": 5, "img": IMG},
        "Afghani Roll": {"price": 8, "img": IMG},
        "Red Roll": {"price": 8, "img": IMG},
        "Hariyali Roll": {"price": 8, "img": IMG},
        "Chicken Seekh Roll": {"price": 8, "img": IMG},
        "Beef Seekh Roll": {"price": 8, "img": IMG},
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
        sessions[phone] = {
            "step": "welcome",
            "cart": [],
            "current_cuisine": "",
            "name": "",
            "address": ""
        }
    return sessions[phone]

def cart_total(cart):
    return sum(i["price"] for i in cart)

def cart_text(cart):
    return "\n".join([f"{i['name']} - {i['price']} SAR" for i in cart])

# ── MAIN FLOW ─────────────────────────
def handle_message(phone, text, button_id=None):
    s = get_session(phone)
    msg = (button_id or text).lower()

    # WELCOME
    if msg in ["hi","hello","start"] or s["step"]=="welcome":
        s["step"] = "main"
        send_buttons(phone,"Welcome! Choose:",
            [{"id":"order","title":"Order Now"}])
        return

    # MAIN
    if s["step"]=="main":
        if msg=="order":
            s["step"]="cuisine"
            send_buttons(phone,"Select Category:",
                [{"id":"seekh","title":"Seekh"},
                 {"id":"tikka","title":"Tikka"},
                 {"id":"more","title":"More"}])
            return

    # MORE CATEGORY
    if msg=="more":
        s["step"]="cuisine"
        send_buttons(phone,"More Categories:",
            [{"id":"galawti","title":"Galawti"},
             {"id":"rolls","title":"Rolls"}])
        return

    # CUISINE
    if s["step"]=="cuisine":
        if msg in MENU:
            s["current_cuisine"]=msg
            s["step"]="item"

            items = MENU[msg]
            text_menu = "\n".join([
                f"{i+1}. {name} - {data['price']} SAR"
                for i,(name,data) in enumerate(items.items())
            ])

            send_text(phone,f"Select item:\n{text_menu}\nReply number")
            return

    # ITEM SELECT
    if s["step"]=="item":
        try:
            idx=int(text)-1
            items=list(MENU[s["current_cuisine"]].items())
            name,data=items[idx]

            s["selected"]={"name":name,"price":data["price"],"img":data["img"]}
            s["step"]="action"

            send_buttons(phone,f"{name} - {data['price']} SAR",
                [{"id":"view","title":"Image"},
                 {"id":"add","title":"Add"}])
        except:
            send_text(phone,"Invalid choice")
        return

    # ACTION
    if s["step"]=="action":
        if msg=="view":
            send_image(phone,s["selected"]["img"],s["selected"]["name"])
            return

        if msg=="add":
            s["cart"].append(s["selected"])
            s["step"]="more2"

            send_buttons(phone,
                f"{cart_text(s['cart'])}\nTotal: {cart_total(s['cart'])} SAR",
                [{"id":"more","title":"More"},
                 {"id":"checkout","title":"Checkout"}])
            return

    # MORE / CHECKOUT
    if s["step"]=="more2":
        if msg=="more":
            s["step"]="cuisine"
            send_buttons(phone,"Select Category:",
                [{"id":"seekh","title":"Seekh"},
                 {"id":"tikka","title":"Tikka"},
                 {"id":"more","title":"More"}])
            return

        if msg=="checkout":
            s["step"]="get_name"
            send_text(phone,"Enter name:")
            return

    # NAME
    if s["step"]=="get_name":
        s["name"]=text
        s["step"]="get_address"
        send_text(phone,"Enter address:")
        return

    # ADDRESS + FINAL
    if s["step"]=="get_address":
        s["address"]=text
        total=cart_total(s["cart"])

        receipt = (
            f"Order Confirmed\n"
            f"{s['name']}\n"
            f"{s['address']}\n"
            f"{cart_text(s['cart'])}\n"
            f"Total: {total} SAR"
        )

        send_text(phone,receipt)
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
            handle_message(phone,msg["interactive"]["button_reply"]["id"],
                           msg["interactive"]["button_reply"]["id"])
        elif msg["type"]=="text":
            handle_message(phone,msg["text"]["body"])
    except:
        pass

    return "ok"

if __name__=="__main__":
    app.run(port=5000)