# CafeQ

CafeQ is a Flask prototype for ordering from a cafe after scanning its QR code. Customers browse a cafe-specific menu, place dine-in or takeout orders, and receive a validation code to show at the cashier. Staff can look up orders, record payment, update preparation status, and remove orders.

## Features

- Separate customer and staff pages.
- Main CafeQ menu, cart, checkout, order history, and live pickup display.
- Sunrise Cafe and Moonlight Coffee demo websites, each with its own branding, menu, cart, order history, live display, and staff dashboard.
- QR gallery and camera scanner. QR images for demo cafes link to their local CafeQ shop; real cafe QR images link to the website URL entered by staff.
- Staff order lookup using a six-character validation code.
- SQLite persistence for cafes and orders. Orders and staff status changes remain available after the server restarts.
- Staff-only order deletion. Deleting an order removes it from the database and from customer history and live displays.
- Locally bundled QR decoding fallback. Camera frames are processed in the browser.

## Requirements

- Python 3
- Packages listed in `CafeQ_Python_QR_Update/requirements.txt`

## Run on Windows

Open PowerShell in the repository folder and run:

```powershell
cd CafeQ_Python_QR_Update
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks virtual-environment activation, allow it for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. To stop the server, press `Ctrl+C` in the terminal.

### Run on macOS or Linux

From the repository folder:

```bash
cd CafeQ_Python_QR_Update
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

## Main pages

| Page | URL |
| --- | --- |
| Customer home and menu | `/` and `/menu` |
| QR scanner | `/scan` |
| Demo cafe QR gallery | `/demo-cafes` |
| Sunrise Cafe demo shop | `/shop/demo-sunrise-cafe` |
| Moonlight Coffee demo shop | `/shop/demo-moonlight-coffee` |
| Customer order history | `/my-order` |
| Staff sign-in | `/staff/login` |
| Staff dashboard | `/staff` |
| Staff live display | `/staff/live` |

Each demo shop has its own cart, checkout, My Orders, Live Display, and cashier pages. The shop's Staff Login link opens its cashier sign-in and dashboard.

## Demo staff sign-in

The prototype uses the following demo credentials:

```text
Username: staff
Password: cafeq123
```

The same credentials are used for CafeQ and both demo cafe cashier dashboards. Demo cafe staff can only see, update, and delete orders belonging to their cafe. The main staff dashboard can manage orders across the app.

## Customer and cashier workflow

1. Open `/demo-cafes` and choose Sunrise Cafe or Moonlight Coffee, or scan that cafe's QR code.
2. Add menu items to the cart and select **Dine-in** or **Takeout** at checkout.
3. Show the generated six-character validation code to the cashier.
4. The cashier signs in to the correct cafe's staff page, looks up the code, checks the order, and records payment.
5. Staff can move the order through **Paid**, **Preparing**, **Ready for Pickup**, and **Completed**. The cafe's public Live Display shows preparing and ready orders.
6. Staff can delete an order from the dashboard. Deletion is permanent and removes the order from customer history and live displays.

## QR codes and phone access

Demo QR codes use the CafeQ server address and open these local shop paths:

```text
/shop/demo-sunrise-cafe
/shop/demo-moonlight-coffee
```

To scan a demo QR using a phone on the same Wi-Fi network:

1. Find the computer's local Wi-Fi IP address.
2. Set `CAFEQ_BASE_URL` to that computer's reachable address before starting Flask. For example, in PowerShell:

   ```powershell
   $env:CAFEQ_BASE_URL = "http://192.168.1.10:5000"
   python app.py
   ```

3. Open the app from the phone using the same address, such as `http://192.168.1.10:5000/demo-cafes`, and scan a newly downloaded QR code.

Replace the example IP with the computer's actual address. `127.0.0.1` is only reachable from the same device. Allow the app through the computer's firewall if necessary.

The camera scanner requires `localhost` or HTTPS in the browser. If the browser does not support its built-in QR detector, CafeQ uses the bundled `static/vendor/jsQR.js` decoder locally; camera frames are not sent to an external scanning service. The decoder's license is included beside the bundled library.

## Manage real cafe QR codes

1. Sign in at `/staff/login`.
2. Open **Manage Cafes** and add a cafe name and its public `http://` or `https://` website URL.
3. Download its QR code from the cafe QR page. Scanning the code opens the URL entered for that cafe.

Demo cafe QR codes open the locally hosted CafeQ demo shop instead of an external site.

## Data storage

SQLite data is stored in:

```text
CafeQ_Python_QR_Update/instance/cafes.sqlite3
```

The app creates the database and tables when it runs. The database stores cafe records and order details, including each order's items, total, validation code, and status. Back up this file to preserve data. Deleting an order in the staff dashboard permanently removes that order from the database.

Customer order history is associated with the browser session that placed the order. Staff and live displays read orders from the shared SQLite database.

## Project layout

```text
CafeQ_Python_QR_Update/
  app.py                 Flask routes, order handling, and SQLite storage
  demo_shops.py          Demo cafe names, themes, and menus
  requirements.txt       Python package dependencies
  templates/             Customer, staff, scanner, and demo shop pages
  static/                Stylesheets and QR scanner assets
  instance/              Local SQLite database (created at runtime)
```

## Prototype security notes

This is a student/demo application, not a production ordering system. Staff authentication uses shared hard-coded demo credentials, and the Flask secret key in `app.py` is a development placeholder. Do not expose the app publicly or use it for real customer data without replacing the authentication, secret-key management, and other production security controls. Use HTTPS for camera access and public deployment.
