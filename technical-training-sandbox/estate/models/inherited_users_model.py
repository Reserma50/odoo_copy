from odoo import models, fields, api, exceptions
import logging

class UsersModelFields(models.Model):
    _inherit = 'res.users'
    
    property_ids = fields.One2many(comodel_name='estate.property', 
                                    inverse_name="seller_id", 
                                   string='Propiedades', 
                                   domain=lambda self: [('state', 'in', ['offer_received', 'offer_accepted', 'sold'])])

    test = fields.Char("Test Field")
    last_licence_front = fields.Binary(string='Frontal',
        help='Front side image of the licence at the moment of this log')
    last_licence_back = fields.Binary(string='Posterior',
        help='Back side  image of the licence at the moment of this log')
    licence_renovation_date = fields.Date(
        'Fecha de vencimiento de la Matrícula',
        required = True,
        help = 'Fecha en el momento que vence la matrícula!')
    estado_licencia = fields.Selection(
        [
         ('Ok', 'Vigente'),
         ('Warning', 'Requiere atención'),
         ('Expired', 'Expirada')
        ], 'Estado de Licencia', default='Ok',
        help='Escoge si la licencia esta vigente o no',
        # tracking=True,
        compute = '_compute_estate',
        copy=False)
    
    @api.depends('estado_licencia')
    def _compute_estate(self):
        """
        return a dict with as value for each licenced 
        if date_renovation is in an more than 1 month, return Ok
        if date_renovation is in an less than 1 month and more than 1 days, return Warning
        otherwise return Expired
        """
        today = fields.Date.from_string(fields.Date.today())
        for record in self:
            print(record.estado_licencia)
            renew_date = fields.Date.from_string(record.licence_renovation_date)
            diff_time = (renew_date - today).days
            if diff_time > 30:
                record.estado_licencia = "Ok"
            elif diff_time > 0 and diff_time < 30:
                record.estado_licencia = "Warning"
            else:
                record.estado_licencia = "Expired"

