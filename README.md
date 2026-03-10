# 🫙 Home Made Pickles & Snacks
### Flask E-Commerce Mini Project (No Database Version)

## Features
- Full e-commerce store with cart, checkout, orders
- User registration & login (in-memory)
- Admin panel to manage products, orders, users
- 9 pre-seeded products (4 Pickles + 5 Snacks)
- **No database required** — all data stored in memory

## How to Run
```bash
unzip pickle_shop_project.zip
cd pickle_shop
pip install flask
python app.py
```
Open: http://127.0.0.1:5000

## Admin Access
URL: http://127.0.0.1:5000/admin/login
- Email: admin@pickles.com
- Password: admin123

## Note on Data
Since there is no database, all data (users, orders, cart) 
resets when you restart the server. Products are pre-loaded 
from app.py on every startup.

## Tech Stack
- Backend: Python Flask
- Frontend: HTML5, Bootstrap 5, CSS3, JavaScript
- Data: In-memory Python dictionaries (no DB)
