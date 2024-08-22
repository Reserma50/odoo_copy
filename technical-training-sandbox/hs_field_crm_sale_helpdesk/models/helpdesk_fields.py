from odoo import models, fields, api, exceptions
import logging
_logger = logging.getLogger(__name__)


class sale_fields(models.Model):
    _inherit = 'helpdesk.ticket'

    codigo_cliente = fields.Char(string='Código del cliente', compute='_compute_related_customers_hd')
    numero_serie_product = fields.Char(string='Número de Serie', compute='_compute_related_product_hd')
    modelo_product = fields.Char(string='Modelo', compute='_compute_related_product_hd' )
    marca_product = fields.Char(string='Marca', compute='_compute_related_product_hd' )
    ubicacion_product = fields.Char(string='Ubicación', compute='_compute_related_product_hd' )

    @api.depends('partner_id')
    def _compute_related_customers_hd(self):
        for record in self:
            record.codigo_cliente = record.partner_id.id
            
    @api.depends('product_id')
    def _compute_related_product_hd(self):
        for record in self:
            record.numero_serie_product = record.product_id.n_serie
            record.modelo_product = record.product_id.modelo
            record.marca_product = record.product_id.marca
            record.ubicacion_product = record.product_id.direccion
            record.x_studio_lista_producto = record.product_id.id




