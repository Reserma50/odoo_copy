from odoo import models, fields, api, exceptions
import logging

class UsersModelFields(models.Model):
    # _name = 'estate.users'
    _inherit = 'res.users'
    
    property_ids = fields.One2many(comodel_name='estate.property', 
                                    inverse_name="seller_id", 
                                   string='Propiedades', 
                                   domain=lambda self: [('state', 'in', ['offer_received', 'offer_accepted', 'sold'])])

    test = fields.Char("Test Field")
