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

    tipo_opciones = [
            ("CSS", "CSS"),
            ("MINSA", "MINSA"),
            ("Privado", "Privado"),
            ("Publico", "Público"),
        ]

    clienteref_ids = fields.Many2many(mdl_res_partner, string="Clientes")

    region_id = fields.Many2one("res.country.state", string="Region", domain=[("country_id","=", "Panama")])
    # region_name = fields.Char(string="Provincia", related="region_id.name")
    tipo = fields.Selection(tipo_opciones, string="Tipo de Institución")

class InheritedModelResPartner(models.Model):
    _inherit = mdl_res_partner

    locations_ids = fields.Many2many(mdl_stock_location, string="Ubicaciones")


class InheritedModelMaintenenceRequest(models.Model):
    _inherit = "maintenance.request"

    partner_id = fields.Many2one(mdl_res_partner, string="Cliente")
    locationmain_id = fields.Many2one(mdl_stock_location, string="Institución", domain=[("location_id","=", 3)])
    tecnicos_ids = fields.Many2many("res.users", string="Tecnicos Acompañantes")
    #quants_ids
    # quants_modificado_ids = fields.One2many(comodel_name = "stock.quant", inverse_name="maintenance_id",string="Productos Ubicados")
    # quants_modificado_id = fields.Many2one(comodel_name = "stock.quant", string="Productos Ubicados")
    quants_ids_rl = fields.One2many(string="Cantidades", related="locationmain_id.quant_ids")

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
                domain = {'domain':{'locationmain_id': [("location_id","=", 3), ('id', 'in', my_locations_ids)], 'quants_ids_rl':[('cliente_lot_rl', '=', record.partner_id)]}} 
                #print("LOS RECORDS ASOCIADOS: ", if record.quants_ids_rl.cliente_lot_rl)
                # for r in  record.quants_ids_rl:
                #     if r.cliente_lot_rl == record.partner_id:
                #         print("My cliente", r.cliente_lot_rl)
                #         self.quants_ids_rl = r
                #añade dominio cuando cliente cambia
                
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
                #,'quants_modificado_ids':[('id', 'in', record.locationmain_id.quant_ids.ids)]
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
    #garantia = fields.Integer(string="Garantia (Meses)")
    #related
    state_equipment = fields.Selection(opciones, string="Estado del Equipo")
    modalidad_encar = fields.Selection(encargados, string="Modalidad Encargada")
    #orden_compra = fields.Char(string="Orden de Compra", default="N/A")
    #contrato_old = fields.Char(string="Contrato Viejo", default="N/A")
    ficha = fields.Char(string="Ficha tecnica", default="N/A")
    install_date = fields.Date(string="Fecha de instalación")
    frecuencia_mantenimiento = fields.Integer(string="Frecuencia de Mantenimiento (Meses)")

    #Contact Fields
    contact = fields.Char(string="Contacto" , default="N/A")
    tel_contact = fields.Char(string = "Teléfono" , default="N/A")
    #reserma-fabrica no al cliente #yo estoy cubierto con fabrica
    garantia_fab_inicio = fields.Date(string="Garantia con Fabrica inicio")
    garantia_fab_fin = fields.Date(string="Garantia con Fabrica fin")
    garantia_fab = fields.Integer(string="Garantia con Fabrica (Años)")

    #garantia de equipo
    gar_extend = fields.Char(string="Garantia extendida", default="N/A")
    vencimiento_gar_extend = fields.Date(string="Vencimiento de Garantia Extendida")

    #sale id
    sale_id = fields.Many2one("sale.order", string="Suscription", domain=[("is_suscription","=", True)])
    # descomentar
    garantia_rl = fields.Char("Garantia", related="sale_id.warranty_duration")
    contrat_oc_rl = fields.Char("Contrato/OC", related="sale_id.contract_oc")
    frecuencia_rl = fields.Integer(string="Frecuencia de Mantenimiento (Meses)", related="sale_id.frecuencia")
    contrato_old_rl = fields.Char("Contrato Viejo", related="sale_id.contrato_old")
    fecha_contrato_rl = fields.Date("Fecha de inicio de Contrato / Orden de Compra", related="sale_id.inicio_contrato")
    #cliente del contrato y por tanto dueño del equipo
    cliente_id_rl = fields.Many2one(string="Cliente", related="sale_id.partner_id")

    @api.onchange("garantia_fab_inicio", "garantia_fab_fin")
    def _onchange_garantia(self):
        print("Her we are!")        
        # for record in self:
        if self.garantia_fab_fin and self.garantia_fab_inicio:
            delta = self.garantia_fab_fin - self.garantia_fab_inicio
            delta = (delta.days/30)
            self.garantia_fab = (delta/12)
        else:
            self.garantia_fab=0

class InheritedModeProduct(models.Model):
    _inherit = "product.product"

    #relacionados
    marca = fields.Char("Marca", default="N/A")
    modelo = fields.Char("Modelo", default ="N/A")

class InheritedModeQuant(models.Model):
    _inherit = "stock.quant"

    #relacionadosS
    #garantia_rl = fields.Integer("Garantia lote", related="lot_id.garantia_rl")
    ficha_rl = fields.Char("Ficha", related="lot_id.ficha")
    install_rl = fields.Date("Fecha de Instalación", related="lot_id.install_date")
    contrato_oc_rl = fields.Char("Contrato/OC", related="lot_id.contrat_oc_rl")
    cliente_lot_rl = fields.Many2one(string="Contrato/OC", related="lot_id.cliente_id_rl")
    marca_rl = fields.Char("Marca", related="product_id.marca")
    modelo_rl = fields.Char("Modelo", related="product_id.modelo")
    region_rl = fields.Char("Region", related="location_id.region_id.name")
    tipo_rl = fields.Selection("Tipo de Institución", related="location_id.tipo")
    # maintenance_id = fields.Many2one(comodel_name = "maintenance.request",inverse='quants_modificado_ids', string="Solicitud de Mantenimiento")

class InheritModelSale(models.Model):
    _inherit = "sale.order"

    contract_oc = fields.Char(string= "Orden de Compra/Contrato")
    observacion = fields.Char(string= "Observación")
    frecuencia = fields.Integer(string="Frecuencia de Mantenimiento (Meses)")
    is_suscription = fields.Boolean("Is Suscription?", default=False)
    contrato_old = fields.Char(string="Contrato Viejo", default="N/A")
    inicio_contrato = fields.Date(string="Fecha de inicio de Contrato / Orden de Compra")












    
