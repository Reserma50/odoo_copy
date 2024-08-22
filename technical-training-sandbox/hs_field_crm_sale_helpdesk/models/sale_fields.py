from odoo import models, fields, api, exceptions
import logging
_logger = logging.getLogger(__name__)


class sale_fields(models.Model):
    _inherit = 'sale.order'
  
    #codigo_socio_negocio_cliente = fields.Char(string='Código del socio de negocios', compute='_compute_related_customers')
    #nombre_socio_negocio_cliente = fields.Char(string='Nombre socio de negocios')
   
    persona_contacto_cliente=fields.Char(string='Atención')
    correo_electronico_contacto=fields.Char(string='Correo Electrónico')
    numero_telefono_cliente_cliente=fields.Char(string='Teléfono')
    #campos nuevos 03 de julio···>
    forma_pago=fields.Char(string='Formas de pago')
    termino_entrega=fields.Char(string='Terminos de entrega')
    garantia_sale=fields.Char(string='Garantia')

    #anexos
    anexo_field = fields.Binary(string='Anexo')

    #@api.depends('partner_id')
    #def _compute_related_customers(self):
     #   for record in self:
      #      record.codigo_socio_negocio_cliente = record.partner_id.codigo_socio_negocio
       #     record.nombre_socio_negocio_cliente = record.partner_id.nombre_socio_negocio
        #    record.numero_telefono_cliente_cliente = record.partner_id.numero_telefono_cliente
        #    record.persona_contacto_cliente = record.partner_id.persona_contacto.name
    
