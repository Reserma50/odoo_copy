# -*- coding: utf-8 -*-

from odoo import models, fields, api


# class compras_fields(models.Model):
#     _name = 'compras_fields.compras_fields'
#     _description = 'compras_fields.compras_fields'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

class InheritedPurchase(models.Model):
    _inherit = ['purchase.order']
    contact_person = fields.Char(string="Persona de Contacto:", default="Carlos Vera")
    contact_mail = fields.Char(string="Email de Contacto:", default="carlos.vera@readymat.com")
    contact_number = fields.Char(string="Teléfono de Contacto", default="67895678")
    comentario = fields.Html(string="Comentario", default="Garantía por Cliente")
    delivery_conditions = fields.Selection(
        [("CIF","CIF"),
         ("CIP","CIP"),
         ("Ex","ExWorks"),
         ], string="Delivery Conditions:",
         default="CIF",
    )
    shipment = fields.Selection(
        [("air","Air"),
         ("sea","Sea"),
         ("ground","Ground"),
         ("courier","courier"),
         ], string="Shipment:",
         default="courier",
    )
    descuento = fields.Integer(string='Descuento',help="Opcional: Descuento en porcentaje que calcula Odoo antes de Total", default=0.0)
    envio_id = fields.Many2one('compras_fields.purchase_shipment',string='Dirección de Envio')
    project_id = fields.Many2one('compras_fields.property_proyect',string='Proyecto')
    

class Purchase_Shipment(models.Model):
    _name = "compras_fields.purchase_shipment"
    _description = "Dirreciones de Envio"
    _order = "name"

    name = fields.Char('Title',required=True)
    description = fields.Html('Description')
    envios_ids = fields.One2many('purchase.order', 'envio_id', string='Dirección de Envio')

    _sql_constraints = [
        ('purchase_shipment_unique_name', 'UNIQUE(name)','The name of porperty type must be unique.'),
    ]

class PropertyProyect(models.Model): #no puede ser compras
    _name = "compras_fields.property_proyect"
    _description = "State Proyect"
    _order = "name"

    name = fields.Char('Title',required=True)
    description = fields.Html('Description')
    color = fields.Integer('Color')
    proyectos_ids = fields.One2many('purchase.order', 'project_id', string='Proyecto')

    _sql_constraints = [
        ('state_property_proyect_unique_name', 'UNIQUE(name)','The name of porperty proyect must be unique.'),
    ]