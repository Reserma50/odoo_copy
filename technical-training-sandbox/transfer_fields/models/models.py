#-*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _, Command
import re, datetime
import logging
from dateutil.relativedelta import relativedelta


mdl_res_partner = "res.partner"
mdl_stock_location = "stock.location"
mld_sale_order = "sale.order"
mdl_product_product = "product.product"
mdl_stock_lot = "stock.lot"
mdl_maintenance_request = 'maintenance.request'
mdl_marcaft_fields = "marcaftk.fields"
mdl_location_fields = "location.fields"
mdl_periferico_fields = "perifericosmodel.fields"

class transfer_fields(models.Model):
    _name = 'transfer_fields.transfer_fields'
    _description = 'transfer_fields.transfer_fields'

    name = fields.Char(string="Nombre")
    code_modalidad = fields.Integer(string="Código", default=lambda self: self.env['ir.sequence'].next_by_code('increment_your_field'))
    producto_ids = fields.One2many(comodel_name = mdl_product_product, inverse_name="modalidad_id",string="Productos")
    color = fields.Integer('Color')

    _sql_constraints = [
        ('transfer_fields_tag_unique_name', 'UNIQUE(name)','El nombre de la Modalidad debe ser único.'),
    ]

class location_fields(models.Model):
    _name = 'location.fields'
    _description = 'location fields'

    name = fields.Char(string="Nombre")
    lotes_series_ids = fields.One2many(comodel_name = mdl_stock_lot, inverse_name="loc_institution_id",string="Lotes/Series")
    color = fields.Integer('Color')

    _sql_constraints = [
        ('location_fields_tag_unique_name', 'UNIQUE(name)','El nombre de la ubicación debe ser único.'),
    ]


class marcaftk_fields(models.Model):
    _name = 'marcaftk.fields'
    _description = 'marcaftk fields'

    name = fields.Char(string="Nombre")
    code_marcaft = fields.Integer(string="Código", default=lambda self: self.env['ir.sequence'].next_by_code('increment_your_marca'))
    producto_mrc_ids = fields.One2many(comodel_name = mdl_product_product, inverse_name="marca_id", string="Productos")
    periferico_mrc_ids = fields.One2many(comodel_name = mdl_periferico_fields, inverse_name="mrc_periferico_id", string="Periféricos")
    color = fields.Integer('Color')

    _sql_constraints = [
        ('marcaft_fields_tag_unique_name', 'UNIQUE(name)','El nombre de la marca debe ser único.'),
    ]

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
    maintenance_ids = fields.One2many(comodel_name = mdl_maintenance_request, inverse_name="locationmain_id", string="Mantenimientos")
    region_id = fields.Many2one("res.country.state", string="Region", domain=[("country_id","=", "Panama")])
    tipo = fields.Selection(tipo_opciones, string="Tipo de Institución")

class InheritedModelResPartner(models.Model):
    _inherit = mdl_res_partner

    locations_ids = fields.Many2many(mdl_stock_location, string="Ubicaciones")


