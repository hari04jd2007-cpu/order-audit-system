# Order-to-Audit System for a Small Food Manufacturer

## Project Overview
A Django-based web application designed to manage sales orders, production, raw material inventory, GST invoicing, production expenses, and business reports for a small food manufacturing unit.

## Technology Stack
- Python
- Django
- SQLite
- HTML / Django Admin
- ReportLab (PDF invoice generation)
- CSV reporting

## Features Implemented
- Product, customer, and raw material management
- Raw material purchase and stock updates
- Bill of Materials (BOM) management
- Production run entry and finished goods stock updates
- Yield variance and oil usage variance calculations
- Production expense tracking (labour and gas/power)
- Production cost per packet calculation
- Sales order creation, approval, and dispatch
- GST invoice generation with PDF download
- Payment and outstanding balance tracking
- Sales register CSV export
- Stock summary CSV export

## Benchmark Test Results

| Metric | Expected / Actual |
|---|---:|
| Flour closing stock | 120 kg |
| Oil closing stock | 19.5 L |
| Spice closing stock | 3.8 kg |
| Pouches closing stock | 294 |
| Cartons closing stock | 21 |
| Finished stock after production | 238 packets |
| Finished stock after dispatch | 88 packets |
| Yield variance | -6% |
| Oil usage variance | +5% |
| Invoice taxable amount | ₹7,500 |
| GST (CGST + SGST) | ₹375 |
| Invoice total | ₹7,875 |
| Production cost | ₹5,885 |
| Cost per good packet | ₹31.30 |

## How to Run Locally

1. Clone the repository:
   ```bash
   git clone YOUR_GITHUB_REPOSITORY_URL
   ```

2. Navigate to the project directory:
   ```bash
   cd order_audit_system
   ```

3. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install django reportlab
   ```

5. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

6. Create an admin account:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

8. Open:
   `http://127.0.0.1:8000/admin/`

## Assumptions
- The benchmark production run uses actual material consumption.
- Damaged pouches are included in pouch consumption.
- Production cost per packet is calculated using total material and production expenses divided by good packets.
- GST is calculated at 5% for the Tamil Nadu customer using CGST and SGST.
- The cost calculation uses the material unit rates stored in the system.

## Current Limitations
- The application currently uses Django Admin as its primary interface.
- Dedicated salesman and role-specific workflows can be enhanced.
- A detailed stock movement ledger and Excel export can be added in future versions.
- The current implementation is intended as a functional MVP and can be extended with a dedicated frontend.

## Future Enhancements
- Dedicated responsive dashboard for sales and production users.
- Role-based access and approval workflows.
- Detailed inventory ledger.
- Excel report export.
- Production cost and profitability analytics.

## Author
Hari Prasath M

Artificial Intelligence and Data Science Student
