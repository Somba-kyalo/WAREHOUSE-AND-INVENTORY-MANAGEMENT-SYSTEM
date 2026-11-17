# Warehouse Control

A production-minded warehouse and inventory management foundation with a Django REST API and a React/Vite operations dashboard.

## Run locally

### Backend

Use Python 3.11+ and install the packages in [requirements.txt](./requirements.txt):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

The API is available under `http://127.0.0.1:8000/api/`.

### Frontend

```powershell
npm install
npm run dev
```

The dashboard reads live summary data from `GET /api/dashboard/` when the backend is running. It keeps a clearly marked operational sample view while the database is empty so the interface can be reviewed before seed data is added.

## Current API surface

- `GET/POST /api/products/`
- `GET/POST /api/warehouses/`
- `GET/POST /api/categories/`
- `GET /api/inventory/`
- `POST /api/inventory/move/` for stock-in and stock-out
- `GET /api/transactions/`
- `GET /api/dashboard/`
- `POST /api/transfers/{id}/execute/` for atomic warehouse transfers

The repeatable `seed_demo` command creates three products, two Nairobi warehouses, and stock levels that exercise optimal, low-stock, and out-of-stock states.

Inventory changes run through `transaction.atomic()` and row locks, update the stock record, and create an immutable transaction record together.

