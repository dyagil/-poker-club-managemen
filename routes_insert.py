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
