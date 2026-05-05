from flask import Flask, request
import requests

app = Flask(__name__)

# ── Credentials ─────────────────────────
VERIFY_TOKEN = "spicebox123"
ACCESS_TOKEN = "EAAW66CLlGCsBRR3c8DdMGEyfdAHwbCvr3rBRXAUbe2SXJiGblikZAiJZBVDNZBSOWFaDPz889ZAmDpfOii1QcZA0VWkDnZAZAoNTT1k2nfA0qaylIaTTR2OGLIc18wWIvabPPTeMgkS7SrTTLupdXR0d8JkdAMXR0hWFNkfuZCB15q7UQf5ttB4ZARvr1iMmFUeqaf5j1OvVTKiZAmmhMWaDH5CLBg5QcLxGjz9ZAZAP0V0c9voMJZB37OrHmOjcmkJGV7XqbzE2QTcH6ZAuzqlxhgMMXgNfY91O34EMx1NAoZD"
PHONE_NUMBER_ID = "1138025436056275"

IMG = "https://i.ibb.co/hR3bJgT3/Fries.png"

# ── MENU ───────────────────────────────
MENU = {
    "seekh": {
        "Beef Seekh": {"price": 7, "img": IMG},
        "Chicken Seekh": {"price": 6, "img": IMG},
    },
    "tikka": {
        "Afghani Tikka": {"price": 8, "img": IMG},
        "Red Tikka": {"price": 8, "img": IMG},
    }
}

sessions = {}

# ── SEND FUNCTIONS ─────────────────────
def send_text(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
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
    if msg in ["hi", "hello", "start"] or s["step"] == "welcome":
        s["step"] = "main"
        send_buttons(phone, "Welcome! What you want?",
                     [{"id": "order", "title": "Order Now"}])
        return

    # MAIN
    if s["step"] == "main":
        if msg == "order":
            s["step"] = "cuisine"
            send_buttons(phone, "Select Category:",
                         [{"id": "seekh", "title": "Seekh"},
                          {"id": "tikka", "title": "Tikka"}])
            return

    # CATEGORY
    if s["step"] == "cuisine":
        if msg in MENU:
            s["current_cuisine"] = msg
            s["step"] = "item"

            items = MENU[msg]
            text_menu = "\n".join([f"{i+1}. {name} - {data['price']} SAR"
                                  for i, (name, data) in enumerate(items.items())])

            send_text(phone, f"Choose item:\n{text_menu}\nReply with number")
            return

    # ITEM SELECT
    if s["step"] == "item":
        try:
            idx = int(text) - 1
            items = list(MENU[s["current_cuisine"]].items())
            name, data = items[idx]

            s["selected"] = {"name": name, "price": data["price"]}
            s["step"] = "action"

            send_buttons(phone, f"{name} - {data['price']} SAR",
                         [{"id": "add", "title": "Add"}])
        except:
            send_text(phone, "Invalid choice")
        return

    # ACTION
    if s["step"] == "action":
        if msg == "add":
            s["cart"].append(s["selected"])
            s["step"] = "more"

            send_buttons(phone,
                         f"Added\n{cart_text(s['cart'])}\nTotal: {cart_total(s['cart'])} SAR",
                         [{"id": "more", "title": "More"},
                          {"id": "checkout", "title": "Checkout"}])
            return

    # MORE
    if s["step"] == "more":
        if msg == "more":
            s["step"] = "cuisine"
            send_buttons(phone, "Select Category:",
                         [{"id": "seekh", "title": "Seekh"},
                          {"id": "tikka", "title": "Tikka"}])
            return

        if msg == "checkout":
            s["step"] = "get_name"
            send_text(phone, "Enter your name:")
            return

    # GET NAME
    if s["step"] == "get_name":
        s["name"] = text
        s["step"] = "get_address"
        send_text(phone, "Enter address:")
        return

    # GET ADDRESS + FINAL RECEIPT
    if s["step"] == "get_address":
        s["address"] = text
        total = cart_total(s['cart'])

        receipt = (
            f"Order Confirmed\n"
            f"{s['name']}\n"
            f"{s['address']}\n"
            f"{cart_text(s['cart'])}\n"
            f"Total: {total} SAR"
        )

        send_text(phone, receipt)
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
            handle_message(phone, msg["interactive"]["button_reply"]["id"],
                           msg["interactive"]["button_reply"]["id"])

        elif msg["type"] == "text":
            handle_message(phone, msg["text"]["body"])

    except:
        pass

    return "ok"

if __name__ == "__main__":
    app.run(port=5000)