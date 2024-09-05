# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
import logging

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
    # Campo calculado de fecha de finalización de mantenimiento
    end_maintenance_calc = fields.Date(string="Fecha de finalización de Mantenimientos (Calculada)", compute="_calculate_fecha_fin")
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

    def _get_numero_ordinal(self, numero):
        sufijos_ordinales = {
            1: 'er',
            2: 'do',
            3: 'er',
            4: 'to',
            5: 'to',
            6: 'to',
            7: 'mo',
            8: 'vo',
            9: 'no',
            10: 'mo'
        }
        sufijo = sufijos_ordinales.get(numero, 'to')
        return f"{numero}{sufijo}"
    
    def create_ticket(self):
        fechas = self._distribute_dates(self.fecha_inicio_mantenimientos, self.frecuencia_mantenimientos, self.cantidad_mantenimientos)
        for i, fecha in enumerate(fechas):
            logging.info("Fecha..." +  str(fecha))
            numero_orden = i + 1
            nombre = "(" + self.name + ") " + self._get_numero_ordinal(numero_orden) + " Mantenimiento " + self.partner_id.name 
            self.insert_ticket(fecha, nombre)
        self.show_button = "1"

    def _calculate_fecha_fin(self, meses=None):
        # if self.fecha_inicio_mantenimientos:
        #Toma la manual por encima de la calculada, es decir si el usuario
        for record in self:
            if meses:
                if record.start_maintenance_calc:
                    fecha_inicio = fields.Date.from_string(record.start_maintenance_calc)
                    end_manintenance_calc = fecha_inicio + relativedelta(months=meses)
                    return end_manintenance_calc.strftime('%Y-%m-%d')
                elif record.start_maintenance_manual:
                    fecha_inicio = fields.Date.from_string(record.start_maintenance_manual)
                    end_maintenance_calc = fecha_inicio + relativedelta(months=meses)
                    return end_maintenance_calc.strftime('%Y-%m-%d')
                else:
                    return False
        else:
            return False
    
    def _distribute_dates(self, fecha_inicio, frecuencia, cantidad):
        fechas = []
        for i in range(cantidad):
            nueva_fecha = fecha_inicio + relativedelta(months=frecuencia * i)
            fechas.append(nueva_fecha.strftime('%Y-%m-%d'))
        return fechas

    # @api.onchange('sale_order_template_id','fecha_inicio_mantenimientos')
    # @api.depends('sale_order_template_id','fecha_inicio_mantenimientos')
    # @api.onchange('fecha_inicio_mantenimientos')
    # @api.depends('fecha_inicio_mantenimientos')
    # def _compute_fecha_fin(self):
    #     for order in self:
    #         order.fecha_fin_mantenimientos = False
    #         if order.sale_order_template_id and order.sale_order_template_id.recurring_rule_count:
    #             order.fecha_fin_mantenimientos = order._calculate_fecha_fin(order.sale_order_template_id.recurring_rule_count)


            #rECURRENCIA DEL MANTENIMIENTO
            # Si cambia la orden, fecha de inicio de mantenimiento. Depende de ambas
            # A la fecha se le calcula la orden.
            #  

    # 
    @api.onchange('start_maintenance_manual','sale_register_id.frecuencia','sale_serie_id.frec_mantenimiento')
    @api.depends('start_maintenance_manual','sale_register_id.frecuencia','sale_serie_id.frec_mantenimiento')
    def _compute_fecha_fin(self):
        #la serie esta por encima de la orden de venta #la frecuencia se toma de la serie
        for order in self:
            order.end_maintenance_calc = False
            if order.sale_serie_id and order.sale_serie_id.frec_mantenimiento:
                order.end_maintenance_calc = order._calculate_fecha_fin(order.sale_serie_id.frec_mantenimiento)
            elif order.sale_register_id and order.sale_register_id.frecuencia:
                order.end_maintenance_calc = order._calculate_fecha_fin(order.sale_register_id.frecuencia)
            else:
                order.end_maintenance_calc = False
    
    
    



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



