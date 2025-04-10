# פילטר לפורמט תאריך לפלאסק
from flask import Flask
from datetime import datetime

def add_date_format_filter(app):
    """מוסיף פילטר date_format לאפליקציית הפלאסק"""
    @app.template_filter('date_format')
    def date_format(value):
        if not value:
            return ''
        try:
            dt = datetime.strptime(value, '%Y-%m-%d')
            return dt.strftime('%d/%m/%Y')
        except:
            return value
    
    return app
