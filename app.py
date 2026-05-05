from flask import Flask, request
import requests
import json

app = Flask(**name**)

# ── Credentials ──────────────────────────────────────────

VERIFY_TOKEN = “spicebox123”
ACCESS_TOKEN = “EAAW66CLlGCsBRUhkIhGL9K0uDhggQynmB1JLlZCbpGeiHwingMt9jiOOmNWjB22ifmNvN7QlZCqV39zysozeYCSZBgg4AKp7dS9TLxZAcZAufAbPqZBQECWtxSe2MSHeZAmrZBBsm8LrZBv9bL0ItMvvIlxuKn3RTb633MJLYtcSK6KIisVn0cOMt7uGfAhKARjkNILxWoEHE98ogrCSz8r6x2rKZBJIo7ts04lhmKWPMqeVnZAibXgzkXuWhbKwa6Ipis33c15wopoKtkUMZCss50iDOGthFYktgZCG63KcZD”
PHONE_NUMBER_ID = “1138025436056275”

# ── Menu ─────────────────────────────────────────────────

MENU = {
“desi”: {
“Chicken Karahi”: 700,
“Chicken Handi”: 1250,
“Mutton Karahi”: 2100,
“Chicken Biryani”: 350,
“Bar B Q Boti”: 699,
“Seek Kabab”: 699,
},
“chinese”: {
“Hot & Sour Soup”: 250,
“Chicken Chowmein”: 750,
“Manchurian Chicken”: 892,
“Egg Fried Rice”: 699,
“Chicken Noodles”: 450,
},
“fries”: {
“Plane Fries”: 219,
“Flavour Fries”: 280,
“Pizza Fries”: 470,
“Nuggets 6 Pcs”: 350,
“Appetizer with Dip”: 599,
}
}

# ── User Sessions ─────────────────────────────────────────

sessions = {}

# ══════════════════════════════════════════════════════════

# SEND FUNCTIONS

# ══════════════════════════════════════════════════════════

def send_text(to, text):
“”“Simple text message”””
url = f”https://graph.facebook.com/v18.0/{1138025436056275}/messages”
headers = {
“Authorization”: f”Bearer {EAAW66CLlGCsBRfmAKY3TWqDJGJZAxLpvTnqz4N8E5do34XVF98V3gy1xX98LszhJkC2Q9FD98g3fmUVHyKmWqhdq0VAh1zbyi5ESLQQs5CmFlm3UyPcLDg5uCYNk8QMcEw9XcrZC0ZAieLb4ymP2bWaUWuHyX9CqIKDjxRPFw0JyUcqevGDcsmZB8bYbO05nhR0PRx8OVXZAAFd2i1Y64JOag5i9uj3PdSf9PTSDmbvZALWEtiybgKx9ufoBd5qT5E0h9PJGnVLqLrW0MM7HFMDWDwaqpWSZC4j6AZDZD}”,
“Content-Type”: “application/json”
}
data = {
“messaging_product”: “whatsapp”,
“to”: to,
“type”: “text”,
“text”: {“body”: text}
}
requests.post(url, headers=headers, json=data)
def send_buttons(to, text, buttons):
“””
Send message with up to 3 clickable buttons
buttons = [{“id”: “btn1”, “title”: “Button 1”}, …]
“””
url = f”https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages”
headers = {
“Authorization”: f”Bearer {ACCESS_TOKEN}”,
“Content-Type”: “application/json”
}
data = {
“messaging_product”: “whatsapp”,
“to”: to,
“type”: “interactive”,
“interactive”: {
“type”: “button”,
“body”: {“text”: text},
“action”: {
“buttons”: [
{
“type”: “reply”,
“reply”: {
“id”: btn[“id”],
“title”: btn[“title”][:20]
}
} for btn in buttons[:3]
]
}
}
}
requests.post(url, headers=headers, json=data)

def send_list(to, text, sections):
“””
Send list menu with multiple items
sections = [{“title”: “Category”, “rows”: [{“id”: “id1”, “title”: “Item”, “description”: “Rs 500”}]}]
“””
url = f”https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages”
headers = {
“Authorization”: f”Bearer {ACCESS_TOKEN}”,
“Content-Type”: “application/json”
}
data = {
“messaging_product”: “whatsapp”,
“to”: to,
“type”: “interactive”,
“interactive”: {
“type”: “list”,
“body”: {“text”: text},
“action”: {
“button”: “View Options”,
“sections”: sections
}
}
}
requests.post(url, headers=headers, json=data)

def send_image(to, image_url, caption=””):
“”“Send image with optional caption”””
url = f”https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages”
headers = {
“Authorization”: f”Bearer {ACCESS_TOKEN}”,
“Content-Type”: “application/json”
}
data = {
“messaging_product”: “whatsapp”,
“to”: to,
“type”: “image”,
“image”: {
“link”: image_url,
“caption”: caption
}
}
requests.post(url, headers=headers, json=data)

