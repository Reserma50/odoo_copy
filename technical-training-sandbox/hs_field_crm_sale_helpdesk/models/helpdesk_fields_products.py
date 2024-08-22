from odoo import models, fields, api, exceptions
import logging
_logger = logging.getLogger(__name__)


class sale_fields(models.Model):
    _inherit = 'helpdesk.ticket'

    numero_serie_product = fields.Char(string='Código del cliente', compute='_compute_related_product_hd')
    modelo_product = fields.Char(string='Código del cliente', compute='_compute_related_product_hd')
    marca_product = fields.Char(string='Código del cliente', compute='_compute_related_product_hd')
    ubicacion_product = fields.Char(string='Código del cliente', compute='_compute_related_product_hd')


    @api.depends('product_id')
    def _compute_related_product_hd(self):
        for record in self:
            record.numero_serie_product = "record.product_id.name"
            #record.modelo_product = record.product_id.name
            #record.marca_product = record.product_id.name
           # record.ubicacion_product = record.product_id.name
