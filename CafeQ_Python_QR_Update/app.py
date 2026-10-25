from flask import Flask, abort, render_template, request, redirect, url_for, session, flash, send_file
import random
import string
import os
import re
import sqlite3
from io import BytesIO
from urllib.parse import urlsplit
import qrcode
from demo_shops import DEMO_SHOPS

app = Flask(__name__)
app.secret_key = "change-this-demo-key"
app.config["CAFEQ_DATABASE"] = os.path.join(app.instance_path, "cafes.sqlite3")

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

def connect_db():
    os.makedirs(os.path.dirname(app.config["CAFEQ_DATABASE"]) or ".", exist_ok=True)
    connection = sqlite3.connect(app.config["CAFEQ_DATABASE"])
    connection.row_factory = sqlite3.Row
    connection.execute(
        """CREATE TABLE IF NOT EXISTS cafes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            website_url TEXT NOT NULL DEFAULT '',
            is_demo INTEGER NOT NULL DEFAULT 0
        )"""
    )
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(cafes)")}
    if "is_demo" not in columns:
        connection.execute("ALTER TABLE cafes ADD COLUMN is_demo INTEGER NOT NULL DEFAULT 0")
    for shop in DEMO_SHOPS.values():
        connection.execute(
            """INSERT OR IGNORE INTO cafes (slug, name, website_url, is_demo)
               VALUES (?, ?, '', 1)""",
            (shop["slug"], f"Demo Cafe - {shop['name']}"),
        )
        connection.execute(
            "UPDATE cafes SET is_demo = 1, website_url = '' WHERE slug = ?",
            (shop["slug"],),
        )
    connection.commit()
    return connection

def get_cafes():
    connection = connect_db()
    try:
        return [dict(row) for row in connection.execute(
            "SELECT id, slug, name, website_url, is_demo FROM cafes ORDER BY name COLLATE NOCASE"
        )]
    finally:
        connection.close()

