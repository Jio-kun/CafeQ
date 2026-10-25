from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import random
import string
import os
from io import BytesIO
import qrcode

app = Flask(__name__)
app.secret_key = "change-this-demo-key"

# Menu items and prices from the Cafe Q menu PDF.
MENU = [
    (1, "Coffee Special", "Spanish Latte", 85, "Espresso, steamed whole milk and sweetened condensed milk."),
    (2, "Coffee Special", "Barako Brown Sugar Latte", 75, "Batangas Kapeng Barako espresso, brown sugar syrup, fresh milk and muscovado."),
    (3, "Coffee Special", "Tablea Mocha Crunch", 85, "Espresso, local tablea chocolate, steamed milk and Choc-Nut or Hani crumbs."),
    (4, "Coffee Special", "Iced Calamansi Cold Brew", 70, "Cold brew with calamansi juice, honey and calamansi slices."),
    (5, "Cream-Based Frappes (Coffee-Free)", "Ube Macapuno Velvet", 95, "Blended milk, ube halaya, macapuno, whipped cream and ube powder."),
    (6, "Cream-Based Frappes (Coffee-Free)", "Choc-Nut Supreme", 85, "Creamy blended base, Choc-Nut, chocolate syrup and whipped cream."),
    (7, "Cream-Based Frappes (Coffee-Free)", "Buko Pandan Cream", 85, "Coconut milk, pandan, whipped cream and toasted pinipig."),
    (8, "Cream-Based Frappes (Coffee-Free)", "Mango Graham Float", 95, "Mango puree, milk, ice, Graham crackers and whipped cream."),
    (9, "Non-Coffee Lattes & Teas", "Iced Strawberry Matcha", 90, "Matcha layered over milk and Philippine strawberry jam or puree."),
    (10, "Non-Coffee Lattes & Teas", "Pandan Vanilla Coconut Pandan", 75, "Infused milk and vanilla syrup, served over ice."),
    (11, "Non-Coffee Lattes & Teas", "Warm Tsokolate with Milk", 65, "Tablea cocoa, fresh milk, cinnamon and coconut sugar."),
    (12, "Tropical Refreshers", "Calamansi Hibiscus Fizz", 65, "Hibiscus tea, calamansi juice, simple syrup and soda water."),
    (13, "Tropical Refreshers", "Green Apple Jasmine Tea with Chia", 60, "Jasmine green tea, green apple syrup and chia seeds."),
    (14, "Tropical Refreshers", "Guyabano Passionfruit Sparkler", 65, "Guyabano juice, passionfruit syrup and sparkling water or Sprite."),
    (15, "Cake and Pastries", "Ube Cheese Pandesal", 25, "Ube dough with ube halaya and quick-melt cheese. ₱25 each or 3 for ₱70."),
    (16, "Cake and Pastries", "Classic Queso Ensaymada", 45, "Buttery brioche-style pastry topped with sugar and queso de bola."),
    (17, "Cake and Pastries", "Spanish Bread Bun", 20, "Soft bread with buttery brown sugar and breadcrumb filling."),
    (18, "Cake and Pastries", "Sylvanas (Classic & Matcha)", 35, "Buttercream sandwich cookies with cashew meringue and cake crumbs. ₱35 each or 3 for ₱100."),
    (19, "Cake and Pastries", "Choc-Nut Chunk Cookie", 45, "Brown butter cookie with milk chocolate chunks and Choc-Nut."),
    (20, "Cake and Pastries", "Tablea Dark Chocolate Fudge Cookie", 50, "Double chocolate cookie made with local tablea and sea salt."),
    (21, "Cake and Pastries", "Ube White Chocolate Crinkle", 40, "Ube crinkle cookie with a white chocolate center."),
    (22, "Cake and Pastries", "Biscoff & Caramel Cookie", 55, "Vanilla cookie dough with Lotus Biscoff spread and crushed cookies."),
    (23, "Slices & Cakes", "Mango Graham Float Cake", 75, "Graham crackers, sweetened cream and Cebu mangoes. Price per slice."),
    (24, "Slices & Cakes", "Bibingka Basque Burnt Cheesecake", 95, "Burnt cheesecake baked on banana leaves with salted egg and cheddar. Price per slice."),
    (25, "Slices & Cakes", "Calamba Coconut Pie (Buko Pie)", 55, "Pie crust filled with young coconut and creamy custard. Price per slice.")
]
STAFF_USER = "staff"
STAFF_PASS = "cafeq123"  # Demo password for school prototype only.

# Keep orders on the server instead of inside the browser session cookie.
# This is simple for a school demo; orders reset when the app is restarted.
ORDERS = []

def menu_dicts():
    return [dict(id=i, category=c, name=n, price=p, description=d) for i, c, n, p, d in MENU]

