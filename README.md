# VERTEX ELECTRONICS — LIVE EDITABLE STORE

A real Flask + SQLite web application with an admin dashboard, product image uploads, product prices/stock, catalogue search, services, contact page and WhatsApp ordering.

## Run locally
`pip install -r requirements.txt` then `python app.py` and open http://127.0.0.1:5000
Admin: http://127.0.0.1:5000/admin
Demo login: admin / ChangeMe123!

## Before going online
Set SECRET_KEY, ADMIN_USER and ADMIN_PASS as environment variables. Replace the exact physical address, Google Maps link, real photos, final prices and business policies.

## Deployment
The included Procfile works with services such as Render/Railway-style Python hosting. The Dockerfile can be used by any container host.
