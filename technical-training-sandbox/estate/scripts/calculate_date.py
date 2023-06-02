from dateutil.relativedelta import relativedelta
# from odoo import models, fields
import datetime


def calculate_start_of_3_months():
    # today = fields.Datetime.today()
    today = datetime.datetime.today()
    print(today)
    future_date = today + relativedelta(months=3)
    print(future_date)
    # start_of_month = self.env['ir.fields'].start_of('month', future_date)


calculate_start_of_3_months()

# self.env['ir.fields'].start_of('month', fields.Datetime.today() + relativedelta(months=3))