# ══════════════════════════════════════════════════════════

# HELPER FUNCTIONS

# ══════════════════════════════════════════════════════════

def get_session(phone):
if phone not in sessions:
sessions[phone] = {
“step”: “welcome”,
“cart”: [],
“name”: “”,
“location”: “”,
“phone_num”: “”,
“current_cuisine”: “”
}
return sessions[phone]

def cart_total(cart):
return sum(item[“price”] for item in cart)

def cart_text(cart):
return “\n”.join([f”• {i[‘name’]} — Rs {i[‘price’]}” for i in cart])

# ══════════════════════════════════════════════════════════

# MAIN FLOW

# ══════════════════════════════════════════════════════════

def handle_message(phone, text, button_id=None):
s = get_session(phone)

```
# Use button_id if available, else use text
msg = (button_id or text).strip().lower()

# ── WELCOME ──────────────────────────────────────────
if msg in ["hi", "hello", "salam", "start", "helo", "hey"] or s["step"] == "welcome":
    s["step"] = "main"
    s["cart"] = []
    send_buttons(phone,
        "🌶️ *Welcome to Spice Box!*\n_Authentic Taste — DHA Phase 9, Lahore_\n\nHow can I help you today?",
        buttons=[
            {"id": "order", "title": "🛒 Order Now"},
            {"id": "menu", "title": "📋 View Menu"},
            {"id": "help", "title": "ℹ️ Help"},
        ]
    )
    return

# ── MAIN MENU ─────────────────────────────────────────
if s["step"] == "main":
    if msg in ["order", "order now"]:
        s["step"] = "cuisine"
        send_buttons(phone,
            "🍽️ *Select Cuisine Type:*",
            buttons=[
                {"id": "desi", "title": "🍛 Desi Cuisine"},
                {"id": "chinese", "title": "🍜 Chinese"},
                {"id": "fries", "title": "🍟 Fries & Snacks"},
            ]
        )

    elif msg in ["menu", "view menu"]:
        # Send menu image first
        send_image(phone,
            "https://i.imgur.com/spicebox_menu.jpg",
            "📋 Spice Box Full Menu"
        )
        # Then send text menu
        menu_text = "📋 *Spice Box Menu:*\n\n"
        menu_text += "🍛 *DESI CUISINE:*\n"
        for k, v in MENU["desi"].items():
            menu_text += f"• {k} — Rs {v}\n"
        menu_text += "\n🍜 *CHINESE:*\n"
        for k, v in MENU["chinese"].items():
            menu_text += f"• {k} — Rs {v}\n"
        menu_text += "\n🍟 *FRIES & SNACKS:*\n"
        for k, v in MENU["fries"].items():
            menu_text += f"• {k} — Rs {v}\n"
        send_text(phone, menu_text)
        send_buttons(phone,
            "Ready to order? 😊",
            buttons=[
                {"id": "order", "title": "🛒 Order Now"},
            ]
        )

    elif msg in ["help"]:
        send_text(phone,
            "📞 *Spice Box Help:*\n\n"
            "📍 Plaza B3, CCA Phase-9, DHA Lahore\n"
            "📞 0329-4799993\n"
            "📞 042-37250019\n\n"
            "Reply *hi* to start ordering!"
        )
    return

# ── CUISINE SELECTION ─────────────────────────────────
if s["step"] == "cuisine":
    if msg in ["desi", "chinese", "fries"]:
        s["current_cuisine"] = msg
        s["step"] = "item"
        
        items = list(MENU[msg].items())
        
        # Send as list menu
        rows = []
        for name, price in items:
            rows.append({
                "id": f"item_{name}_{price}",
                "title": name[:24],
                "description": f"Rs {price}"
            })
        
        cuisine_names = {
            "desi": "🍛 Desi Cuisine",
            "chinese": "🍜 Chinese",
            "fries": "🍟 Fries & Snacks"
        }
        
        send_list(phone,
            f"*{cuisine_names[msg]}*\nSelect your item:",
            sections=[{
                "title": cuisine_names[msg],
                "rows": rows
            }]
        )
    return

# ── ITEM SELECTION ────────────────────────────────────
if s["step"] == "item":
    if msg.startswith("item_") or button_id and button_id.startswith("item_"):
        parts = (button_id or msg).split("_", 2)
        if len(parts) >= 3:
            item_info = parts[2].rsplit("_", 1)
            item_name = item_info[0]
            item_price = int(item_info[1])
            
            s["cart"].append({"name": item_name, "price": item_price})
            s["step"] = "more"
            
            send_buttons(phone,
                f"✅ *{item_name}* added!\n\n"
                f"🛒 *Cart:*\n{cart_text(s['cart'])}\n\n"
                f"💰 Total: Rs {cart_total(s['cart'])}",
                buttons=[
                    {"id": "add_more", "title": "➕ Add More"},
                    {"id": "checkout", "title": "✅ Checkout"},
                ]
            )
    return

# ── ADD MORE OR CHECKOUT ──────────────────────────────
if s["step"] == "more":
    if msg in ["add_more", "add more"]:
        s["step"] = "cuisine"
        send_buttons(phone,
            "🍽️ *Select Cuisine:*",
            buttons=[
                {"id": "desi", "title": "🍛 Desi Cuisine"},
                {"id": "chinese", "title": "🍜 Chinese"},
                {"id": "fries", "title": "🍟 Fries & Snacks"},
            ]
        )
    elif msg in ["checkout"]:
        s["step"] = "name"
        send_text(phone, "👤 Please enter your *name*:")
    return

# ── COLLECT NAME ──────────────────────────────────────
if s["step"] == "name":
    s["name"] = text.title()
    s["step"] = "location"
    send_text(phone, "📍 Please enter your *delivery address*:")
    return

# ── COLLECT LOCATION ──────────────────────────────────
if s["step"] == "location":
    s["location"] = text.title()
    s["step"] = "phone_num"
    send_text(phone, "📱 Please enter your *phone number*:")
    return

# ── COLLECT PHONE ─────────────────────────────────────
if s["step"] == "phone_num":
    s["phone_num"] = text
    s["step"] = "confirm"
    
    summary = (
        f"📋 *Order Summary:*\n\n"
        f"{cart_text(s['cart'])}\n\n"
        f"👤 Name: {s['name']}\n"
        f"📍 Address: {s['location']}\n"
        f"📱 Phone: {s['phone_num']}\n\n"
        f"💰 *Total: Rs {cart_total(s['cart'])}*"
    )
    
    send_buttons(phone, summary,
        buttons=[
            {"id": "confirm", "title": "✅ Confirm Order"},
            {"id": "cancel", "title": "❌ Cancel"},
        ]
    )
    return

# ── CONFIRM ORDER ─────────────────────────────────────
if s["step"] == "confirm":
    if msg in ["confirm"]:
        total = cart_total(s["cart"])
        send_text(phone,
            f"✅ *Order Confirmed!*\n\n"
            f"🙏 Thank you *{s['name']}*!\n"
            f"Your food is being prepared 🔥\n\n"
            f"📍 Delivery to: {s['location']}\n"
            f"💰 Total: Rs {total}\n\n"
            f"📞 For queries: 0329-4799993\n\n"
            f"_Spice Box — Authentic Taste_ 🌶️"
        )
        sessions.pop(phone, None)
        
    elif msg in ["cancel"]:
        sessions.pop(phone, None)
        send_buttons(phone,
            "❌ Order cancelled!\nWant to start again?",
            buttons=[
                {"id": "order", "title": "🛒 Order Again"},
            ]
        )
    return

# ── DEFAULT ───────────────────────────────────────────
send_buttons(phone,
    "🌶️ *Spice Box*\nHow can I help you?",
    buttons=[
        {"id": "order", "title": "🛒 Order Now"},
        {"id": "menu", "title": "📋 View Menu"},
        {"id": "help", "title": "ℹ️ Help"},
    ]
)
```

