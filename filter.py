from flask import Blueprint
import locale

# Set locale for number formatting
locale.setlocale(locale.LC_ALL, '')

# Create a Blueprint for our filters
filters_bp = Blueprint('filters', __name__)

@filters_bp.app_template_filter('format_number')
def format_number(value):
    """Format a number with thousands separator"""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value