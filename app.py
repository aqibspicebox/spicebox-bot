from flask import Flask, request
import requests

app = Flask(__name__)

# ── Credentials ─────────────────────────
VERIFY_TOKEN = "spicebox123"
ACCESS_TOKEN = "EAAW66CLlGCsBRWxKx52Q7ZBSg3aZCAESrLd7EKt47jw4YF11UkA6buV4GqRozdS8oS7a2Ww60s7vfypTvOxyne4p4MC11kCJk49WoKbzQ8ZCC4ZA77WZBha3ZCzZCqPQ3zdJXBVm1hpdiXr9ysApkZBkKnKOOjXyHVfIXi3zVSmxj2dMuFyCQ1kREOZCJZCyqnthx8YZCOualx0MxqUkabZB7JpApSdd7EKlLtJ3otdAxcqoI6ZAUmbqRvAwQ8FcFW1ToZAnz0hZA4bqB2YPvLjxxSOqEqyGgj0m8XU0ADZC8gZDZD"
PHONE_NUMBER_ID = "1138025436056275"
OWNER_NUMBER = "966578042512"

IMG = "https://i.ibb.co/hR3bJgT3/Fries.png"

RESTAURANT_INFO = """🏪 *PASSSHION COOKING RESTAURANT*
📍 Ibn Haitam, Arabian Street
    Al Aziziyah District, Jeddah
    (Near Al Baik)

🥐 *Passion of Baking*
📍 Al Batarji Street
    Az Zahra District, Jeddah"""

# ── ORDER COUNTER ──────────────────────
def get_next_order_number():
    try:
        with open("order_counter.txt", "r") as f:
            num = int(f.read().strip())
    except:
        num = 0
    num += 1
    with open("order_counter.txt", "w") as f:
        f.write(str(num))
    return str(num).zfill(5)

def get_time():
    from datetime import datetime, timezone, timedelta
    tz = timezone(timedelta(hours=3))
    now = datetime.now(tz)
    return now.strftime("%d-%m-%Y %I:%M %p")

# ── MENU ───────────────────────────────
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
    data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
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
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}}
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
            "action": {"button": "View Options", "sections": sections}
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

# ── RECEIPT ────────────────────────────
def send_receipt(phone, order_num, cart, name, address):
    total = cart_total(cart)
    items_text = "\n".join([f"  ▪️ {i['name']} — {i['price']} SAR" for i in cart])

    customer_receipt = f"""╔══════════════════════╗
🍽️  *PASSSHION COOKING*
        *RESTAURANT*
╚══════════════════════╝

🧾 *ORDER RECEIPT*
━━━━━━━━━━━━━━━━━━━━━━
🔢 Order No: *#{order_num}*
👤 Name: *{name}*
📍 Address: *{address}*
━━━━━━━━━━━━━━━━━━━━━━

🛒 *Items Ordered:*
{items_text}

━━━━━━━━━━━━━━━━━━━━━━
💰 *Total: {total} SAR*
━━━━━━━━━━━━━━━━━━━━━━

📍 *Our Location:*
Ibn Haitam, Arabian Street
Al Aziziyah District, Jeddah
(Near Al Baik)

⏰ Your order is being
   prepared with ❤️

🙏 *Thank you for choosing*
*Passshion Cooking Restaurant!*"""

    owner_receipt = f"""🔔 *NEW ORDER ALERT!*
━━━━━━━━━━━━━━━━━━━━━━
🔢 Order No: *#{order_num}*
👤 Customer: *{name}*
📱 Phone: *+{phone}*
📍 Address: *{address}*
━━━━━━━━━━━━━━━━━━━━━━

🛒 *Items:*
{items_text}

━━━━━━━━━━━━━━━━━━━━━━
💰 *Total: {total} SAR*
⏰ Time: {get_time()}
━━━━━━━━━━━━━━━━━━━━━━"""

    send_text(phone, customer_receipt)
    send_text(OWNER_NUMBER, owner_receipt)

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
    return "\n".join([f"▪️ {i['name']} — {i['price']} SAR" for i in cart])