# ══════════════════════════════════════════════════════════

# WEBHOOK

# ══════════════════════════════════════════════════════════

@app.route(”/webhook”, methods=[“GET”])
def verify():
mode = request.args.get(“hub.mode”)
token = request.args.get(“hub.verify_token”)
challenge = request.args.get(“hub.challenge”)
if mode == “subscribe” and token == VERIFY_TOKEN:
return challenge, 200
return “Error”, 403

@app.route(”/webhook”, methods=[“POST”])
def webhook():
data = request.get_json()
try:
entry = data[“entry”][0]
changes = entry[“changes”][0]
value = changes[“value”]

```
    if "messages" in value:
        msg = value["messages"][0]
        phone = msg["from"]
        
        # Check if button reply
        if msg["type"] == "interactive":
            interactive = msg["interactive"]
            
            if interactive["type"] == "button_reply":
                button_id = interactive["button_reply"]["id"]
                handle_message(phone, button_id, button_id=button_id)
                
            elif interactive["type"] == "list_reply":
                list_id = interactive["list_reply"]["id"]
                handle_message(phone, list_id, button_id=list_id)
                
        # Regular text message
        elif msg["type"] == "text":
            text = msg["text"]["body"]
            handle_message(phone, text)
            
except Exception as e:
    print(f"Error: {e}")

return "OK", 200
```
if **name** == “**main**”:
app.run(debug=True, port=5000)