class InheritedModelMaintenenceRequest(models.Model):
    _inherit = mdl_maintenance_request

    partner_id = fields.Many2one(mdl_res_partner, string="Cliente")
    locationmain_id = fields.Many2one(mdl_stock_location, string="Institución", domain=[("location_id","=", 3)])
    tecnicos_ids = fields.Many2many("res.users", string="Tecnicos Acompañantes")
    quants_ids_rl = fields.One2many(string="Cantidades", related="locationmain_id.quant_ids") #descomentar porque es funcional
    sale_id = fields.Many2one(string="Venta/Suscripción", comodel_name = mld_sale_order)
    
    nf_product_id = fields.Many2one(mdl_product_product, string="Producto")
    nf_lot_id = fields.Many2one(mdl_stock_lot, string="Lote / Serie")

    @api.onchange("partner_id")
    def _onchange_partner_id_domain_location(self):
        domain = []
        for record in self:
            if  record.partner_id:
                print("Cliente", record.partner_id)
                print("UBICACIONES", record.partner_id.locations_ids)
                # Construct a list of IDs of the fetched sales orders
                my_locations_ids = list(record.partner_id.locations_ids.ids)
                my_sale_ids = list(record.partner_id.sale_order_ids.ids)
                domain = {'domain':{'locationmain_id': ["&", ("location_id","=", 3),('id', 'in', my_locations_ids)], 'sale_id':[("id", "in", my_sale_ids)]}} 
                
                return domain
            else:
                return {'domain':{'locationmain_id': [], 'sale_id':[]}}

    @api.onchange("locationmain_id")
    def _onchange_locationmain_id_domain_partner_id(self):
        domain = []
        for record in self:
            if  record.locationmain_id:
                print("Ubicación", record.locationmain_id)
                print("Clientes", record.locationmain_id.clienteref_ids)
                # Construct a list of IDs of the fetched sales orders
                my_clients_ids = list(record.locationmain_id.clienteref_ids.ids)
                products = record.quants_ids_rl.product_id.ids
                domain = {'domain':{'nf_product_id': [('id', 'in', products)], 'partner_id':[('id', 'in', my_clients_ids)]}} 
                 
                return domain
            else:
                return {'domain':{'partner_id': []}}
            
    @api.onchange("nf_product_id")
    def _onchange_nf_product_id_domain_lot_id(self):
        domain = []
        for record in self:
            product = record.nf_product_id
            if  product:
                my_list_ser = record.quants_ids_rl.lot_id #extract ids in list
                my_new_array = []
                for rec in my_list_ser:
                    if product.id == rec.product_id.id:
                        my_new_array.append(rec.id)
                
                # add product domai
                domain = {'domain':{'nf_lot_id': [('id', 'in', my_new_array)]}} 
                 
                return domain
            else:
                
                return {'domain':{'nf_lot_id': []}}
            
    @api.model
    def open_record_form_view_maintenance(self):
        action = {
            'res_model': mdl_maintenance_request,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'name': 'Edit Record',
            'view_id': self.env.ref("base.view_partner_form").id,
            #'res_id': record_id,
            'target': 'self',
        }
        return action

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
    # garantia = fields.Integer(string="Garantia (Meses)")
    #related
    state_equipment = fields.Selection(opciones, string="Estado del Equipo")
    modalidad_encar = fields.Selection(encargados, string="Modalidad Encargada")
    # orden_compra = fields.Char(string="Orden de Compra", default="N/A")
    #contrato_old = fields.Char(string="Contrato Viejo", default="N/A")
    ficha = fields.Char(string="Ficha tecnica", default="N/A")
    install_date = fields.Date(string="Fecha de instalación", tracking=True)
    # este campo proviene del sale.order por eso sta comentado
    frec_mantenimiento = fields.Integer(string="Frecuencia del Mantenimiento (Meses)")

    #Contact Fields
    contact = fields.Char(string="Contacto" , default="N/A")
    tel_contact = fields.Char(string = "Teléfono" , default="N/A")
    #reserma-fabrica no al cliente #yo estoy cubierto con fabrica
    garantia_fab_inicio = fields.Date(string="Garantia con Fabrica inicio")
    garantia_fab_fin = fields.Date(string="Garantia con Fabrica fin")
    garantia_fab = fields.Integer(string="Garantia con Fabrica (Meses)", help="Antes estaba en Años")

    #PEDIDO
    pedido = fields.Char(string="Pedido")
    #Last Location
    my_last_location = fields.Char(string="Ubicación Actual",compute="_compute_last_loc")
    #



    #garantia de equipo
    gar_extend = fields.Char(string="Garantia extendida", default="N/A")
    vencimiento_gar_extend = fields.Date(string="Vencimiento de Garantia Extendida")

    #Garantia con el cliente
    gar_cliente = fields.Float(string="Garantia con el cliente (Años)")
    fin_gar_cliente = fields.Date(string="Fin de la garantia con el Cliente", compute="_compute_last_date_gar")

    #sale id #no esta bien definido la siguiente relacion porque un lote puede tener mas de un registro desde venta
    #sale_id = fields.Many2one("sale.order", string="Suscription", domain=[("is_suscription","=", True)])
    # descomentar 
    # garantia_rl = fields.Char("Garantia", related="sale_id.warranty_duration")
    # contrat_oc_rl = fields.Char("Contrato/OC", related="sale_id.contract_oc")
    # frecuencia_rl = fields.Integer(string="Frecuencia de Mantenimiento (Meses)", related="sale_id.frecuencia")
    # contrato_old_rl = fields.Char("Contrato Viejo", related="sale_id.contrato_old")
    # fecha_contrato_rl = fields.Date("Fecha de inicio de Contrato / Orden de Compra", related="sale_id.inicio_contrato")
    #cliente del contrato y por tanto dueño del equipo #loca campos anteriores se comentan para no llamarlos individualmente
    # cliente_id_rl = fields.Many2one(string="Cliente", related="sale_id.partner_id")
    # CONTRATOS/VENTAS
    sale_ids = fields.Many2many(comodel_name=mld_sale_order, string="Ventas/Contratos")
    en_contrato = fields.Boolean(string="En contrato?", compute="_compute_state_acuerdos")
    #CHILDS
    lot_id = fields.Many2one(comodel_name=mdl_stock_lot, string='Parent Lot', index=True, ondelete='cascade',
        help="The parent lote that includes this lote. Example : The 'Dispatch Zone' is the 'Gate 1' parent location.")

    child_lot_ids = fields.One2many(comodel_name=mdl_stock_lot, inverse_name='lot_id', string='Contains Lot')
    #Registros de Servicios
    mytickets_ids = fields.One2many(comodel_name=mdl_maintenance_request, inverse_name='nf_lot_id', string="Servicios de asistencia")
    # DATA IT
    ip_field = fields.Char(string="IP")
    loc_institution_id = fields.Many2one(comodel_name=mdl_location_fields, string="Ubicación en sitio")#by convention
    
    # last partner
    thepartner_id = fields.Many2one(comodel_name="res.partner", string="El contacto final", help="Este campo se actualiza cada que se genera una nueva transacción Venta/OC/Contrato")

    # Perifericos 
    periferico_ids = fields.One2many(comodel_name=mdl_periferico_fields, inverse_name="lote_peri_id", string="Periféricos")

    @api.onchange("garantia_fab_inicio", "garantia_fab")
    def _onchange_garantia(self):
        print("Her we are!")        
        # for record in self:
        if self.garantia_fab and self.garantia_fab_inicio:
            # delta = self.garantia_fab_fin - self.garantia_fab_inicio
            # delta = (delta.days/30)
            # self.garantia_fab = (delta/12)
            self.garantia_fab_fin = self.garantia_fab_inicio + relativedelta(months=self.garantia_fab)

        else:
            self.garantia_fab = 0

    @api.depends("install_date")
    def _compute_last_date_gar(self):
        for record in self:
            if record.install_date and record.gar_cliente != 0:
                period=record.gar_cliente * 12

                record.fin_gar_cliente = record.install_date + relativedelta(months=int(period))

            else:
                record.fin_gar_cliente = 0

    @api.depends("quant_ids")
    def _compute_last_loc(self):
        for record in self:
            if record.name:
                logging.info("Loc:::::" + str(record.name))
                quant_record = self.env['stock.quant'].search([('lot_id', '=', record.id), ('quantity', '>=', 1)], limit=1)
                record.my_last_location = quant_record.location_id.complete_name
                logging.info("Calculada:::::" + str(quant_record.location_id))
            else:
                record.my_last_location = "N/A"

    #Definir fecha de instalación si esta en blanco. En caso de tener definido algo por el usuario
    @api.depends("mytickets_ids")
    def _calcular_fecha_install(self):
        logging.info("Calculada::::: Se dispara la función ")
        for record in self:
            if record.install_date:
                return record.install_date
            else:
                for ticket in record.mytickets_ids:
                    if ticket.maintenance_team_id.is_install and ticket.schedule_date and ticket.stage_id.id == 3:
                        record.install_date = ticket.schedule_date



    #Verificación de contratos o algo que lo respalde
    @api.depends("sale_ids")
    def _compute_state_acuerdos(self):
        for record in self:
            record.en_contrato = False
            if record.sale_ids:
                for rec in record.sale_ids:
                    # logging.info("Registro de SaleOrder:::::" + str(rec.name))
                    # quant_record = self.env['sale.order'].search([('id', 'in', record.sale_ids.ids)])
                    if not rec.fin_contrato:
                        # logging.info("Registro sin fecha")
                        continue 
                    # logging.info("Fecha del Registro:::::" + str(datetime.datetime(rec.fin_contrato.year,rec.fin_contrato.month,rec.fin_contrato.day)))
                    # logging.info("Contra fecha actual:::::" + str(fields.datetime.today()))
                    if datetime.datetime(rec.fin_contrato.year,rec.fin_contrato.month,rec.fin_contrato.day,23,59,59) >= fields.datetime.today():
                        record.en_contrato = True
                        # logging.info("Equipo vigente en contrato")
                        return True

