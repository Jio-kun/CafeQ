CAFEQ PYTHON PROTOTYPE
======================

For the complete GitHub project guide, including installation, customer and staff
workflows, QR setup, SQLite storage, and prototype security notes, see the
repository's README.md in the project root.

Quick start from PowerShell:

1. Open a terminal in the repository root and change to this folder:
   cd CafeQ_Python_QR_Update
2. Create and activate a virtual environment:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
3. Install dependencies and start the server:
   python -m pip install -r requirements.txt
   python app.py
4. Open http://127.0.0.1:5000

Demo cafe QR gallery: /demo-cafes
Staff sign-in: /staff/login
Demo staff username: staff
Demo staff password: cafeq123
