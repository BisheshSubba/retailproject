# Shoe Retail Management System
A comprehensive information system for managing a shoe retail shop, built with Django and MySQL.

## Features
### 🏬 Inventory Management
- Product catalog with detailed attributes
- Stock level monitoring
- Automatic low stock alerts
- Overstock identification
### 💰 Sales Processing
- Point of Sale (POS) interface
- Receipt generation
- Sales history tracking
### 📊 Reporting System
- **Inventory Reports**: Stock levels, valuation
- **Sales Reports**: Daily/weekly/monthly sales
- **Financial Reports**: Profit/loss statements
- **Supplier Reports**: Purchase history, performance
### 🚚 Supplier Management
- Supplier database
- Restocking workflow
- Return-to-supplier processing

## Technology Stack

- **Backend**: Django 4.x
- **Database**: MySQL 8.x
- **Frontend**: HTML5, CSS3, JavaScript

## Installation
### Prerequisites
- Python 3.9+
- MySQL Server
- pip

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/BisheshSubba/retailproject.git
   cd retailproject
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
4. Configure MySQL:
   ```bash
   DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
    }
   ```
5. Run migrations and run server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
  

