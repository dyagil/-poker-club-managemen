# -*- coding: utf-8 -*-
"""
אפליקציית מערכת תשלומים - מודול ראשי
כולל את כל הנתיבים (routes) של המערכת
"""
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, date
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import pytz
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from report_generator import generate_role_based_report
import io
from auth_decorators import login_required, admin_required, agent_or_admin_required, player_or_agent_or_admin_required
from excel_export import export_super_agent_report, export_agent_report, export_payments

# הגדרת אזור זמן ישראל
IST = pytz.timezone('Asia/Jerusalem')

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # מפתח סודי לשימוש ב-session ו-flash

# קוד אפליקציה קיים...

# ייצוא דוח סופר-אייג'נט לאקסל
@app.route('/export/super-agent-report/<super_agent_name>')
@login_required
@admin_required
def export_super_agent_excel(super_agent_name):
    return export_super_agent_report(super_agent_name, load_excel_data, load_payment_history)

# ייצוא דוח אייג'נט לאקסל
@app.route('/export/agent-report/<agent_name>')
@login_required
@admin_required
def export_agent_excel(agent_name):
    return export_agent_report(agent_name, load_excel_data, load_payment_history)

# ייצוא היסטוריית תשלומים לאקסל
@app.route('/export/payments')
@login_required
@admin_required
def export_payments_excel():
    return export_payments(load_payment_history, request.args)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
