#-*- coding: utf-8 -*-

from odoo import models, fields, api
mdl_res_partner = "res.partner"
mdl_stock_location = "stock.location"

class transfer_fields(models.Model):
    _name = 'transfer_fields.transfer_fields'
    _description = 'transfer_fields.transfer_fields'

    name_test = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

#Our Change
    # @api.model
    # def create(self, vals):
    #     # Do some business logic, modify vals...
    #     ...
    #     # Then call super to execute the parent method
    #     return super().create(vals)

class InheritedModelStockPicking(models.Model):
    _inherit = "stock.picking"

    new_field = fields.Char(string="New Field")

    def button_validate(self):
        print("We are here")
        return super().button_validate()


class InheritedModelStockMove(models.Model):
    _inherit = "stock.move"

    # new_field = fields.Char(string="New Field")

    def _action_done(self, cancel_backorder=False):
        print(self)
        print("Making changes")
        stock_valuation_layers = self.env['stock.valuation.layer']
        print(stock_valuation_layers)
        return super()._action_done()
    

class InheritedModelStockLocation(models.Model):
    _inherit = mdl_stock_location

    clienteref_ids = fields.Many2many(mdl_res_partner, string="Clientes")

    region_id = fields.Many2one("res.country.state", string="Region", domain=[("country_id","=", "Panama")])
    # region_name = fields.Char(string="Provincia", related="region_id.name")

class InheritedModelResPartner(models.Model):
    _inherit = mdl_res_partner

    locations_ids = fields.Many2many(mdl_stock_location, string="Ubicaciones")


class InheritedModelMaintenenceRequest(models.Model):
    _inherit = "maintenance.request"

    partner_id = fields.Many2one(mdl_res_partner, string="Cliente")
    locationmain_id = fields.Many2one(mdl_stock_location, string="Institución", domain=[("location_id","=", 3)])
    tecnicos_ids = fields.Many2many("res.users", string="Tecnicos Acompañantes")


    @api.onchange("partner_id")
    def _onchange_partner_id_domain_location(self):
        domain = []
        for record in self:
        #print("soy yo")
            if  record.partner_id:
                print("Cliente", record.partner_id)
                print("UBICACIONES", record.partner_id.locations_ids)
                # Construct a list of IDs of the fetched sales orders
                my_locations_ids = list(record.partner_id.locations_ids.ids)
                #self.locationmain_id = [(6, 0, my_locations_ids)]
                domain = {'domain':{'locationmain_id': [("location_id","=", 3), ('id', 'in', my_locations_ids)]}} 
                return domain
            else:
                #self.locationmain_id = [(5,)]
                return {'domain':{'locationmain_id': []}}

    @api.onchange("locationmain_id")
    def _onchange_locationmain_id_domain_partner_id(self):
        domain = []
        for record in self:
        #print("soy yo")
            if  record.locationmain_id:
                print("Ubicación", record.locationmain_id)
                print("Clientes", record.locationmain_id.clienteref_ids)
                # Construct a list of IDs of the fetched sales orders
                my_clients_ids = list(record.locationmain_id.clienteref_ids.ids)
                domain = {'domain':{'partner_id': [('id', 'in', my_clients_ids)]}} 
                return domain
            else:
                #self.locationmain_id = [(5,)]
                return {'domain':{'partner_id': []}}

class InheritedModelLote(models.Model):
    _inherit = "stock.lot"

    opciones = [
        ("funcional","Funcional"),
        ("desconocido","Desconocido"),
        ("no_funcional","No Funcional"),
        ("pendiente","Pendiente Instalación"),
    ]
    encargados = [
        ("tecnico", "Servicio Tecnico"),
        ("it", "IT")
    ]
    garantia = fields.Integer(string="Garantia (Meses)")
    state_equipment = fields.Selection(opciones, string="Estado del Equipo")
    modalidad_encar = fields.Selection(encargados, string="Modalidad Encargada")
    orden_compra = fields.Char(string="Orden de Compra", default="N/A")
    contrato_old = fields.Char(string="Contrato Viejo", default="N/A")
    ficha = fields.Char(string="Ficha tecnica", default="N/A")

class InheritedModeProduct(models.Model):
    _inherit = "product.product"

    #relacionados
    marca = fields.Char("Marca", defaul="N/A")
    modelo = fields.Char("Modelo", default ="N/A")

class InheritedModeQuant(models.Model):
    _inherit = "stock.quant"

    #relacionados
    garantia_rl = fields.Integer("Garantia lote", related="lot_id.garantia")
    ficha_rl = fields.Char("Ficha", related="lot_id.ficha")
    marca_rl = fields.Char("Marca", related="product_id.marca")
    modelo_rl = fields.Char("Modelo", related="product_id.modelo")
    region_rl = fields.Char("Region", related="location_id.region_id.name")






    
