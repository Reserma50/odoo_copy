# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

mdl_sale_order = 'sale.order'
mdl_partner = "res.partner"
mdl_product = "product.template"
mdl_stock_lot = "stock.lot"
mdl_rs_custom_maintenance = "rs_custom_maintenance"
mdl_stock_location = "stock.location"
mdl_maintenance_team = 'maintenance.team'
mdl_maintenance_request = 'maintenance.request'

class RsCustomMaintenance(models.Model):
    _name = 'rs_custom_maintenance'
    _description = 'rs_custom_maintenance'

    name = fields.Char(store=True,compute="_compute_recurrence_name")
    #compute="_compute_recurrence_name", 
    cantidad = fields.Integer(required=True, string="Cantidad de Mant.", help="Cantidad de Mantenimientos a realizar")
    start_maintenance_calc = fields.Date(string="Fecha Inicial del Mantenimiento (Calculada)", help="Puede ser obtenida del primer registro de Ticket Preventivo")
    start_maintenance_manual = fields.Date(string="Fecha Inicial del Mantenimiento (Manual)", help="El usuario Ingresa manualmente sino existe el preventivo")
    sale_register_id = fields.Many2one(comodel_name=mdl_sale_order, string="Orden de Venta/Contrato/OC")
    sale_client = fields.Many2one(related="sale_register_id.partner_id", string="Cliente") #se calcula a partir
    sale_location_id = fields.Many2one(comodel_name=mdl_stock_location, string="Sitio")
    sale_product_id = fields.Many2one(comodel_name=mdl_product, string="Equipo en sitio")
    sale_serie_id = fields.Many2one(comodel_name=mdl_stock_lot, string="Serie en Sitio")
    # frecuencia_man = fields.Integer(related="sale_serie_id.frec_mantenimiento",string="Frecuencia del Mantenimiento (MESES)", )
    frecuencia_man = fields.Integer(string="Frecuencia del Mantenimiento (MESES)", )

    #Frecuencia de Mantenimiento
    #

    maintenance_team_id = fields.Many2one(comodel_name=mdl_maintenance_team, string="Tipo de Mantenimiento")
    already_ticket_amount_import = fields.Integer(string="Cantidad de Mantenimientos ya realizados")
    state = fields.Selection([('draft', 'Draft'), ('lock', 'Locked'), ('unlock', 'Unlocked')], default = 'draft')    
    #Campos que se actualizan a partir de los campos anteriores
    maintenances_ids = fields.One2many(comodel_name=mdl_maintenance_request, inverse_name='recurrence_main_id', string="Mantenimientos")

    def maintenance_set_confirm(self):
        self.write({'state':'lock'})

    @api.depends('sale_register_id', 'sale_location_id.name', 'sale_serie_id.name')
    def _compute_recurrence_name(self):
        for record in self:
            record.name = (record.sale_register_id.contract_oc or '') + '/' + (record.sale_location_id.name or '') + '/' + (record.sale_serie_id.name or _('No Serie'))
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


class InheritedSaleOrderV(models.Model):
    _inherit = mdl_sale_order
    mantenimientos_contract_ids = fields.One2many(comodel_name=mdl_rs_custom_maintenance, inverse_name='sale_register_id', string='Mantenimientos asociados a Contrato')

class InheritedProductTemplateV(models.Model):
    _inherit = mdl_product
    mantenimientos_products_ids = fields.One2many(comodel_name=mdl_rs_custom_maintenance, inverse_name='sale_product_id', string='Mantenimientos asociados a Producto')

class InheritedModelMaintenenceTeam(models.Model):
    _inherit = mdl_maintenance_team

    request_team_id = fields.One2many(comodel_name=mdl_rs_custom_maintenance, inverse_name='maintenance_team_id', string='Tipo de Ticket')


class InheritedModelMaintenenceRequest(models.Model):
    _inherit = mdl_maintenance_request

    recurrence_main_id = fields.Many2one(comodel_name=mdl_rs_custom_maintenance, string="Solicitudes de Mantenimientos")