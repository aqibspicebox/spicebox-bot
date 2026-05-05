from flask import Flask, request
import requests

app = Flask(__name__)

# ── Credentials ─────────────────────────
VERIFY_TOKEN = "spicebox123"
ACCESS_TOKEN = "EAAW66CLlGCsBRR3c8DdMGEyfdAHwbCvr3rBRXAUbe2SXJiGblikZAiJZBVDNZBSOWFaDPz889ZAmDpfOii1QcZA0VWkDnZAZAoNTT1k2nfA0qaylIaTTR2OGLIc18wWIvabPPTeMgkS7SrTTLupdXR0d8JkdAMXR0hWFNkfuZCB15q7UQf5ttB4ZARvr1iMmFUeqaf5j1OvVTKiZAmmhMWaDH5CLBg5QcLxGjz9ZAZAP0V0c9voMJZB37OrHmOjcmkJGV7XqbzE2QTcH6ZAuzqlxhgMMXgNfY91O34EMx1NAoZD"
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
        "Tikka Platter": {"price": 40, "img": IMG},
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
def send_receipt(phone, order_num, cart):
    total = cart_total(cart)
    items_text = "\n".join([f"  ▪️ {i['name']} — {i['price']} SAR" for i in cart])

    customer_receipt = f"""╔══════════════════════╗
🍽️  *PASSSHION COOKING*
        *RESTAURANT*
╚══════════════════════╝

🧾 *ORDER RECEIPT*
━━━━━━━━━━━━━━━━━━━━━━
🔢 Order No: *#{order_num}*
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
*Passshion Cooking Restaurant!*

_For queries, contact us_
_on this number_ 📞"""

    owner_receipt = f"""🔔 *NEW ORDER ALERT!*
━━━━━━━━━━━━━━━━━━━━━━
🔢 Order No: *#{order_num}*
📱 Customer: *+{phone}*
━━━━━━━━━━━━━━━━━━━━━━

🛒 *Items:*
{items_text}

━━━━━━━━━━━━━━━━━━━━━━
💰 *Total: {total} SAR*
━━━━━━━━━━━━━━━━━━━━━━
⏰ Time: {get_time()}"""

    send_text(phone, customer_receipt)
    send_text(OWNER_NUMBER, owner_receipt)

def get_time():
    from datetime import datetime, timezone, timedelta
    tz = timezone(timedelta(hours=3))  # Saudi Arabia UTC+3
    now = datetime.now(tz)
    return now.strftime("%d-%m-%Y %I:%M %p")

# ── HELPERS ────────────────────────────
def get_session(phone):
    if phone not in sessions:
        sessions[phone] = {"step": "welcome", "cart": [], "current_cuisine": ""}
    return sessions[phone]

def cart_total(cart):
    return sum(i["price"] for i in cart)

def cart_text(cart):
    return "\n".join([f"▪️ {i['name']} — {i['price']} SAR" for i in cart])

# ── MAIN FLOW ─────────────────────────
def handle_message(phone, text, button_id=None):
    s = get_session(phone)
    msg = (button_id or text).lower()

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
            [{"id": "order", "title": "🛒 Order Now"}, {"id": "menu", "title": "📋 View Menu"}])
        return

    # MAIN
    if s["step"] == "main":
        if msg in ["order", "menu"]:
            s["step"] = "cuisine"
            send_buttons(phone, "🍽️ Select Category:",
                [{"id": "seekh", "title": "🥩 Seekh"}, {"id": "tikka", "title": "🍗 Tikka"}, {"id": "more_cat", "title": "📋 More..."}])
            return

    # MORE CATEGORIES
    if msg == "more_cat":
        s["step"] = "cuisine"
        send_buttons(phone, "🍽️ Select Category:",
            [{"id": "galawti", "title": "🍢 Galawti Kabab"}, {"id": "rolls", "title": "🌯 Rolls"}])
        return

    # CUISINE
    if s["step"] == "cuisine":
        if msg in MENU:
            s["current_cuisine"] = msg
            s["step"] = "item"

            rows = []
            for i, (name, data) in enumerate(MENU[msg].items()):
                rows.append({"id": f"item_{i}", "title": name[:24], "description": f"{data['price']} SAR"})

            send_list(phone, f"🍽️ *{msg.title()}* Menu:", [{"title": msg.title(), "rows": rows}])
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
                [{"id": "view", "title": "🖼️ View Image"}, {"id": "add", "title": "✅ Order Now"}])
            return

    # ACTION
    if s["step"] == "action":
        if msg == "view":
            send_image(phone, s["selected"]["img"], s["selected"]["name"])
            send_buttons(phone, "What's next?",
                [{"id": "add", "title": "✅ Order Now"}, {"id": "back", "title": "🔙 Back"}])
            return

        if msg == "add":
            s["cart"].append(s["selected"])
            s["step"] = "more"
            send_buttons(phone,
                f"✅ *Added to cart!*\n\n🛒 *Your Cart:*\n{cart_text(s['cart'])}\n\n💰 *Total: {cart_total(s['cart'])} SAR*",
                [{"id": "more", "title": "➕ Add More"}, {"id": "checkout", "title": "🧾 Checkout"}])
            return

        if msg == "back":
            s["step"] = "cuisine"
            send_buttons(phone, "🍽️ Select Category:",
                [{"id": "seekh", "title": "🥩 Seekh"}, {"id": "tikka", "title": "🍗 Tikka"}, {"id": "more_cat", "title": "📋 More..."}])
            return

    # MORE
    if s["step"] == "more":
        if msg == "more":
            s["step"] = "cuisine"
            send_buttons(phone, "🍽️ Select Category:",
                [{"id": "seekh", "title": "🥩 Seekh"}, {"id": "tikka", "title": "🍗 Tikka"}, {"id": "more_cat", "title": "📋 More..."}])
            return

        if msg == "checkout":
            order_num = get_next_order_number()
            send_receipt(phone, order_num, s["cart"])
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
                handle_message(phone, msg["interactive"]["button_reply"]["id"], msg["interactive"]["button_reply"]["id"])
            elif "list_reply" in msg["interactive"]:
                handle_message(phone, msg["interactive"]["list_reply"]["id"], msg["interactive"]["list_reply"]["id"])
        elif msg["type"] == "text":
            handle_message(phone, msg["text"]["body"])
    except:
        pass

    return "ok"

if __name__ == "__main__":
    app.run(port=5000)