def get_cafe(slug):
    connection = connect_db()
    try:
        row = connection.execute(
            "SELECT id, slug, name, website_url, is_demo FROM cafes WHERE slug = ?", (slug,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()

def valid_website_url(value):
    if not value or len(value) > 2048 or any(char.isspace() for char in value):
        return False
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
    except ValueError:
        return False
    return (
        parsed.scheme in {"http", "https"}
        and bool(hostname)
        and parsed.username is None
        and parsed.password is None
    )

def cafe_destination(cafe):
    if cafe["is_demo"]:
        app_base_url = os.environ.get("CAFEQ_BASE_URL", request.url_root).rstrip("/")
        return app_base_url + url_for("demo_shop", cafe_slug=cafe["slug"])
    return cafe["website_url"]

def demo_cart_key(cafe_slug):
    return f"demo_cart_{cafe_slug}"

def demo_customer_order_codes_key(cafe_slug):
    return f"demo_customer_order_codes_{cafe_slug}"

def demo_cart_items(shop):
    cart = session.get(demo_cart_key(shop["slug"]), {})
    items = []
    for item in shop["menu"]:
        quantity = int(cart.get(str(item["id"]), 0))
        if quantity:
            items.append({
                **item,
                "qty": quantity,
                "line_total": quantity * item["price"],
            })
    return items

def demo_cart_total(items):
    return sum(item["line_total"] for item in items)

def demo_customer_orders(cafe_slug):
    order_codes = set(session.get(demo_customer_order_codes_key(cafe_slug), []))
    if not order_codes:
        order_codes = set(session.get("customer_order_codes", []))
    return [
        order for order in ORDERS
        if order.get("cafe_slug") == cafe_slug and order["code"] in order_codes
    ]

def demo_shop_staff_logged_in(cafe_slug):
    return session.get("demo_staff_slug") == cafe_slug

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/menu")
def menu():
    return render_template("menu.html", menu=menu_dicts())

@app.route("/qr")
def qr_page():
    cafes = get_cafes()
    for cafe in cafes:
        cafe["destination_url"] = cafe_destination(cafe)
    return render_template("qr.html", cafes=cafes)

@app.route("/demo-cafes")
def demo_cafes():
    cafes = [cafe for cafe in get_cafes() if cafe["is_demo"]]
    for cafe in cafes:
        cafe["destination_url"] = cafe_destination(cafe)
    return render_template("demo_cafes.html", cafes=cafes)

@app.route("/scan")
def scan_qr():
    return render_template("scan.html")

@app.route("/shop/<cafe_slug>")
def demo_shop(cafe_slug):
    shop = DEMO_SHOPS.get(cafe_slug)
    if shop is None:
        abort(404)
    return render_template(
        "demo_shop.html",
        shop=shop,
        cart_count=sum(session.get(demo_cart_key(cafe_slug), {}).values()),
    )

@app.route("/shop/<cafe_slug>/add/<int:item_id>", methods=["POST"])
def demo_shop_add(cafe_slug, item_id):
    shop = DEMO_SHOPS.get(cafe_slug)
    if shop is None:
        abort(404)
    if not any(item["id"] == item_id for item in shop["menu"]):
        abort(404)
    cart = session.get(demo_cart_key(cafe_slug), {})
    key = str(item_id)
    cart[key] = int(cart.get(key, 0)) + 1
    session[demo_cart_key(cafe_slug)] = cart
    flash("Added to your cafe order.")
    return redirect(url_for("demo_shop", cafe_slug=cafe_slug) + "#menu")

@app.route("/shop/<cafe_slug>/cart")
def demo_shop_cart(cafe_slug):
    shop = DEMO_SHOPS.get(cafe_slug)
    if shop is None:
        abort(404)
    items = demo_cart_items(shop)
    return render_template("demo_shop_cart.html", shop=shop, items=items, total=demo_cart_total(items))

@app.route("/shop/<cafe_slug>/quantity/<int:item_id>/<action>", methods=["POST"])
def demo_shop_quantity(cafe_slug, item_id, action):
    shop = DEMO_SHOPS.get(cafe_slug)
    if shop is None:
        abort(404)
    if action not in {"plus", "minus"} or not any(item["id"] == item_id for item in shop["menu"]):
        abort(404)
    cart = session.get(demo_cart_key(cafe_slug), {})
    key = str(item_id)
    if key in cart:
        cart[key] = int(cart[key]) + (1 if action == "plus" else -1)
        if cart[key] <= 0:
            cart.pop(key)
    session[demo_cart_key(cafe_slug)] = cart
    return redirect(url_for("demo_shop_cart", cafe_slug=cafe_slug))

@app.route("/shop/<cafe_slug>/checkout", methods=["GET", "POST"])
def demo_shop_checkout(cafe_slug):
    shop = DEMO_SHOPS.get(cafe_slug)
    if shop is None:
        abort(404)
    items = demo_cart_items(shop)
    if not items:
        flash("Add an item before checking out.")
        return redirect(url_for("demo_shop", cafe_slug=cafe_slug))
    if request.method == "POST":
        order_type = request.form.get("type", "")
        if order_type not in {"Dine-in", "Takeout"}:
            flash("Choose Dine-in or Takeout.")
            return redirect(url_for("demo_shop_checkout", cafe_slug=cafe_slug))
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        order = {
            "number": random.randint(100, 999),
            "code": code,
            "customer": request.form.get("customer", "").strip() or "CafeQ Guest",
            "type": order_type,
            "cafe_name": shop["name"],
            "cafe_slug": cafe_slug,
            "items": items,
            "total": demo_cart_total(items),
            "status": "Pending Payment",
        }
        ORDERS.insert(0, order)
        customer_codes = session.get(demo_customer_order_codes_key(cafe_slug), [])
        customer_codes.insert(0, code)
        session[demo_customer_order_codes_key(cafe_slug)] = customer_codes
        session[demo_cart_key(cafe_slug)] = {}
        return render_template("demo_shop_confirmation.html", shop=shop, order=order)
    return render_template(
        "demo_shop_checkout.html",
        shop=shop,
        items=items,
        total=demo_cart_total(items),
    )

@app.route("/shop/<cafe_slug>/my-orders")
def demo_shop_my_orders(cafe_slug):
    shop = DEMO_SHOPS.get(cafe_slug)
    if shop is None:
        abort(404)
    return render_template(
        "demo_shop_orders.html",
        shop=shop,
        orders=demo_customer_orders(cafe_slug),
        cart_count=sum(session.get(demo_cart_key(cafe_slug), {}).values()),
    )

@app.route("/shop/<cafe_slug>/live")
def demo_shop_live(cafe_slug):
    shop = DEMO_SHOPS.get(cafe_slug)
    if shop is None:
        abort(404)
    orders = [order for order in ORDERS if order.get("cafe_slug") == cafe_slug]
    return render_template(
        "demo_shop_live.html",
        shop=shop,
        preparing=[order for order in orders if order["status"] == "Preparing"],
        ready=[order for order in orders if order["status"] == "Ready for Pickup"],
        cart_count=sum(session.get(demo_cart_key(cafe_slug), {}).values()),
    )

@app.route("/shop/<cafe_slug>/staff/login", methods=["GET", "POST"])
def demo_shop_staff_login(cafe_slug):
    shop = DEMO_SHOPS.get(cafe_slug)
    if shop is None:
        abort(404)
    if demo_shop_staff_logged_in(cafe_slug):
        return redirect(url_for("demo_shop_staff", cafe_slug=cafe_slug))
    if request.method == "POST":
        if request.form.get("username") == STAFF_USER and request.form.get("password") == STAFF_PASS:
            session["demo_staff_slug"] = cafe_slug
            session.pop("demo_staff_selected_code", None)
            return redirect(url_for("demo_shop_staff", cafe_slug=cafe_slug))
        flash("Wrong username or password.")
    return render_template("demo_shop_staff_login.html", shop=shop)

@app.route("/shop/<cafe_slug>/staff/logout")
def demo_shop_staff_logout(cafe_slug):
    if cafe_slug not in DEMO_SHOPS:
        abort(404)
    if demo_shop_staff_logged_in(cafe_slug):
        session.pop("demo_staff_slug", None)
        session.pop("demo_staff_selected_code", None)
    return redirect(url_for("demo_shop", cafe_slug=cafe_slug))

@app.route("/shop/<cafe_slug>/staff", methods=["GET", "POST"])
def demo_shop_staff(cafe_slug):
    shop = DEMO_SHOPS.get(cafe_slug)
    if shop is None:
        abort(404)
    if not demo_shop_staff_logged_in(cafe_slug):
        return redirect(url_for("demo_shop_staff_login", cafe_slug=cafe_slug))
    orders = [order for order in ORDERS if order.get("cafe_slug") == cafe_slug]
    if request.method == "POST":
        code = request.form.get("code", "").strip().upper()
        order = next((item for item in orders if item["code"] == code), None)
        if order:
            session["demo_staff_selected_code"] = code
            flash("Order found. Review it and validate payment below.")
            return redirect(url_for("demo_shop_staff", cafe_slug=cafe_slug) + "#selected-order")
        else:
            session.pop("demo_staff_selected_code", None)
            flash("No order from this cafe matches that code.")
            return redirect(url_for("demo_shop_staff", cafe_slug=cafe_slug) + "#order-lookup")
    selected_code = session.get("demo_staff_selected_code")
    selected_order = next((item for item in orders if item["code"] == selected_code), None)
    return render_template(
        "demo_shop_staff.html",
        shop=shop,
        orders=orders,
        selected_order=selected_order,
        preparing=[order for order in orders if order["status"] == "Preparing"],
        ready=[order for order in orders if order["status"] == "Ready for Pickup"],
    )

@app.route("/shop/<cafe_slug>/staff/status/<code>/<status>", methods=["POST"])
def demo_shop_staff_status(cafe_slug, code, status):
    if cafe_slug not in DEMO_SHOPS:
        abort(404)
    if not demo_shop_staff_logged_in(cafe_slug):
        return redirect(url_for("demo_shop_staff_login", cafe_slug=cafe_slug))
    allowed = ["Paid", "Preparing", "Ready for Pickup", "Completed"]
    if status not in allowed:
        abort(400)
    order = next(
        (item for item in ORDERS if item["code"] == code and item.get("cafe_slug") == cafe_slug),
        None,
    )
    if order is None:
        abort(404)
    order["status"] = status
    flash("Order status updated.")
    session["demo_staff_selected_code"] = code
    return redirect(url_for("demo_shop_staff", cafe_slug=cafe_slug) + "#selected-order")

@app.route("/qr/<cafe_slug>.png")
def qr_image(cafe_slug):
    cafe = get_cafe(cafe_slug)
    if cafe is None or (not cafe["is_demo"] and not cafe["website_url"]):
        abort(404)
    qr = qrcode.QRCode(box_size=8, border=3)
    qr.add_data(cafe_destination(cafe))
    qr.make(fit=True)
    picture = qr.make_image(fill_color="black", back_color="white")
    image_file = BytesIO()
    picture.save(image_file, format="PNG")
    image_file.seek(0)
    response = send_file(image_file, mimetype="image/png")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

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
            "cafe_name": "CafeQ",
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
    if staff_only():
        return redirect(url_for("staff"))
    if request.method == "POST":
        if request.form.get("username") == STAFF_USER and request.form.get("password") == STAFF_PASS:
            session["staff_logged_in"] = True
            return redirect(url_for("staff"))
        flash("Wrong username or password.")
    return render_template("login.html")

@app.route("/staff/logout")
def staff_logout():
    session.pop("staff_logged_in", None)
    session.pop("selected_code", None)
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
    return render_template(
        "staff.html",
        orders=ORDERS,
        preparing=[o for o in ORDERS if o["status"] == "Preparing"],
        ready=[o for o in ORDERS if o["status"] == "Ready for Pickup"],
    )

@app.route("/staff/cafes", methods=["GET", "POST"])
def staff_cafes():
    if not staff_only():
        return redirect(url_for("staff_login"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        website_url = request.form.get("website_url", "").strip()
        if not name or len(name) > 100:
            flash("Enter a cafe name of 1 to 100 characters.")
            return redirect(url_for("staff_cafes"))
        if not valid_website_url(website_url):
            flash("Enter a valid website URL starting with http:// or https://.")
            return redirect(url_for("staff_cafes"))
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:80].strip("-")
        if not slug:
            flash("The cafe name must include at least one letter or number.")
            return redirect(url_for("staff_cafes"))
        connection = connect_db()
        try:
            connection.execute(
                "INSERT INTO cafes (slug, name, website_url) VALUES (?, ?, ?)",
                (slug, name, website_url),
            )
            connection.commit()
        except sqlite3.IntegrityError:
            flash("That cafe URL slug is already in use. Choose a different cafe name.")
            return redirect(url_for("staff_cafes"))
        finally:
            connection.close()
        flash("Cafe added. Its QR code opens the website URL.")
        return redirect(url_for("staff_cafes"))
    return render_template("staff_cafes.html", cafes=get_cafes())

@app.route("/staff/cafes/<int:cafe_id>", methods=["POST"])
def update_cafe(cafe_id):
    if not staff_only():
        return redirect(url_for("staff_login"))
    name = request.form.get("name", "").strip()
    website_url = request.form.get("website_url", "").strip()
    if not name or len(name) > 100:
        flash("Enter a cafe name of 1 to 100 characters.")
        return redirect(url_for("staff_cafes"))
    connection = connect_db()
    try:
        existing = connection.execute(
            "SELECT is_demo FROM cafes WHERE id = ?", (cafe_id,)
        ).fetchone()
        if existing is None:
            abort(404)
        if not existing["is_demo"] and not valid_website_url(website_url):
            flash("Enter a valid website URL starting with http:// or https://.")
            return redirect(url_for("staff_cafes"))
        if existing["is_demo"]:
            website_url = ""
        cursor = connection.execute(
            "UPDATE cafes SET name = ?, website_url = ? WHERE id = ?",
            (name, website_url, cafe_id),
        )
        connection.commit()
    finally:
        connection.close()
    if cursor.rowcount == 0:
        abort(404)
    flash("Cafe details updated.")
    return redirect(url_for("staff_cafes"))

@app.route("/staff/live")
def staff_live():
    if not staff_only():
        return redirect(url_for("staff_login"))
    return render_template(
        "live.html",
        staff_view=True,
        preparing=[o for o in ORDERS if o["status"] == "Preparing"],
        ready=[o for o in ORDERS if o["status"] == "Ready for Pickup"],
    )

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
        staff_view=False,
        preparing=[o for o in ORDERS if o["status"] == "Preparing"],
        ready=[o for o in ORDERS if o["status"] == "Ready for Pickup"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