#COPY
# -*- coding: utf-8 -*-
# from odoo import models, fields, api, exceptions
# from dateutil.relativedelta import relativedelta
# from odoo.exceptions import ValidationError
# from datetime import datetime, timedelta

# import logging
# _logger = logging.getLogger(__name__)


# class customers_fields(models.Model):
#     _inherit = 'sale.order'

#     total_monto_proyecto = fields.Float(
#     string="Total del Contrato",
#     default=0.00,
#     store= True
#     )

#     total_monto_facturado = fields.Float(
#     string="Monto Facturado",
#     default=0.00
#     ,compute='_compute_project_amount',
#     readonly=True
#     )
#     total_monto_pagado = fields.Float(
#     string="Monto Pagado",
#     default=0.00
#     ,compute='_compute_project_amount',
#     readonly=True
#     )

#     total_monto_pendiente= fields.Float(
#     string="Monto Pendiente",
#     default=0.00
#     ,compute='_compute_project_pending_amount',
#     readonly=True
#     )
#     fecha_inicio_garantia= fields.Date(
#     string="Fecha inicio de la garantía",
#     compute='_compute_project_amount',
#     readonly=True
#     )
#     fecha_fin_garantia= fields.Date(
#     string="Fecha fin de la garantía",
#      readonly=True,
#     compute='_compute_project_amount')
    
#     fecha_inicio_vigencia_ext = fields.Date(string='Fecha inicio de la vigencia de garantía Extendida con fábrica')
#     fecha_fin_vigencia_ext = fields.Date(string='Fecha fin de la vigencia de garantía Extendida con fábrica')

#     fecha_inicio_mantenimientos= fields.Date(
#     string="Inicio de Mantenimiento"
#     )

#     cantidad_mantenimientos = fields.Integer(string="Cantidad de Mantenimientos")

#     show_button = fields.Char(string="Mostrar Botón")

#     fecha_fin_mantenimientos = fields.Date(
#     string="Fecha Fin Mantenimeinto",
#     compute='_compute_fecha_fin',
#     readonly=True
#     )

#     frecuencia_mantenimientos = fields.Integer(string="Frecuencia de Mantenimientos", compute='_compute_frecuencia', readonly=True)  
#     fechas_mantenimientos = fields.Text(string="Fechas de Mantenimientos", compute='_compute_fechas_mantenimientos', readonly=True)
 

#     @api.constrains('fecha_inicio_vigencia_ext', 'fecha_fin_vigencia_ext')
#     def validar_fechas(self):
#         for record in self:
#             if record.fecha_inicio_vigencia_ext and record.fecha_fin_vigencia_ext:
#                 if record.fecha_inicio_vigencia_ext > record.fecha_fin_vigencia_ext:
#                     raise ValidationError("La fecha de inicio de la garantía extendida con fábrica no puede ser mayor que la fecha de final.")
    
#     @api.onchange('state')
#     @api.depends('state')
#     def _compute_project_amount(self):
#         var_monto_fact = 0.00
#         var_monto_pag= 0.00
#         var_one_posted = 0
#         str_mes="Meses"
#         garantia=""
#         fecha_inicio_garantia=""
#         fecha_fin=""
#         for order in self:
#             # Obtener una lista de IDs a partir de los objetos account.move en order.invoice_ids
#             try:
#                 logging.info("STATE INGRESO...")
#                 #self.garantia_sale="Meses.."
#                 tickets = self.env['helpdesk.ticket'].search([('sale_order_id', '=', self.id), ('stage_id', '=', 4)], limit=1)
#                 logging.info(str(tickets))
#                 logging.info(str(tickets.custom_product_id.id))
#                 fecha_inicio_garantia = tickets.date_last_stage_update
#                 tickets_stock_info=self.env['stock.quant'].search([('id', '=', tickets.custom_product_id.id)])
#                 logging.info(str(tickets_stock_info))
#                 garantia=tickets_stock_info.product_id.garantia
#                 logging.info(str(garantia))
#                 logging.info(str(fecha_inicio_garantia))
#                 fecha_garantia = datetime.strptime(str(fecha_inicio_garantia), '%Y-%m-%d %H:%M:%S')
#                 fecha_fin=fecha_garantia+relativedelta(months=garantia)
#                 logging.info(str(fecha_fin))
#                 if garantia==1:
#                     str_mes="Mes"
#             except Exception as e:
#                 logging.info("LOAD STATE="+str(e)) 
#             order.total_monto_facturado = 0.00
#             order.total_monto_pagado = 0.00
#             #order.garantia_sale=str(garantia)+" "+str_mes
#             order.garantia_sale_ticket=str(garantia)+" "+str_mes
#             order.fecha_inicio_garantia=fecha_inicio_garantia
            
