from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    DecimalField,
    TextAreaField,
    SelectField,
    DateField,
    SubmitField,
)
from wtforms.validators import DataRequired, Optional, NumberRange, Length
from datetime import date
from constants.categories import EXPENSE_CATEGORIES, get_all_categories


class ExpenseForm(FlaskForm):
    """Form for creating/editing expenses."""

    name = StringField("Expense Name", validators=[DataRequired(), Length(max=64)])

    amount = DecimalField(
        "Amount",
        validators=[
            DataRequired(),
            NumberRange(min=0.01, message="Amount must be greater than 0"),
        ],
        places=2,
    )

    main_category = SelectField("Category", validators=[DataRequired()])

    subcategory = SelectField("Subcategory", validators=[DataRequired()])

    date = DateField("Date", validators=[DataRequired()], default=date.today)

    payment_method = SelectField(
        "Payment Method",
        choices=[
            ("", "Select Payment Method"),
            ("Cash", "Cash"),
            ("Credit Card", "Credit Card"),
            ("Debit Card", "Debit Card"),
            ("Bank Transfer", "Bank Transfer"),
            ("Check", "Check"),
            ("PayPal", "PayPal"),
            ("Venmo", "Venmo"),
            ("Other", "Other"),
        ],
        validators=[Optional()],
    )

    description = TextAreaField("Description", validators=[Optional(), Length(max=255)])

    submit = SubmitField("Save Expense")

    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        # Populate main categories
        self.main_category.choices = [("", "Select Category")] + [
            (cat, cat) for cat in get_all_categories()
        ]

        # Initially populate subcategories (will be updated via JavaScript)
        if self.main_category.data:
            subcats = EXPENSE_CATEGORIES.get(self.main_category.data, [])
            self.subcategory.choices = [("", "Select Subcategory")] + [
                (sub, sub) for sub in subcats
            ]
        else:
            self.subcategory.choices = [("", "First select a category")]
