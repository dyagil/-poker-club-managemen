@app.route('/export_super_agents_report')
@login_required
@admin_required
def export_super_agents():
    """ייצוא דוח סופר-אייג'נטים לאקסל"""
    from excel_export import export_super_agents_report
    return export_super_agents_report(load_excel_data, load_payment_history)