#             order.fecha_fin_garantia=fecha_fin
#             for facturas in order.invoice_ids:
#                 if facturas.state == 'posted':                 
#                     var_monto_fact = var_monto_fact + facturas.amount_total
#                     var_monto_pag = var_monto_pag + (facturas.amount_total-facturas.amount_residual)
#                     var_one_posted = 1
                    
#             if var_one_posted == 1:
#                 order.total_monto_facturado = var_monto_fact
#                 order.total_monto_pagado = var_monto_pag
#             else:
#                 order.total_monto_facturado = 0.00
#                 order.total_monto_pagado = 0.00
         
            
        
            
#     @api.depends('cantidad_mantenimientos')
#     def _compute_frecuencia(self):
#         for order in self:
#             order.frecuencia_mantenimientos = 0
#             if order.cantidad_mantenimientos and order.sale_order_template_id and order.sale_order_template_id.recurring_rule_count:
#                 order.frecuencia_mantenimientos = order.sale_order_template_id.recurring_rule_count / order.cantidad_mantenimientos

#     @api.onchange('total_monto_proyecto')
#     @api.depends('total_monto_proyecto')
#     def _compute_project_pending_amount(self):
#         for order in self:
#             order.total_monto_pendiente = 0.00
#             var_monto_fact = 0.00
#             for facturas in order.invoice_ids:
#                 if facturas.state == 'posted':                
#                     var_monto_fact = var_monto_fact + (facturas.amount_total-facturas.amount_residual)
#             if var_monto_fact > 0 and order.total_monto_proyecto > 0:
#                 order.total_monto_pendiente = order.total_monto_proyecto - var_monto_fact
#             else:
#                  order.total_monto_pendiente = 0.00
                 


#     @api.depends('fecha_inicio_mantenimientos', 'frecuencia_mantenimientos', 'cantidad_mantenimientos')
#     def _compute_fechas_mantenimientos(self):
        
#         for order in self:
#             order.fechas_mantenimientos = ""
#             if order.fecha_inicio_mantenimientos and order.frecuencia_mantenimientos and order.cantidad_mantenimientos:
#                 fechas = order._distribute_dates(order.fecha_inicio_mantenimientos, order.frecuencia_mantenimientos, order.cantidad_mantenimientos)
#                 texto_fechas = []
#                 for i, fecha in enumerate(fechas):
#                     numero_orden = i + 1
#                     texto_fechas.append(f"{self._get_numero_ordinal(numero_orden)} mantenimiento - {fecha}")
#                 order.fechas_mantenimientos = "\n".join(texto_fechas)


    

#     def insert_ticket(self, fecha, nombre):
#         # Save the move info
#         order_line_id = 0
#         for line in self.order_line:
#            order_line_id = line.id

#         self.env['helpdesk.ticket'].create({
#             'team_id': 7,
#             'name': nombre,
#             'sale_order_id':self.id,
#             'fecha_inicio':fecha,
#             'fecha_fin': fecha,
#             'sale_client_id': order_line_id,
#             'sale_line_id': order_line_id,
#             'partner_id': self.partner_id.id
#         })
