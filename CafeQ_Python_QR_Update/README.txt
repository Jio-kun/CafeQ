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

CUSTOMER QR CODE
1. Open http://127.0.0.1:5000/qr to show the QR code.
2. The QR code directs customers straight to the /menu page.
3. IMPORTANT: 127.0.0.1 only works on the same computer. A phone cannot open your computer using that address.
4. For a phone demo on the same Wi-Fi:
   a. Run ipconfig in PowerShell and find your Wi-Fi IPv4 Address (example: 192.168.1.10).
   b. Replace the example IP below with your own IP, then run this in the same terminal BEFORE python app.py:
      $env:CAFEQ_BASE_URL="http://192.168.1.10:5000"
   c. Start the app using python app.py.
   d. On the computer, open http://192.168.1.10:5000/qr using your actual IP and scan the code with your phone.
   e. Keep both devices on the same Wi-Fi. If Windows Firewall asks, allow Python on your private network.
5. For scanning outside your Wi-Fi, the website needs to be hosted online and CAFEQ_BASE_URL set to that public website address.

STAFF LOGIN
Open http://127.0.0.1:5000/staff/login
Username: staff
Password: cafeq123

CUSTOMER FLOW
Scan QR > Digital Menu > Add to Cart > Checkout > Validation Code

STAFF FLOW
Staff Login > find order by code > update order status.

IMPORTANT LIMITATION
This is a student demo. Orders are kept in the running Flask app's memory, so the staff section can see orders made by customers using the same running app. Orders reset when you stop/restart the app. For permanent storage, the next step is a shared database such as SQLite. The staff login is for demonstration only.

Staff validation fix: the staff page now loads the live ORDERS list, so submitted validation codes can be found and displayed. Orders remain in memory and reset when the Flask app restarts.
