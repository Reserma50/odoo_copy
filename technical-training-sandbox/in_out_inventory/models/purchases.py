# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions, tools
import base64
import logging

MYACCOUNT_DOMAIN = "['&', '&', '&', ('deprecated', '=', False),  ('company_id', '=', current_company_id), ('account_type', 'not in', ('asset_receivable','liability_payable','asset_cash','liability_credit_card')), ('is_off_balance', '=', False)]"

class InheritedPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    our_default_account_id = fields.Many2one(
            comodel_name='account.account', copy=False, ondelete='restrict',
            string='Cuenta Relacionada',
            domain=MYACCOUNT_DOMAIN
            )
    
class InheritedPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_type = fields.Selection([
        ('product', 'PRODUCTO'),
        ('servicio', 'SERVICIO')
    ], string='Tipo de Pedido', index=True, copy=False, default='product', tracking=True)

    def _prepare_invoice(self):
        res = super(InheritedPurchaseOrder,self)._prepare_invoice()
        try:
            if self.purchase_type:
                res['purchase_type'] = self.purchase_type
        except ValueError:
            pass

        return res

#Product

class InheritedProductMask(models.Model):
    _inherit = 'stock.valuation.layer'

    detail_type_rel = fields.Selection(related="product_id.detailed_type", string="Tipo de Producto")
    barcode_rel = fields.Char(related="product_id.barcode", string="Código")
    # mrc_rel1 = fields.Many2one(related="product_id.marca_id", string="Marca Rel")
    # mrc_rel2 = fields.Char(related="product_id.marca", string="Marca")

#move line
class InheritedMoveMod(models.Model):
    _inherit = "account.move"

    purchase_type = fields.Selection([
        ('product', 'PRODUCTO'),
        ('servicio', 'SERVICIO')
    ], string='Type Order', index=True, copy=False, default='product', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        moves = super(InheritedMoveMod,self).create(vals_list)

        try:
            for move, vals in zip(moves, vals_list):
                if 'purchase_type' in vals:
                    move.purchase_type = vals['purchase_type']
        except ValueError:
            pass

        return moves

class InheritedMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends('display_type', 'company_id')
    def _compute_account_id(self):
       
        #Account Payable
        # account_type = line.account_id.account_type

       res = super(InheritedMoveLine,self)._compute_account_id()
       logging.info("Antes del recorrido del objeto")
       myaccount = self.env['account.account'].search([('code', '=', '612000')], limit=1)
       
       for line in self:
            if line.display_type != 'payment_term' and line.move_id.purchase_type == "servicio":
                logging.info("Antes:::::ID::::::" + str(line.account_id))
                logging.info("Antes:::::NAME::::::" + str(line.account_id.name))
                line.account_id = myaccount.id ## ID TO CHANGE 612000 #28
                logging.info("Después:::ID::::::::" + str(line.account_id))
                logging.info("Después:::NAME::::::::" + str(line.account_id.name))
    