class InheritedModeProduct(models.Model):
    _inherit = "product.template"

    #relacionados
    marca = fields.Char("Marca", default="N/A")
    modelo = fields.Char("Modelo", default ="N/A") 
    modalidad_id = fields.Many2one(comodel_name="transfer_fields.transfer_fields", string="Modalidad Relacionada")#by convention
    marca_id = fields.Many2one(comodel_name=mdl_marcaft_fields, string="Marca Relacionada")#by convention

class PerifericosModel_fields(models.Model):
    _name = 'perifericosmodel.fields'
    _description = 'Perifericos Model Fields'

    name = fields.Char(string="Nombre")
    code_base = fields.Char(string="Código")
    canti = fields.Integer(string="Cantidad")
    mrc_periferico_id = fields.Many2one(comodel_name=mdl_marcaft_fields, string="Marca .")#by convention
    lote_peri_id = fields.Many2one(comodel_name = mdl_stock_lot, string="Equipo")
    color = fields.Integer('Color')

    _sql_constraints = [
        ('code_base_fields_unique_name', 'UNIQUE(code_base)','El Código debe ser único.'),
    ]    


class InheritedModeQuant(models.Model):
    _inherit = "stock.quant"

    # garantia_rl = fields.Integer("Garantia lote", related="lot_id.garantia_rl")
    ficha_rl = fields.Char(related="lot_id.ficha", string="Ficha")
    install_rl = fields.Date(related="lot_id.install_date", string="Fecha de Instalación")
    cliente_rl = fields.Many2one(related="lot_id.thepartner_id", string="Dueño")
    # " se comenta" para evitar error
    # contrato_oc_rl = fields.Char("Contrato/OC", related="lot_id.contrat_oc_rl")
    # se comenta para evitar errores
    # cliente_lot_rl = fields.Many2one(string="Contrato/OC", related="lot_id.cliente_id_rl")
    marca_rl = fields.Char(related="product_id.marca", string="Marca")
    modelo_rl = fields.Char(related="product_id.modelo", string="Modelo")
    region_rl = fields.Char(related="location_id.region_id.name", string="Region")
    tipo_rl = fields.Selection(related="location_id.tipo", string="Tipo de Institución")
    # maintenance_id = fields.Many2one(comodel_name = mdl_maintenance_request,inverse='quants_modificado_ids', string="Solicitud de Mantenimiento")

    # Work around to open the model
    def open_form_action(self, *args, **kwargs):
        # Retrieve the record ID from the context or any other source
        value = None
        value = self.env.context.get('Lot_id')
        cliente = self.env.context.get('partner_id')
        # user = self.env.context.get('')
        # id of last one sale 
        # location id
        # product 
        # lote/serie
        # print("El tipo", type(value))
        # print("El valor", value)
        # print("THIS IS MY RECORD_ID", record_id)
        

        if self.id and value:
            print("here 1")
            action = self.open_new_record_form_view(self.id, value)
            return action
        elif self.id and value and cliente:
            print("here 2")
            action = self.open_new_record_form_view(self.id, value, cliente)
            return action
        elif self.id:
            print("here 3")
            action = self.open_old_record_form_view(self.id)
            return action
        else:
            print("IN FALSE STATEMENT")
            return False
    
    @api.model
    def open_new_record_form_view(self, *args, **kwargs):

        # for key, value in args.items():
        #     print("%s == %s" % (key, value))

        #" value_when_true if condition else value_when_false"
        self.ensure_one()
        action = {
            'res_model': mdl_maintenance_request,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            # 'nf_lot_id':args[0],
            'name': 'Crear Ticket',
            'view_id': self.env.ref("maintenance.hr_equipment_request_view_form").id,
            'target': 'new',
            'context': {
                # Agrega aquí los campos y valores predeterminados que necesitas
                'default_nf_lot_id': args[0] if len(args)> 0 else None,
                'default_nf_product_id': args[0] if len(args)> 0 else None,
                # default last partner
                # default location
            }
        }
        return action
    
    @api.model
    def open_old_record_form_view(self, record_id):
        action = {
            'res_model': mdl_maintenance_request,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'name': 'Edit Record',
            'view_id': self.env.ref("maintenance.hr_equipment_request_view_form").id,
            'res_id': record_id,
            'target': 'self',
        }
        return action