def cart_items():
    cart = session.get("cart", {})
    result = []
    for item in menu_dicts():
        qty = int(cart.get(str(item["id"]), 0))
        if qty:
            item["qty"] = qty
            item["line_total"] = qty * item["price"]
            result.append(item)
    return result

def total():
    return sum(item["line_total"] for item in cart_items())

def staff_only():
    return session.get("staff_logged_in", False)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/menu")
def menu():
    return render_template("menu.html", menu=menu_dicts())

@app.route("/qr")
def qr_page():
    # Open this page to display the QR code customers scan.
    menu_url = os.environ.get("CAFEQ_BASE_URL", request.host_url.rstrip("/")) + "/menu"
    return render_template("qr.html", menu_url=menu_url)

@app.route("/qr.png")
def qr_image():
    # The QR code opens the CafeQ menu page.
    menu_url = os.environ.get("CAFEQ_BASE_URL", request.host_url.rstrip("/")) + "/menu"
    qr = qrcode.QRCode(box_size=8, border=3)
    qr.add_data(menu_url)
    qr.make(fit=True)
    picture = qr.make_image(fill_color="black", back_color="white")
    image_file = BytesIO()
    picture.save(image_file, format="PNG")
    image_file.seek(0)
    return send_file(image_file, mimetype="image/png")

@app.route("/add/<int:item_id>", methods=["POST"])
def add(item_id):
    if not any(row[0] == item_id for row in MENU):
        return redirect(url_for("menu"))
    cart = session.get("cart", {})
    key = str(item_id)
    cart[key] = int(cart.get(key, 0)) + 1
    session["cart"] = cart
    flash("Added to cart!")
    return redirect(url_for("menu"))

@app.route("/cart")
def cart():
    return render_template("cart.html", items=cart_items(), total=total())

@app.route("/quantity/<int:item_id>/<action>", methods=["POST"])
def quantity(item_id, action):
    cart = session.get("cart", {})
    key = str(item_id)
    if key in cart:
        cart[key] = int(cart[key]) + (1 if action == "plus" else -1)
        if cart[key] <= 0:
            cart.pop(key)
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items = cart_items()
    if not items:
        flash("Your cart is empty.")
        return redirect(url_for("menu"))
    if request.method == "POST":
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        order = {
            "number": random.randint(100, 999),
            "code": code,
            "customer": request.form.get("customer", "").strip() or "CafeQ Guest",
            "type": request.form.get("type", "Takeout"),
            "items": items,
            "total": total(),
            "status": "Pending Payment"
        }
        ORDERS.insert(0, order)
        customer_codes = session.get("customer_order_codes", [])
        customer_codes.insert(0, code)
        session["customer_order_codes"] = customer_codes
        session["cart"] = {}
        return render_template("confirmation.html", order=order)
    return render_template("checkout.html", items=items, total=total())

@app.route("/my-order")
def my_order():
    customer_codes = session.get("customer_order_codes", [])
    customer_orders = [order for order in ORDERS if order["code"] in customer_codes]
    return render_template("orders.html", orders=customer_orders)

@app.route("/staff/login", methods=["GET", "POST"])
def staff_login():
    if request.method == "POST":
        if request.form.get("username") == STAFF_USER and request.form.get("password") == STAFF_PASS:
            session["staff_logged_in"] = True
            return redirect(url_for("staff"))
        flash("Wrong username or password.")
    return render_template("login.html")

@app.route("/staff/logout")
def staff_logout():
    session.pop("staff_logged_in", None)
    return redirect(url_for("home"))

@app.route("/staff", methods=["GET", "POST"])
def staff():
    if not staff_only():
        return redirect(url_for("staff_login"))
    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        order = next((o for o in ORDERS if o["code"] == code), None)
        if order:
            session["selected_code"] = code
            flash("Order found. Review the order below.")
        else:
            session.pop("selected_code", None)
            flash("Code not found.")
        return redirect(url_for("staff"))
    return render_template("staff.html", orders=ORDERS)

@app.route("/staff/status/<code>/<status>", methods=["POST"])
def status(code, status):
    if not staff_only():
        return redirect(url_for("staff_login"))
    allowed = ["Paid", "Preparing", "Ready for Pickup", "Completed"]
    if status not in allowed:
        return redirect(url_for("staff"))
    for order in ORDERS:
        if order["code"] == code:
            order["status"] = status
            break
    flash("Order status updated.")
    return redirect(url_for("staff"))

@app.route("/live")
def live():
    return render_template("live.html",
        preparing=[o for o in ORDERS if o["status"] == "Preparing"],
        ready=[o for o in ORDERS if o["status"] == "Ready for Pickup"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
