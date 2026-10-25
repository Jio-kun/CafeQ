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
1. Visit http://127.0.0.1:5000/demo-cafes to see, scan, or download the dummy cafe QR codes. The page uses its own template at templates/demo_cafes.html.
2. Each QR contains a CafeQ website URL for a different demo cafe:
   /shop/demo-sunrise-cafe
   /shop/demo-moonlight-coffee
3. The two demo websites have separate designs and menus. Customers can add items, choose Dine-in or Takeout, and receive an order validation code.
4. The cashier signs in at /staff/login, enters the code, checks the order, collects payment, and confirms it.
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
2. Point the camera at a cafe QR code. The scanner opens its CafeQ shop or real cafe website.
3. Camera access requires HTTPS or localhost. This scanner uses the browser's built-in QR detector without a third-party scanning service. If the browser does not provide that detector, scan using the phone's built-in camera app.

STAFF LOGIN
Open http://127.0.0.1:5000/staff/login
Username: staff
Password: cafeq123
Staff pages have their own navigation and dashboard. The dashboard includes customer orders and order validation; use Live Display to view preparing and ready orders.

CUSTOMER FLOW
Scan a demo cafe QR > Cafe-specific menu > Add to order > Choose Dine-in or Takeout > Show validation code to cashier > Cashier validates and takes payment.

STAFF FLOW
Staff Login > find order by code > update order status.

IMPORTANT LIMITATION
This is a student demo. Orders are kept in the running Flask app's memory, so the staff section can see orders made by customers using the same running app. Orders reset when you stop/restart the app. For permanent storage, the next step is a shared database such as SQLite. The staff login is for demonstration only.

Staff validation fix: the staff page now loads the live ORDERS list, so submitted validation codes can be found and displayed. Orders remain in memory and reset when the Flask app restarts.
