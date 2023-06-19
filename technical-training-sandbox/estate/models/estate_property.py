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
    # buller_id = fields.Many2one("res.Buller", string="Buller")
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    # partner_id = fields.Many2one("res.partner", string="Partner")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    seller_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    # An offer applies to one property, but the same property can have many offers.
    offer_ids = fields.One2many("estate.property.offer","id", string="Offers")

    # def calculate_start_of_3_months(self):
    #     today = fields.Datetime.today()
    #     future_date = today + relativedelta(months=3)
    #     self.date_availability(default = self.env['ir.fields'].start_of('month', future_date))

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Estate Property Type"

    name = fields.Char('Title',required=True)

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Estate Property Tag"

    name = fields.Char('Title',required=True)

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float()
    status = fields.Selection(
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        copy = False,
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)