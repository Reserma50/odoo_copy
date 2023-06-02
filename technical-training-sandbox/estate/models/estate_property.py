from odoo import models, fields
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"

    name = fields.Char('Title',required=True)
    description = fields.Text()
    postcode = fields.Char()
    # date_availability = fields.Date(copy=False, default=lambda self: fields.Datetime.today()) #the default availability date is in 3 months
    date_availability = fields.Date('Available From',copy=False, default=lambda self:fields.Datetime.today() + relativedelta(months=3))
    expected_price = fields.Float('Expected Price', required=True)
    selling_price = fields.Float('Selling Price',readonly=True, copy=False)
    bedrooms = fields.Integer(default = 2)
    living_area = fields.Integer('Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer('Garden Area (sqm)')
    garden_orientation = fields.Selection(string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
    )    
    active = fields.Boolean('Active', default=False)
    state = fields.Selection(
        default='new',
        required=True,
        selection=[('new', 'New'), ('offer received', 'Offer Received'), ('offer accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')],
    )    

    # def calculate_start_of_3_months(self):
    #     today = fields.Datetime.today()
    #     future_date = today + relativedelta(months=3)
    #     self.date_availability(default = self.env['ir.fields'].start_of('month', future_date))
