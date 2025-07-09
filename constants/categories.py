# constants/categories.py

EXPENSE_CATEGORIES = {
    "Housing": [
        "Rent/Mortgage",
        "Property Taxes",
        "Home Insurance",
        "Maintenance & Repairs",
        "HOA Fees",
        "Utilities (Electric, Water, Gas)",
    ],
    "Food & Groceries": ["Groceries", "Dining Out", "Coffee Shops", "Meal Delivery"],
    "Transportation": [
        "Fuel",
        "Public Transit",
        "Car Payment",
        "Car Insurance",
        "Maintenance/Repairs",
        "Parking & Tolls",
        "Rideshare",
    ],
    "Utilities & Subscriptions": [
        "Internet",
        "Mobile Phone",
        "Streaming Services",
        "Cloud Storage",
        "Software Subscriptions",
    ],
    "Health & Insurance": [
        "Health Insurance",
        "Dental & Vision",
        "Medical Bills",
        "Prescriptions",
        "Therapy/Counseling",
        "Fitness",
    ],
    "Education & Personal Development": [
        "Tuition",
        "Student Loans",
        "Books & Supplies",
        "Online Courses",
        "Certifications",
    ],
    "Shopping & Personal": [
        "Clothing & Accessories",
        "Beauty & Grooming",
        "Gifts & Special Occasions",
        "Retail Spending",
    ],
    "Family & Children": [
        "Childcare",
        "School Supplies",
        "Allowance",
        "Baby Essentials",
        "Kids' Activities",
    ],
    "Entertainment & Leisure": [
        "Movies, Concerts, Events",
        "Hobbies",
        "Gaming",
        "Other Subscriptions",
    ],
    "Travel & Vacations": [
        "Flights",
        "Hotels",
        "Transportation",
        "Travel Insurance",
        "Souvenirs",
    ],
    "Debt & Loans": [
        "Credit Card Payments",
        "Personal Loans",
        "Payday Loans",
        "Installment Plans",
    ],
    "Savings & Investments": [
        "Emergency Fund",
        "Retirement",
        "Stock Investments",
        "Crypto",
        "Real Estate Investment",
    ],
    "Business & Side Hustles": [
        "Office Supplies",
        "Business Tools & Software",
        "Advertising",
        "Contractors/Freelancers",
        "Taxes",
    ],
    "Donations & Giving": ["Charities", "Church/Tithing", "Fundraisers"],
    "Miscellaneous/Uncategorized": [
        "ATM Withdrawals",
        "Cash Expenses",
        "One-Time Payments",
        "Other",
    ],
}


# Helper functions
def get_all_categories():
    """Get list of main categories."""
    return list(EXPENSE_CATEGORIES.keys())


def get_subcategories(main_category):
    """Get subcategories for a main category."""
    return EXPENSE_CATEGORIES.get(main_category, [])


def get_all_subcategories_flat():
    """Get all subcategories as a flat list."""
    subcategories = []
    for subs in EXPENSE_CATEGORIES.values():
        subcategories.extend(subs)
    return subcategories


def validate_category(main_category, subcategory):
    """Validate if a category/subcategory combination is valid."""
    if main_category not in EXPENSE_CATEGORIES:
        return False
    return subcategory in EXPENSE_CATEGORIES[main_category]