class InheritModelMaintenenceTeam(models.Model):
    _inherit = "maintenance.team"

    is_install = fields.Boolean(string="Es Equipo de Instalación", default=False)


class InheritModelSale(models.Model):
    _inherit = "sale.order"

    contract_oc = fields.Char(string= "Orden de Compra/Contrato", )
    observacion = fields.Char(string= "Observación")
    frecuencia = fields.Integer(string="Frecuencia de Mantenimiento (Meses)")
    is_suscription = fields.Boolean("Is Suscription?", default=False)
    data_export = fields.Boolean("Data Importada?", default=False)
    contrato_old = fields.Char(string="Contrato Viejo", default="N/A")
    inicio_contrato = fields.Date(string="Fecha de inicio de Contrato / Orden de Compra", help="Este campo esta dentro del apartado información adicional, de la versión enterprise.")
    fin_contrato = fields.Date(string="Fecha de fin de Contrato / Orden de Compra")
    # lotes y series
    serie_ids = fields.Many2many(comodel_name=mdl_stock_lot, name="Series/Lote")
    ticket_install_created = fields.Boolean(default=False, string="Ticket de instalación creado?")
    fecha_prevista_install = fields.Date(string="Fecha prevista para Instalación")
    maintenance_ids = fields.One2many(comodel_name=mdl_maintenance_request, string="Mantenimientos", inverse_name="sale_id")
    response_time = fields.Integer(string=" Tiempor de respuesta (Horas)")

    def action_set_install_ticket(self):
        '''isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface'''
        for record in self:
            if not record.ticket_install_created and record.state != 'cancel':
                # self.env[mdl_maintenance_request].
                maintenance_vals = self.preparar_ticket_install()
                request = self.env[mdl_maintenance_request].create(maintenance_vals)
                print("my_request", request)
                record.ticket_install_created = True
            else:
                raise exceptions.UserError('Ticket already exist!.')
        # isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface
        return True
    
    def preparar_ticket_install(self):
        '''
        Prepare dict with values to create a new maintenance
        '''
        self.ensure_one()
        maintenance_type = "Install"
        maintenance = self.env['maintenance.team'].search([('name', '=', maintenance_type)], limit = 1)
        print("Maintenece Type, ID", maintenance)
        if len(self.serie_ids) == 0:
            raise exceptions.UserError(('Porfavor seleccionar lote/serie para asignar al mantenimiento.'))
        else:
            lote_serie = self.serie_ids[0]
            # location = self.serie_ids[0].quant_ids.
            print("El lote o la serie es :", lote_serie)
            print("El producto :", lote_serie.product_id)
            
            print("Locations (all):", lote_serie.quant_ids.ids)
            # Assuming you want to filter stock.quant records with IDs 64 and 65 and quantity equals 1
            quant_record = self.env['stock.quant'].search([('id', 'in', lote_serie.quant_ids.ids), ('quantity', '=', 1)], limit = 1)
            print("Locations (1 quantity):", quant_record)

        if self.partner_id is None:
            raise exceptions.UserError(('Porfavor definir un cliente para asignar al mantenimiento.'))
        
        myname = ' '.join(('Instalación de ', str(lote_serie.product_id.name), str(quant_record.location_id.name))) 
        maintenance_vals = {
                'name': myname,
                'partner_id': self.partner_id.id,
                'locationmain_id': quant_record.location_id.id,
                'sale_id': self.id,
                'maintenance_team_id': maintenance.id, 
                'description': lote_serie.name, 
            }
        if self.fecha_prevista_install:
            maintenance_vals['schedule_date']=self.fecha_prevista_install
            

        return maintenance_vals
    
    @api.constrains('contract_oc')
    def _check_contract_oc(self):
        for record in self:
            if record.contract_oc:
                txt = record.contract_oc
                self.validar_cadena(txt)
    
    @api.constrains('contrato_old')
    def _check_contrato_viejo(self):
        for record in self:
            if record.contrato_old:
                txt = record.contrato_old
                self.validar_cadena(txt)

    def validar_cadena(self, cadena):
        # La expresión regular permite solo letras y números
        # patron = r'^[a-zA-Z0-9]+$'
        patron = r'^[a-zA-Z0-9/-]+$'
        # Comprobamos si la cadena cumple con el patrón
        if re.match(patron, cadena):
            return True
        else:
            raise exceptions.ValidationError("Ha ingresado un dato errado! Nota: Solo se permiten palabras, Números y símbolos especiales como guión (-) barra (/).")

    def name_get(self):
        '''SOBREESCRIBIENDO LA FUNCION NAME_GET DEL MODELO SALE.ORDER (SI, EXISTE)'''
        
        # if self._context.get('sale_show_partner_name'):
        result = []
        for record in self:
            if record.contract_oc:
                name = "%s - %s" % (record.name, record.contract_oc)
            else:
                name = record.name
            result.append((record.id, name))
        return result
        # return super().name_get()
        

    # def name_get(self):
    #     if self._context.get('sale_show_partner_name'):
    #         res = []
    #         for order in self:
    #             name = order.name
    #             if order.partner_id.name:
    #                 name = '%s - %s' % (name, order.partner_id.name)
    #             res.append((order.id, name))
    #         return res
    #     return super().name_get()

#add field to move line
# class InheritModelStockMoveLine(models.Model):
#     _inherit = "stock.move.line"

#     fabrica_gar_start = fields.Datetime(
#         string='Garantia con Fabrica Inicio', 
#         help='This is the date on which the product with this Serial Number may'
#         ' become inside warranty .')    
#     fabrica_gar_end = fields.Datetime(
#         string='Garantia con Fabrica Fin', 
#         help='This is the date on which the goods with this Serial Number may'
#         ' become out of warranty and ant the company must buy not an extend warranty.')   

#     compute='_compute_expiration_date', store=True














    
