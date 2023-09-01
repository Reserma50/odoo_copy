# -*- coding: utf-8 -*-

from odoo import models, fields, api


class sale_fields(models.Model):
    # _name = 'sale_fields.sale_fields'
    # _description = 'sale_fields.sale_fields'

    # name = fields.Char()
    # value = fields.Integer()
    # value2 = fields.Float(compute="_value_pc", store=True)
    # description = fields.Text()

    # @api.depends('value')
    # def _value_pc(self):
    #     for record in self:
    #         record.value2 = float(record.value) / 100

    _inherit = 'sale.order'

    propuesta_ejecutiva = fields.Html(string='Proposal')
    consecutivo = fields.Char(string='Consecutive', default="1245VEN23")



