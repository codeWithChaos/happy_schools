# School Data Initialization & Currency Setup Guide

## What's Been Set Up

### 1. Classes & Sections Created
For **Happy Kids International School** (School ID: 4), the following has been initialized:

#### Academic Year
- **2025-2026** (September 1, 2025 to July 31, 2026)

#### Ghanaian Education System Classes
The following classes have been created, each with sections A, B, and C (capacity: 30 students each):

1. **Creche**
2. **Nursery**
3. **Kindergarten 1**
4. **Kindergarten 2**
5. **Class 1**
6. **Class 2**
7. **Class 3**
8. **Class 4**
9. **Class 5**
10. **Class 6**
11. **JHS 1** (Junior High School 1)
12. **JHS 2** (Junior High School 2)
13. **JHS 3** (Junior High School 3)

**Total:** 13 Classes × 3 Sections = 39 Sections

### 2. Currency Configuration
The system has been configured to use the **Ghanaian Cedi (GH₵)**.

## How to Use

### Adding Students
Now when you go to add a student:
1. Navigate to **Students** → **Add Student**
2. You'll see all the classes listed in the "Class" dropdown
3. Select a class, and the corresponding sections (A, B, or C) will be available
4. Complete the student registration form

### For Other Schools
If you need to initialize data for other schools, run:
```bash
python manage.py init_school_data <school_id>
```

For example, to initialize school ID 1:
```bash
python manage.py init_school_data 1
```

You can also specify a custom academic year:
```bash
python manage.py init_school_data 1 --year 2024-2025
```

### Currency in Templates
The currency symbol (GH₵) is now available throughout the application:

#### In Templates - Three Ways:

1. **Using the currency filter:**
```django
{% load currency_tags %}
{{ fee_amount|currency }}
<!-- Output: GH₵ 500.00 -->
```

2. **Just the symbol:**
```django
{% load currency_tags %}
{% currency_symbol %} {{ amount }}
<!-- Output: GH₵ 500.00 -->
```

3. **Using context variable:**
```django
{{ CURRENCY_SYMBOL }} {{ amount }}
<!-- Output: GH₵ 500.00 -->
```

#### In Python Code:
```python
from django.conf import settings

currency_symbol = settings.CURRENCY_SYMBOL  # GH₵
currency_code = settings.CURRENCY_CODE      # GHS
```

### Changing Currency (Optional)
If you need to change the currency later, edit `.env` file:
```env
CURRENCY_SYMBOL=GH₵
CURRENCY_CODE=GHS
```

Or for other currencies:
```env
# US Dollar
CURRENCY_SYMBOL=$
CURRENCY_CODE=USD

# Euro
CURRENCY_SYMBOL=€
CURRENCY_CODE=EUR

# British Pound
CURRENCY_SYMBOL=£
CURRENCY_CODE=GBP
```

## Admin Panel Access
You can also manage classes and sections through the Django admin panel:
1. Go to http://127.0.0.1:8000/admin/
2. Navigate to **Accounts** section
3. Click on **Classes** or **Sections** to view/edit

## Notes
- Each section has a default capacity of 30 students
- You can modify section capacities in the admin panel
- Class teachers can be assigned through the admin panel or in the application
- Room numbers can be assigned to each section
