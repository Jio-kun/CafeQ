CAFEQ PYTHON PROTOTYPE 
================================================

RUN THE WEBSITE
1. Open this folder in VS Code.
2. Open Terminal > New Terminal.
3. Create a virtual environment:
   python -m venv .venv
4. If PowerShell blocks activation, run:
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
5. Activate the environment:
   .\.venv\Scripts\Activate.ps1
6. Install the packages:
   python -m pip install -r requirements.txt

If error Encountered : 
cd CafeQ_Python_QR_Update

then : 
python -m pip install -r requirements.txt

7. Start the website:
   python app.py
8. On the computer, open http://127.0.0.1:5000

DEMO CAFE WEBSITES AND QR CODES
1. Visit http://127.0.0.1:5000/demo-cafes to see, scan, or download the dummy cafe QR codes. Download a fresh code after this update; previously downloaded or printed QR images cannot be changed.
2. Each QR contains a CafeQ website URL for a different demo cafe:
   /shop/demo-sunrise-cafe
   /shop/demo-moonlight-coffee
3. The two demo websites have separate designs and menus. Customers can add items, choose Dine-in or Takeout, and receive an order validation code.
4. Each demo cafe website has a Staff login link. Cashiers sign in with Username: staff, Password: cafeq123, then enter the validation code, check the cafe-specific order, collect payment, and confirm it. Each cafe's staff dashboard only lists that cafe's orders.
5. Demo cafe menu data and branding are in CafeQ_Python_QR_Update/demo_shops.py. The standalone shop templates and styling are in templates/demo_shop*.html and static/demo_shops.css.
6. To make demo QR codes work on a phone over the same Wi-Fi, open the app using the computer's Wi-Fi IP (not 127.0.0.1), or set CAFEQ_BASE_URL to that reachable address before starting the app. For example:
   $env:CAFEQ_BASE_URL="http://192.168.1.10:5000"
7. For use outside the local network, deploy this app to a public HTTPS address and set CAFEQ_BASE_URL to that address.

REAL CAFE QR CODES
1. Sign in at http://127.0.0.1:5000/staff/login and open Manage Cafes.
2. Add each real cafe with its public website URL. The QR code opens that cafe website directly.
3. Cafe names and website URLs are saved in CafeQ_Python_QR_Update/instance/cafes.sqlite3.

CAMERA QR SCANNER
1. Open http://127.0.0.1:5000/scan and allow camera access.
2. Point the camera at a cafe QR code. The scanner opens its CafeQ shop or real cafe website. Old demo Sunrise Cafe and Moonlight Coffee Google Maps QR codes are also redirected to their local demo shops by this scanner.
3. Camera access requires HTTPS or localhost. When the browser has no built-in QR detector, CafeQ uses the locally bundled jsQR decoder in static/vendor. Camera frames are processed in the browser and are not sent to a third-party scanning service. The library's Apache 2.0 license is included beside the decoder.

STAFF LOGIN
Open http://127.0.0.1:5000/staff/login
Username: staff
Password: cafeq123
Staff pages have their own navigation and dashboard. The dashboard includes customer orders and order validation; use Live Display to view preparing and ready orders.

CUSTOMER FLOW
Scan a demo cafe QR > Cafe-specific menu > Add to order > Choose Dine-in or Takeout > Show validation code to the cafe's cashier > Check that cafe's My Orders or Live Display.

EACH DEMO CAFE WEBSITE
Sunrise Cafe and Moonlight Coffee have their own menu, cart, checkout, My Orders, and Live Display pages. My Orders lists only the signed-in browser's orders for that cafe. The Live Display shows only that cafe's orders. Links stay within the current demo shop, except the explicit Other demo cafes link.

STAFF FLOW
Staff Login > find order by code > update order status.

IMPORTANT LIMITATION
This is a student demo. Orders are kept in the running Flask app's memory, so the staff section can see orders made by customers using the same running app. Orders reset when you stop/restart the app. For permanent storage, the next step is a shared database such as SQLite. The staff login is for demonstration only.

Staff validation fix: the staff page now loads the live ORDERS list, so submitted validation codes can be found and displayed. Orders remain in memory and reset when the Flask app restarts.
