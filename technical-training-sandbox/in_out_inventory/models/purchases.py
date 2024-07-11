# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions, tools
import base64
import logging

class InheritedPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    our_default_account_id = fields.Many2one(
            comodel_name='account.account', copy=False, ondelete='restrict',
            string='Default Account',
            domain="[('deprecated', '=', False), ('company_id', '=', company_id),"
                "('account_type', '=', default_account_type), ('account_type', 'not in', ('asset_receivable', 'liability_payable'))]"
            )
    
class InheritedPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_type = fields.Selection([
        ('product', 'PRODUCTO'),
        ('servicio', 'SERVICIO')
    ], string='Tipo de Pedido', index=True, copy=False, default='product', tracking=True)

#Product

class InheritedProductMask(models.Model):
    _inherit = 'stock.valuation.layer'

    detail_type_rel = fields.Selection(related="product_id.detailed_type", string="Tipo de Producto")
    barcode_rel = fields.Char(related="product_id.barcode", string="Código")
    # mrc_rel1 = fields.Many2one(related="product_id.marca_id", string="Marca Rel")
    # mrc_rel2 = fields.Char(related="product_id.marca", string="Marca")

#move line

class InheritedMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends('display_type', 'company_id')
    def _compute_account_id(self):
       
       res = super(InheritedMoveLine,self)._compute_account_id()
       logging.info("Date:::::::::::" + str(res))
       return res