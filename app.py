from flask import Flask, request
import requests
import json

app = Flask(__name__)

# ── Credentials ──────────────────
VERIFY_TOKEN = "spicebox123"
ACCESS_TOKEN = "EAAW66CLlGCsBRZAzaMnt0ZAVKy8dEVqgDKKAeD33gtSd4hRzExrkftaNZBDfJi1tiSmxfBelUNfyRvYIsxyk02ZAZANgqZBzatJ6vfb6wfrw8s21yBL5uzFByaVAXb0zpUAlLhVZCyC03renMlXA3pKj4R4hyeVmdGZCjP18ylZCuBJAf6sjlOvo4pjydXqFduzdZA0vzZBQQnA7ZAk8VTlROxeESRCMUnTcZCqQbP7vTJWGIwwG55ZAHtmwDZCdQk2EcBaV2JvJKZCkkYUPwNQjgdZC1leCeb4Fnbm8ovNZAEFSkZD"
PHONE_NUMBER_ID = "1138025436056275"

# ── Menu ─────────────────────────
MENU = {
    "desi": {
        "Chicken Karahi": 700,
        "Chicken Handi": 1250,
        "Mutton Karahi": 2100,
        "Chicken Biryani": 350,
    },
    "chinese": {
        "Hot & Sour Soup": 250,
        "Chicken Chowmein": 750,
        "Manchurian Chicken": 892,
        "Egg Fried Rice": 699,
    },
    "fries": {
        "Plane Fries": 219,
        "Flavour Fries": 280,
        "Pizza Fries": 470,
        "Nuggets (6 Pcs)": 350,
    }
}

# ── User Sessions ─────────────────
sessions = {}

def send_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, headers=headers, json=data)

def get_session(phone):
    if phone not in sessions:
        sessions[phone] = {
            "step": "welcome",
            "cart": [],
            "name": "",
            "location": "",
            "phone": ""
        }
    return sessions[phone]

def handle_message(phone, text):
    s = get_session(phone)
    text = text.strip().lower()

    if s["step"] == "welcome" or text in ["hi","hello","سلام","مرحبا","helo"]:
        s["step"] = "main"
        send_message(phone,
            "🌶️ *Welcome to Spice Box!*\n"
            "_Authentic Taste_\n\n"
            "Reply with:\n"
            "1️⃣ Order Now\n"
            "2️⃣ View Menu\n"
            "3️⃣ Help"
        )

    elif s["step"] == "main":
        if text in ["1","order now","order"]:
            s["step"] = "cuisine"
            send_message(phone,
                "🍽️ *Select Cuisine:*\n\n"
                "1️⃣ 🍛 Desi Cuisine\n"
                "2️⃣ 🍜 Chinese Cuisine\n"
                "3️⃣ 🍟 Fries & Snacks"
            )
        elif text in ["2","view menu","menu"]:
            msg = "📋 *Spice Box Menu:*\n\n"
            msg += "🍛 *DESI:*\n"
            for k,v in MENU["desi"].items():
                msg += f"• {k} — Rs {v}\n"
            msg += "\n🍜 *CHINESE:*\n"
            for k,v in MENU["chinese"].items():
                msg += f"• {k} — Rs {v}\n"
            msg += "\n🍟 *FRIES:*\n"
            for k,v in MENU["fries"].items():
                msg += f"• {k} — Rs {v}\n"
            msg += "\nReply *1* to Order Now!"
            send_message(phone, msg)
        else:
            send_message(phone,"📞 Call: 0329-4799993\nReply *1* to Order!")

    elif s["step"] == "cuisine":
        if text in ["1","desi"]:
            s["step"] = "item_desi"
            msg = "🍛 *Desi Menu:*\n\n"
            for i,(k,v) in enumerate(MENU["desi"].items(),1):
                msg += f"{i}️⃣ {k} — Rs {v}\n"
            send_message(phone, msg)
        elif text in ["2","chinese"]:
            s["step"] = "item_chinese"
            msg = "🍜 *Chinese Menu:*\n\n"
            for i,(k,v) in enumerate(MENU["chinese"].items(),1):
                msg += f"{i}️⃣ {k} — Rs {v}\n"
            send_message(phone, msg)
        elif text in ["3","fries"]:
            s["step"] = "item_fries"
            msg = "🍟 *Fries Menu:*\n\n"
            for i,(k,v) in enumerate(MENU["fries"].items(),1):
                msg += f"{i}️⃣ {k} — Rs {v}\n"
            send_message(phone, msg)

    elif s["step"] in ["item_desi","item_chinese","item_fries"]:
        cat = s["step"].replace("item_","")
        items = list(MENU[cat].items())
        try:
            idx = int(text) - 1
            name, price = items[idx]
            s["cart"].append({"name": name, "price": price})
            s["step"] = "more"
            send_message(phone,
                f"✅ *{name}* added! Rs {price}\n\n"
                f"🛒 Cart Total: Rs {sum(i['price'] for i in s['cart'])}\n\n"
                "Reply:\n"
                "1️⃣ Add More\n"
                "2️⃣ Checkout"
            )
        except:
            send_message(phone,"❌ Sahi number likhein!")

    elif s["step"] == "more":
        if text in ["1","add more"]:
            s["step"] = "cuisine"
            send_message(phone,
                "🍽️ *Select Cuisine:*\n\n"
                "1️⃣ 🍛 Desi\n"
                "2️⃣ 🍜 Chinese\n"
                "3️⃣ 🍟 Fries"
            )
        elif text in ["2","checkout"]:
            s["step"] = "name"
            send_message(phone,"👤 Apna *naam* likhein:")

    elif s["step"] == "name":
        s["name"] = text.title()
        s["step"] = "location"
        send_message(phone,"📍 *Delivery address* likhein:")

    elif s["step"] == "location":
        s["location"] = text.title()
        s["step"] = "phone"
        send_message(phone,"📱 *Phone number* likhein:")

    elif s["step"] == "phone":
        s["phone"] = text
        s["step"] = "confirm"
        cart_text = "\n".join([f"• {i['name']} — Rs {i['price']}" for i in s["cart"]])
        total = sum(i["price"] for i in s["cart"])
        send_message(phone,
            f"📋 *Order Summary:*\n\n"
            f"{cart_text}\n\n"
            f"👤 Name: {s['name']}\n"
            f"📍 Address: {s['location']}\n"
            f"📱 Phone: {s['phone']}\n\n"
            f"💰 *Total: Rs {total}*\n\n"
            "Reply:\n"
            "✅ *confirm* — Order karo\n"
            "❌ *cancel* — Cancel karo"
        )

    elif s["step"] == "confirm":
        if text == "confirm":
            total = sum(i["price"] for i in s["cart"])
            send_message(phone,
                f"✅ *Order Confirmed!*\n\n"
                f"🙏 Shukriya {s['name']}!\n"
                f"Aapka khana tayar ho raha hai 🔥\n"
                f"Total: Rs {total}\n\n"
                f"📞 0329-4799993"
            )
            sessions.pop(phone)
        elif text == "cancel":
            sessions.pop(phone)
            send_message(phone,"❌ Order cancel ho gaya!\nReply *hi* to start again!")

# ── Webhook ───────────────────────
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Error", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        if "messages" in value:
            msg = value["messages"][0]
            phone = msg["from"]
            text = msg["text"]["body"]
            handle_message(phone, text)
    except:
        pass
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)