# ── MAIN FLOW ─────────────────────────
def handle_message(phone, text, button_id=None):
    s = get_session(phone)
    msg = (button_id or text).lower().strip()

    # WELCOME
    if msg in ["hi", "hello", "start"] or s["step"] == "welcome":
        s["step"] = "main"
        send_text(phone, f"""🌟 *Assalam o Alaikum!* 🌟

Welcome to
╔══════════════════════╗
🍽️  *PASSSHION COOKING*
        *RESTAURANT*
╚══════════════════════╝

{RESTAURANT_INFO}

_Freshly cooked with love_ ❤️""")
        send_buttons(phone, "What would you like to do?",
            [{"id": "order", "title": "🛒 Order Now"},
             {"id": "menu", "title": "📋 View Menu"}])
        return

    # MAIN
    if s["step"] == "main":
        if msg in ["order", "menu"]:
            s["step"] = "cuisine"
            send_buttons(phone, "🍽️ Select Category:",
                [{"id": "seekh", "title": "🥩 Seekh"},
                 {"id": "tikka", "title": "🍗 Tikka"},
                 {"id": "more_cat", "title": "📋 More..."}])
            return

    # MORE CATEGORIES
    if msg == "more_cat":
        s["step"] = "cuisine"
        send_buttons(phone, "🍽️ More Categories:",
            [{"id": "galawti", "title": "🍢 Galawti Kabab"},
             {"id": "rolls", "title": "🌯 Rolls"}])
        return

    # CUISINE
    if s["step"] == "cuisine":
        if msg in MENU:
            s["current_cuisine"] = msg
            s["step"] = "item"
            rows = []
            for i, (name, data) in enumerate(MENU[msg].items()):
                rows.append({
                    "id": f"item_{i}",
                    "title": name[:24],
                    "description": f"{data['price']} SAR"
                })
            send_list(phone, f"🍽️ *{msg.title()}* Menu:",
                [{"title": msg.title(), "rows": rows}])
            return

    # ITEM SELECT
    if s["step"] == "item":
        if msg.startswith("item_"):
            idx = int(msg.split("_")[1])
            items = list(MENU[s["current_cuisine"]].items())
            name, data = items[idx]
            s["selected"] = {"name": name, "price": data["price"], "img": data["img"]}
            s["step"] = "action"
            send_buttons(phone,
                f"🍽️ *{name}*\n💰 Price: *{data['price']} SAR*",
                [{"id": "view", "title": "🖼️ View Image"},
                 {"id": "add", "title": "✅ Order Now"}])
            return

    # ACTION
    if s["step"] == "action":
        if msg == "view":
            send_image(phone, s["selected"]["img"], s["selected"]["name"])
            send_buttons(phone, "What's next?",
                [{"id": "add", "title": "✅ Order Now"},
                 {"id": "back", "title": "🔙 Back"}])
            return

        if msg == "add":
            s["cart"].append(s["selected"])
            s["step"] = "more"
            send_buttons(phone,
                f"✅ *Added!*\n\n🛒 *Your Cart:*\n{cart_text(s['cart'])}\n\n💰 *Total: {cart_total(s['cart'])} SAR*",
                [{"id": "add_more", "title": "➕ Add More"},
                 {"id": "checkout", "title": "🧾 Checkout"}])
            return

        if msg == "back":
            s["step"] = "cuisine"
            send_buttons(phone, "🍽️ Select Category:",
                [{"id": "seekh", "title": "🥩 Seekh"},
                 {"id": "tikka", "title": "🍗 Tikka"},
                 {"id": "more_cat", "title": "📋 More..."}])
            return

    # MORE
    if s["step"] == "more":
        if msg == "add_more":
            s["step"] = "cuisine"
            send_buttons(phone, "🍽️ Select Category:",
                [{"id": "seekh", "title": "🥩 Seekh"},
                 {"id": "tikka", "title": "🍗 Tikka"},
                 {"id": "more_cat", "title": "📋 More..."}])
            return

        if msg == "checkout":
            s["step"] = "get_name"
            send_text(phone, "👤 Please enter your *Name*:")
            return

    # GET NAME
    if s["step"] == "get_name":
        s["name"] = text
        s["step"] = "get_address"
        send_text(phone, "📍 Please enter your *Delivery Address*:")
        return

    # GET ADDRESS + SEND RECEIPT
    if s["step"] == "get_address":
        s["address"] = text
        order_num = get_next_order_number()
        send_receipt(phone, order_num, s["cart"], s["name"], s["address"])
        sessions.pop(phone)
        return

# ── WEBHOOK ───────────────────────────
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "error"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        phone = msg["from"]

        if msg["type"] == "interactive":
            if "button_reply" in msg["interactive"]:
                bid = msg["interactive"]["button_reply"]["id"]
                handle_message(phone, bid, bid)
            elif "list_reply" in msg["interactive"]:
                lid = msg["interactive"]["list_reply"]["id"]
                handle_message(phone, lid, lid)
        elif msg["type"] == "text":
            handle_message(phone, msg["text"]["body"])
    except Exception as e:
        print("ERROR:", e)

    return "ok"

if __name__ == "__main__":
    app.run(port=5000)