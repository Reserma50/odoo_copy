from odoo import fields, models, api, Command, _, exceptions
from collections import defaultdict
from odoo.tools.float_utils import float_compare, float_is_zero
from dateutil.relativedelta import relativedelta

class InheritedFleetVehicleOdometer(models.Model):
    # _inherit = ['fleet.vehicle.odometer', 'mail.thread','mail.activity.mixin']
    _inherit = ['fleet.vehicle.odometer']


    def crear_servicios_manteniento(self, my_type, record):
        '''CREATE NEW MAINTENANCE WITH NEW SERVICE'''

        for field_name, field in self.fields_get().items():
            if field_name in self:
                print(f"Campo: {field_name}, Valor: {self[field_name]}")

        #create service
        servicio = self.env["fleet.vehicle.log.services"].create(
            {
            "vehicle_id": record.vehicle_id.id,
            "description":f" Mantenimiento de {my_type.name} requerido; Vehiculo alcanzó la referencia de {my_type.reference} ",
            "odometer_id" : record.id,
            "purchaser_id": record.driver_id.id,  # 
            "service_type_id":my_type.id,
            }
        )
        #create service
        print("\n Después de cargar servicio")
        for field_name, field in servicio.fields_get().items():
            if field_name in self:
                print(f"Campo: {field_name}, Valor: {self[field_name]}")
        #log maintenance
        return self.env['fleet.vehicle.log.maintenance'].create(
            {
                "description":f"Mantenimiento de {my_type.name} porque el Vehiculo alcanzó {my_type.reference} ",
                'vehicle_id': servicio.vehicle_id.id,
                "service_id":servicio.id,
                "driver_id": record.driver_id.id,  # 
                "odometer_id" : record.id,
                "service_type_id":my_type.id,   
                "odometer" : self.value,
            }
        )
        
    def create_maintenance(self, my_type, record): #record from fleet.vehicle.odometer
        '''CREATE MAINTENANCE WITH NEW SERVICES '''
        # print("\n *********************************************** \n")
        print("\n **** def create_maintenance(self, my_type, record):   CLASS [ODOMETER] **** \n")
        # print("\n *********************************************** \n")
        for field_name, field in self.fields_get().items():
            if field_name in self:
                print(f"Campo: {field_name}, Valor: {self[field_name]}")

        # Create service
        servicio = self.env["fleet.vehicle.log.services"].create(
            {
            "vehicle_id": record.vehicle_id.id,
            "description":f" Mantenimiento de {my_type.name} requerido; Vehiculo alcanzó la referencia de {my_type.reference} ",
            "odometer_id" : record.id,
            "purchaser_id": record.driver_id.id,  # 
            "service_type_id":my_type.id,
            "state":"done",
            }
        )
        
        # self.verify_output_values(servicio)

        return self.env['fleet.vehicle.log.maintenance'].create(
            {
                "description":f"Mantenimiento de {my_type.name} porque el Vehiculo alcanzó {my_type.reference} ",
                'vehicle_id': self.vehicle_id.id,
                "service_id":servicio.id,
                "driver_id": record.driver_id.id,  # 
                "odometer_id" : record.id,
                "service_type_id":my_type.id,   
                "odometer" : self.value,
                "complete": False,
                "set_kms":(self.value+my_type.reference)
            }
        )
    def actualizar_servicios_manteniento(self, my_type, last_maintenance):
        '''UPDATE MAINTENANCE NO CREATE SERVICES'''
        
        print("CAMPOS COMO LOS DE SELF! En la función actualizar!")
        self.verify_output_values(None)
        print("My Self vehicle model actualizando", self.vehicle_id.id)

        return last_maintenance.write(
            {
                'services_ids':[
                    Command.create({
                        "vehicle_id": self.vehicle_id.id,
                        "description":f" Mantenimiento de {my_type.name} requerido; Vehiculo alcanzó la referencia de {my_type.reference} ",
                        "odometer" : self.value,
                        "purchaser_id": self.driver_id.id,  # 
                        "service_type_id":my_type.id,   
                    })
                ],
                "kms_recorridos" : self.value,
            }
        )
    
    def verify_output_values(self, data):
        '''PRINT VALUES AND KEYS AFTER CREATE OR UPDATE OBJ'''
        for field_name, field in self.fields_get().items():
            if field_name in self:
                print(f"Campo: {field_name}, Valor: {self[field_name]}")
    
    def update_service_maintenance(self, my_type, last_maintenance, record, state='done', update=True):
        '''UPDATE MAINTENANCE, NEW SERVICES OR NO NEW SERVICES'''

        print("\n *********************************************** \n")
        print("\n **** def update_service_maintenance(self, my_type, last_maintenance, record, state='done', update=True): **** \n")
        print("\n *********************************************** \n")

        if not (state == "done" and update == False): #Crear Servicio #Actualizar Mantenimiento
            servicio = self.env["fleet.vehicle.log.services"].create(
                {
                "vehicle_id": record.vehicle_id.id,
                "description":f" Servicio de Mantenimiento de {my_type.name} requerido; Vehiculo alcanzó la referencia de {my_type.reference} ",
                "odometer_id" : record.id,
                "purchaser_id": record.driver_id.id,  # 
                "service_type_id":my_type.id,
                "state":state,
                }
            )
            
            #call function verify
            # self.verify_output_values(servicio)
            return last_maintenance.write(
                {
                    "description":f"Mantenimiento de {my_type.name} porque el Vehiculo alcanzó {my_type.reference} ",
                    # 'vehicle_id': servicio.vehicle_id.id,
                    "service_id":servicio.id,
                    # "driver_id": record.driver_id.id,  # 
                    "odometer_id" : record.id,
                    # "service_type_id":my_type.id,   
                    "odometer" : self.value,
                }
            )
        else: #No crear servicio #Actualizar con nuevo odometro
            return last_maintenance.write(
                {
                    "odometer_id" : record.id, 
                    "odometer" : self.value,
                }
            )
    
    
    @api.model
    def create(self, vals):
        record = super(InheritedFleetVehicleOdometer, self).create(vals)
        # record.odometer_service_procedure(record)
        record.maintenance_service_procedure(record)
        print("Después de impresión!")
        return record

    def maintenance_service_procedure(self, record):
        print("\n *********************************************** \n")
        print("\n **** def maintenance_service_procedure(self, record): **** \n")
        print("\n *********************************************** \n")

        
        order = "create_date DESC"
        aviso_km = 10
        #Extract services types
        all_types = self.env['fleet.service.type'].search([('category', '=', 'service')])
        for my_type in all_types:
            if my_type.reference > 0:
                total_len = self.env['fleet.vehicle.log.maintenance'].search_count([('vehicle_id', '=', self.vehicle_id.id),('service_type_id', '=', my_type.id)])
                if total_len == 0: #No existe registro de mantenimiento
                    maintenance = self.create_maintenance(my_type=my_type, record=record) #solo mantenimiento con servicio realizado para comenzar
                    # self.send_service_mail_notification(created=True, updated=False, service_type = my_type)
                    # self.create_activity_notification(created=True, updated=False, service_name=my_type.name) #activity

                else:
                    last_maintenance = self.env['fleet.vehicle.log.maintenance'].search([('vehicle_id', '=', self.vehicle_id.id),('service_type_id', '=', my_type.id)], order=order)
                    #tenga un servicio vinculado
                    print(last_maintenance)
                    if last_maintenance:
                        print("Contiene data el último mantenimiento?")
                        for field_name, field in last_maintenance.fields_get().items():
                            if field_name in self:
                                print(f"Campo: {field_name}, Valor: {self[field_name]}")
                        print("\n ************************************* \n")
                        # print(last_maintenance.service_id)
                        # print(last_maintenance.service_id.service_type_id)
                        if(my_type == last_maintenance.service_id.service_type_id):#COMPARAR TIPOS
                            last_maintenance_to_update=last_maintenance
                            print("ULTIMO MANTENIMIENTO CONTIENE (Servicios):", last_maintenance.service_id)
                            last_maintenance = last_maintenance.service_id.sorted(key=lambda r: r.create_date, reverse=True)[0]
                            print("\n ************************************* \n")

                            # next_minus_estimate = last_maintenance_to_update.kms_next_estimate - aviso_km
                            next_minus_estimate = last_maintenance_to_update.set_kms - aviso_km

                            print("Al asignar para ver cual es el record", last_maintenance) #Servicio
                            calculate = next_minus_estimate - record.value 

                            result = (record.value - last_maintenance.odometer_id.value) 
                            print("\n ************************************* \n")
                            print("Resultado del calculo", result)
                            print("Resultado del calculo, menos Tope", calculate)

                            # Tope 
                            # replace result result!
                            if last_maintenance.state == 'done':
                                if calculate > 0:  #aviso_km means kilometer before reach the End (10kms).  #solo actualizar mantenimiento, no crear servicio
                                    maintenance = self.update_service_maintenance(my_type=my_type, last_maintenance=last_maintenance_to_update, record=record, state="done", update=False)
                                    # self.send_service_mail_notification(created=False, updated=True, service_type = my_type)
                                    # self.create_activity_notification(created=False, updated=True, service_name=my_type.name)
                                elif calculate <= 0 and calculate > -10: #actualizar manteniemiento creando servicios nuevos
                                    maintenance = self.update_service_maintenance(my_type=my_type, last_maintenance=last_maintenance_to_update, record=record, state="new", update=True)
                                    self.send_service_mail_notification(created=True, updated=False, service_type = my_type)
                                    self.create_activity_notification(created=True, updated=False, service_name=my_type.name) 
                                else: #sobrepaso el standard y no realizo el mantenieminto #actualizar manteniemiento creando servicios nuevos
                                    maintenance = self.update_service_maintenance(my_type=my_type, last_maintenance=last_maintenance_to_update, record=record, state="cancelled", update=True)
                                    self.send_service_mail_notification(created=True, updated=False, service_type = my_type)
                                    self.create_activity_notification(created=True, updated=False, service_name=my_type.name)
                            elif last_maintenance.state in ['running']:# Service
                                if calculate > 0:  #aviso_km means kilometer before reach the End (10kms).  #solo actualizar mantenimiento, no crear servicio
                                    print("\n NO DEBERÍA suceder este escenario! ")
                                elif calculate <= 0 and calculate > -10: #actualizar manteniemiento creando servicios nuevos
                                    maintenance = self.update_service_maintenance(my_type=my_type, last_maintenance=last_maintenance_to_update, record=record, state="new", update=True)
                                else: #sobrepaso el standard y no realizo el mantenieminto #actualizar manteniemiento creando servicios nuevos
                                    maintenance = self.update_service_maintenance(my_type=my_type, last_maintenance=last_maintenance_to_update, record=record, state="cancelled", update=True)
                                    self.send_service_mail_notification(created=False, updated=True, service_type = my_type)
                                    print('FALTAN KILOMETROS:',(my_type.reference - (self.value - last_maintenance.odometer)))
                            elif last_maintenance.state in ['cancelled']:# Service
                                maintenance = self.update_service_maintenance(my_type=my_type, last_maintenance=last_maintenance_to_update, record=record, state="cancelled", update=True)
                                self.send_service_mail_notification(created=False, updated=True, service_type = my_type)
                                self.create_activity_notification(created=False, updated=True, service_name=my_type.name)
                                print('FALTAN KILOMETROS:',(my_type.reference - (self.value - last_maintenance.odometer)))
                            else:# State  = "New"  
                                if calculate > 0:  #aviso_km means kilometer before reach the End (10kms).  #solo actualizar mantenimiento, no crear servicio
                                    print("\n NO DEBERÍA suceder este escenario! ")
                                elif calculate <= 0 and calculate > -10: #actualizar manteniemiento creando servicios nuevos
                                    maintenance = self.update_service_maintenance(my_type=my_type, last_maintenance=last_maintenance_to_update, record=record, state="new", update=True)
                                else: #sobrepaso el standard y no realizo el mantenieminto #actualizar manteniemiento creando servicios nuevos
                                    maintenance = self.update_service_maintenance(my_type=my_type, last_maintenance=last_maintenance_to_update, record=record, state="cancelled", update=True)
                                    self.send_service_mail_notification(created=False, updated=True, service_type = my_type)

        return True



    def message_post_after_service_maintenance(self, record, new_message, message_values):
        '''Send message when the User use the car without execute maintenance or When we add new Service '''
        odoobot = self.env.ref('base.partner_root')
        if not record:
            kms = float(record.kms_recorridos)
            if kms < 0:
                record.message_post(body=_('Warning! The service is not executed, it was not updated. Vehicle is over the limits! KMS %s' % (kms)),
                                message_type='comment',
                                subtype_xmlid='mail.mt_note',
                                author_id=odoobot.id)
                return True
            if kms > 0 and  kms < 100:
                record.message_post(body=_('Maintenance already left %s to the next Maintenence' % (kms)),
                                message_type='comment',
                                subtype_xmlid='mail.mt_note',
                                author_id=odoobot.id)
                return True
        return True

    def send_service_mail_notification(self, created, updated, service_type):
        vehicle_name = self.vehicle_id.name
        odometer_value = self.value
        service_name = service_type.name

        if created:
            subject = _("New Service Maintenance for %s" % vehicle_name)
            body = _("Una nueva lectura de %s fue registrada para el vechiculo %s, for instance we need to execute the maintenance %s" % (odometer_value, vehicle_name, service_name))
            
        if updated:
            subject = _("Remind to execute Service Maintenance for %s" % vehicle_name)
            body = _("Una nueva lectura de %s fue registrada para el vechiculo %s, for instance we need to execute the last maintenance %s" % (odometer_value, vehicle_name, service_name))
            
        mail_values = {
            'subject': subject,
            'body_html': body,
            'email_to': 'programador@reserma.com' #replace with the actual mail    
        }
        mail = self.env['mail.mail'].create(mail_values)
        mail.send()
        
        return True
    
    def create_activity_notification(self, created, updated, service_name):
        '''CREATE ACTIVITY'''
        my_vehicle=self.env["fleet.vehicle"].search([('id', '=', self.vehicle_id.id)])
        if created:
            my_vehicle.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=my_vehicle.manager_id.id or self.env.user.id,
            note=_('Service maintenance %s to do, %s ') % (service_name ,my_vehicle.driver_id.name))
        # if updated:
        #     my_vehicle.activity_schedule(
        #     'mail.mail_activity_data_todo',
        #     user_id=my_vehicle.manager_id.id or self.env.user.id,
        #     note=_('Service maintenance %s to do for %s') % (service_name ,my_vehicle.driver_id.name))
        

    
class FleetVehicleMaintenance(models.Model):
    _name = "fleet.vehicle.maintenance"
    _description = "Future and Past Manintenance"

    

    date = fields.Date(help='Date when the maintenance/service has been created', default=fields.Date.context_today)
    # odometros_ids = fields.One2many(comodel_name='fleet.vehicle.odometer',
    #                                inverse_name='vehicle_id',
    #                                string="Odometros")# if you know the vehicle, you know the odometers (cantidad, fecha)
    
    services_ids = fields.One2many(comodel_name='fleet.vehicle.log.services',
                                   inverse_name='vehicle_id',
                                   string="Servicios")# if you know the vehicle, you know the services (estado, tipo) #if you know the type you know the reference
    

    # kms_recorridos = fields.Char(string="KM", compute='_compute_km_maintenance', store=True,
    #                              help="Verde, indica los Kilometros que faltan para un futuro mantenimiento. Rojo, indica los Kilometros recorridos sin haber realizado el mantenimiento.")

    odometro = fields.One2many
    kms_recorridos = fields.Char(string="KM", 
                                 help="Verde, indica los Kilometros que faltan para un futuro mantenimiento. Rojo, indica los Kilometros recorridos sin haber realizado el mantenimiento.")

    # @api.depends("services_ids.odometer")
    # def _compute_km_maintenance(self):

    #     'dependiendo del valor del odometro y de cuando el servicio se genero (si existe) calcular kms'
    #     print("computando")
    #     self.kms_recorridos = 190

class InheritedFleetVehicleLogServices(models.Model):
    _inherit = "fleet.vehicle.log.services"

    # def action_set_done(self):
    #     '''isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface'''
    #     for record in self:
    #         if not record.amount > 0.0:
    #             raise exceptions.UserError('Services cannot be done without cost. Set cost and try again!')
    #     # isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface
    #     return True
    
    def write(self, vals):
        print("vals", vals)
        myrecord = super(InheritedFleetVehicleLogServices, self).write(vals)
        print("\n EL ESTADO DEL REGISTRO: usando self", self.state)

        print("Contiene data el último mantenimiento?")
        for field_name, field in self.fields_get().items():
            if field_name in self:
                print(f"Campo: {field_name}, Valor: {self[field_name]}")



        for record in self:


            Odometer = self.env["fleet.vehicle.odometer"]
            last_maintenance = self.env['fleet.vehicle.log.maintenance'].search([('service_id', '=', record.id)],limit=1,order='create_date desc')    
            print("last main", last_maintenance)                 
            vehicle_odometer = Odometer.search([('vehicle_id', '=', last_maintenance.vehicle_id.id)], limit=1, order='value desc')
            print("EL ESTADO DEL REGISTRO:  usand record ", record.state)
            print("last_maintenance.complete", last_maintenance.complete)
            if not last_maintenance.complete and record.state == "done":
                last_maintenance.complete = False
                last_maintenance.set_kms = vehicle_odometer.value + last_maintenance.service_id.service_type_id.reference
                print("Contrario a no hacer nada", last_maintenance.set_kms)
                
            else:
                print("No hacer nada")
                print("No hacer nada", last_maintenance.set_kms)
            #vehicle_odometer.update_service_maintenance(my_type=maintenance.service_type_id, last_maintenance=maintenance, maintenance=vehicle_odometer, state='done', update=True)
        # record.odometer_service_procedure(record)
        # record.maintenance_service_procedure(record)
        # print("Después de impresión!")
        return myrecord    

    

class InheritedFleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    def compute_next_year_date(self, strdate):
        oneyear = relativedelta(years=1)
        start_date = fields.Date.from_string(strdate)
        return fields.Date.to_string(start_date + oneyear)

    log_maintenance = fields.One2many('fleet.vehicle.log.maintenance', 'vehicle_id', 'Maintenances Logs') 
    maintenance_count = fields.Integer(compute="_compute_count_maintenance", string='Maintenance')     
    log_images = fields.One2many('fleet.vehicle.log.images', 'vehicle_id', 'Images Logs') 
    #log matriculation
    log_matriculation = fields.One2many('fleet.vehicle.log.matriculation', 'vehicle_id', 'Matriculas Logs') 
    matriculation_count = fields.Integer(compute="_compute_count_matriculation", string='Matriculation')
    last_image_front = fields.Binary(compute='_get_last_front_image',inverse='_set_front_image', string='Frontal',
        help='Front side image of the vehicle at the moment of this log')
    last_image_back = fields.Binary(string='Posterior',
        help='Back side  image of the vehicle at the moment of this log')
    last_image_right_side = fields.Binary(string='Lado Derecho',
        help='right (copilot) side image of the vehicle at the moment of this log')
    last_image_lefth_side = fields.Binary(string='Lado Izquierdo',
        help='lefth (pilot) side image of the vehicle at the moment of this log')
    last_image_fuel_level = fields.Binary(string='Nivel de Combustible',
        help='Fuel image level of the vehicle at the moment of this log')
    
    
    #signature
    signature = fields.Image('Signature', help='Signature', copy=False, attachment=True)
    is_signed = fields.Boolean('Is Signed', compute="_compute_is_signed")
    is_locked = fields.Boolean(default=True, help='When the chages is not done this allows changing the '
                               'initial fields. When the changes is done this allows '
                               'changing the done fields.')
    #renovación del registro del vehículo
    renovation_date = fields.Date(
        'Matriculation Date', 
        required=True,
        default = fields.date.today(),
        help='Date when the vehicle has been renovated')
    expiration_date = fields.Date(
            'Placa Expiration Date', 
            # default=lambda self:
            # self.compute_next_year_date(self.env.vehicle),
            default=lambda self:self.compute_next_year_date(fields.Date.context_today(self)),
            compute='_compute_next_year_date',
            help='Date when the coverage of the placa expirates (by default, one year after begin date)')

    @api.depends('renovation_date')
    def _compute_next_year_date(self):
        for record in self:
            oneyear = relativedelta(years=1)
            start_date = fields.Date.from_string(record.renovation_date)
            record.expiration_date = fields.Date.to_string(start_date + oneyear)      

    @api.depends('signature')
    def _compute_is_signed(self):
        for vehicle in self:
            vehicle.is_signed = vehicle.signature

    def write(self, vals):
        # print("My vals", vals)
        res = super(InheritedFleetVehicle, self).write(vals)
        if vals.get('signature'):
            for vehicle in self:
                vehicle._attach_sign()
        #si cambia deberia actualizar el último proceso de matricula
        #         if vals.get('renovation_date'):
        # create matriculation
        #     matriculate = self.env["fleet.vehicle.log.matriculation"].create(
        #         {
        #         "vehicle_id": res.id,
        #         "renovation_date": res.renovation_date,
        #         "expiration_date":res.expiration_date
        #         "driver_id": record.driver_id.id, 
        #         }
        #     )

        return res

    def _attach_sign(self):
        """ Render the changes report in pdf and attach it to the picking in `self`. """
        self.ensure_one()
        # report = self.env['ir.actions.report']._render_qweb_pdf("stock.action_report_delivery", self.id) #modificando el reporte
        report = self.env['ir.actions.report']._render_qweb_pdf("fleet_maintenance.action_report_images", self.id) #modificando el reporte
        
        filename = "%s_signed_car_changes" % self.name
        if self.driver_id:
            message = _('Vehicle verification signed by %s') % (self.driver_id.name)
        else:
            message = _('vehicle verification')
        self.message_post(
            attachments=[('%s.pdf' % filename, report[0])],
            body=message,
        )
        return True

    @api.model
    def create(self, vals):
        print("\n *********************************************** \n")
        print("\n **** def create(self, vals):     [Class SERVICES ] **** \n")
        print("\n *********************************************** \n")
        print(vals)
        record = super(InheritedFleetVehicle, self).create(vals)
        print("ADD CHATTER!!")
        # record.enviar_mi_nueva_notificacion_chatter()
        # FleetMatriculation = self.env["fleet.vehicle.log.matriculation"]
        # FleetMatriculation.create_matriculation(record)

        #si cambia deberia actualizar el último proceso de matricula
        if vals.get('renovation_date'):
        #create matriculation
            matriculate = self.env["fleet.vehicle.log.matriculation"].create(
                {
                "vehicle_id": record.id,
                # "renovation_date": record.renovation_date,
                "expiration_date":record.expiration_date,
                # "driver_id": record.driver_id.id, 
                }
            )

        return record
    
    def enviar_mi_nueva_notificacion_chatter(self):
        try:
            subject = _("Nueva lectura de %s, el servicio de %s " % (self.vehicle_id.name, self.service_type.name, ))
            body = _("Una nueva lectura de %s fue registrada para el vechiculo %s y genero un servicio de %s" % (self.odometer, self.vehicle_id.name, self.service_type.name, ))
            self.message_post(subject=subject, body=body, message_type='notification') #'fleet.vehicle.odometer' object has no attribute 'message_post'
        except AttributeError:
            print("No driver in vehicle!")
        
        return True
    
    def action_set_maintenance(self):
        print("\n *********************************************** \n")
        print("\n **** action_set_maintenance(self):     [Class VEHICLE ] **** \n")
        print("\n *********************************************** \n")

        Odometer = self.env["fleet.vehicle.odometer"]
        ServiceType = self.env["fleet.service.type"]
        for record in self:
            vehicle_odometer = Odometer.search([('vehicle_id', '=', record.id)], limit=1, order='value desc')
            total_len = ServiceType.search_count([('reference', '>', 0)])
            print("record.odometer", vehicle_odometer.value)                
            print("total len", total_len)
            if vehicle_odometer:#verificar que exista un odometro vinculado!
                if not total_len == 0:
                    if vehicle_odometer.value > 0:
                        print("Odometer id", vehicle_odometer.id)
                        vehicle_odometer.maintenance_service_procedure(vehicle_odometer)
                    else:
                        Odometer.create({
                                'value': 0.0,
                                'vehicle_id' :record.id,
                        })
                else:
                    raise exceptions.UserError("Níngun servicio tiene referencia de Kilometrajes añadida!")
            else:
                if not total_len == 0:
                    Odometer.create({
                            'value': 0.0,
                            'vehicle_id' :record.id,
                    })
                else:
                    raise exceptions.UserError("Níngun servicio tiene referencia de Kilometrajes añadida!")

        return True

    
    def _compute_count_maintenance(self):
        print("\n *********************************************** \n")
        print("\n **** _compute_count_maintenance(self):     [Class VEHICLE ] **** \n")
        print("\n *********************************************** \n")


        Maintenance = self.env['fleet.vehicle.log.maintenance']
        maintenance_data = Maintenance.read_group([('vehicle_id', 'in', self.ids)], ['vehicle_id'], ['vehicle_id'])
        # print("MAINTENANCE DATA", maintenance_data)
        mapped_maintenance_data = defaultdict(lambda: 0)

        for maintenance_data in maintenance_data:
            mapped_maintenance_data[maintenance_data['vehicle_id'][0]] = maintenance_data['vehicle_id_count']
            # print("mapped_maintenance_data[maintenance_data['vehicle_id'][0]]", mapped_maintenance_data[maintenance_data['vehicle_id'][0]])
        
        for vehicle in self:
            # print("EL ID DEL VEHICULO", vehicle.id, "Vehicle active", vehicle.active)
            if vehicle.active:
                vehicle.maintenance_count = mapped_maintenance_data[vehicle.id]
            else:
                vehicle.maintenance_count = 0

    def _compute_count_matriculation(self):
        print("\n *********************************************** \n")
        print("\n **** _compute_count_matriculation(self):     [Class VEHICLE ] **** \n")
        print("\n *********************************************** \n")

        Matriculation = self.env['fleet.vehicle.log.matriculation']
        matriculation_data = Matriculation.read_group([('vehicle_id', 'in', self.ids)], ['vehicle_id'], ['vehicle_id'])
        mapped_matriculation_data = defaultdict(lambda: 0)

        for matriculation_data in matriculation_data:
            mapped_matriculation_data[matriculation_data['vehicle_id'][0]] = matriculation_data['vehicle_id_count']
        
        for vehicle in self:
            if vehicle.active:
                vehicle.matriculation_count = mapped_matriculation_data[vehicle.id]
            else:
                vehicle.matriculation_count = 0

    def _get_last_front_image(self):
        FleetVehicalImage = self.env['fleet.vehicle.log.images']
        for record in self:
            vehicle_image = FleetVehicalImage.search([('vehicle_id', '=', record.id)], limit=1, order='create_date desc')
            if vehicle_image:
                record.last_image_front = vehicle_image.car_image_front
                record.last_image_back =  vehicle_image.car_image_back
                record.last_image_right_side = vehicle_image.car_image_izq
                record.last_image_lefth_side = vehicle_image.car_image_der
                record.last_image_fuel_level = vehicle_image.car_image_fuel
            else:
                record.last_image_front = None
                record.last_image_back = None
                record.last_image_right_side = None
                record.last_image_lefth_side = None
                record.last_image_fuel_level = None

    def _set_front_image(self):
        for record in self:
            if record.last_image_front:
                date = fields.Date.context_today(record)
                data = {
                    'car_image_front': record.last_image_front,
                    'car_image_back':record.last_image_back,
                    'car_image_izq':record.last_image_right_side,
                    'car_image_der':record.last_image_lefth_side,
                    'car_image_fuel': record.last_image_fuel_level,

                    'date': date,
                    'vehicle_id': record.id}
                self.env['fleet.vehicle.log.images'].create(data)

class InheritFleetLogImage(models.Model):

    _name= "fleet.vehicle.log.images"
    _description = "Different Car Views"
    _order = 'date desc'

    date = fields.Date(default=fields.Date.context_today)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True)
    user_id = fields.Many2one('res.users', 'Fleet Responsible', default=lambda self: self.env.user, index=True)#no manager
    car_image_front = fields.Binary(string='Imagen de Frente/Delantera')
    car_image_back = fields.Binary(string='Imagen Posterior/Trasera')
    car_image_izq = fields.Binary(string="Imagen Lado Izquierdo/Conductor")
    car_image_der = fields.Binary(string='Imagen Lado Derecho/Copiloto')
    car_image_fuel = fields.Binary(string='Nivel de Combustible')

class InheritedFleetLogMatriculation(models.Model):

    _name = 'fleet.vehicle.log.matriculation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Vehicle Matriculation'
    _order = 'state_matriculation desc'

    def compute_next_year_date(self, strdate):
        oneyear = relativedelta(years=1)
        start_date = fields.Date.from_string(strdate)
        return fields.Date.to_string(start_date + oneyear)

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo', required=True)
    # default=lambda self: self._get_current_vehicle()
    date = fields.Date(help='Date when the cost has been executed', string="Realizado el día")
    amount = fields.Monetary('Cost')
    # currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    currency_id = fields.Many2one('res.currency', "Currency")

    user_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user, index=True)
    days_left = fields.Integer(compute='_compute_days_left', string='Fecha de aviso')
    expires_today = fields.Boolean(compute='_compute_days_left')
    state_matriculation = fields.Selection(
        [
         ('open', 'In Progress'),
         ('expired', 'Expired'),
         ('closed', 'Closed')
        ], 'Status', default='open',
        help='Choose whether the renovation is still valid or not',
        # tracking=True,
        copy=False)
    expiration_date = fields.Date(
            'Expiración de la Placa', 
            # default=lambda self:
            # self.compute_next_year_date(self.env.vehicle),
            # compute='_compute_next_year_date',
            help='Date when the coverage of the placa expirates (by default, one year after begin date)')
    notes = fields.Html('Terms and Conditions', copy=False)
    # cost_generated = fields.Monetary('Recurring Cost', tracking=True)
    cost_frequency = fields.Selection([
        ('no', 'No'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')
        ], 'Recurring Cost Frequency', default='yearly', required=True)
    
    @api.depends('expiration_date', 'state_matriculation', 'vehicle_id' )
    def _compute_days_left(self):
        """return a dict with as value for each matriculate an integer
        if matriculate is in an open state and is overdue, return 0
        if matriculate is in a closed state, return -1
        otherwise return the number of days before the matriculate expires
        """
        print("Compute days MATRICULATION!")

        today = fields.Date.from_string(fields.Date.today())
        for record in self:
            my_vehicle=self.env["fleet.vehicle"].search([('id', '=', record.vehicle_id.id)])
            if my_vehicle.expiration_date and record.state_matriculation in ['open', 'expired']:
                record.expiration_date = my_vehicle.expiration_date
                print("my_vehicle.expiration_date", my_vehicle.expiration_date)
                renew_date = fields.Date.from_string(my_vehicle.expiration_date)
                print("Que es renew date", renew_date)
                print("Today", today)
                diff_time = (renew_date - today).days
                print("time diff", diff_time)
                record.days_left = diff_time if diff_time > 0 else diff_time
                record.state_matriculation = "expired" if diff_time < 0 else "open"
                record.expires_today = diff_time == 0
            else:
                record.days_left = -1
                record.expires_today = False

    def write(self, vals):
        print(vals)
        self.ensure_one()
        if len(vals)<=1 and vals.get('state_matriculation'):#si solo quieres cambiar el estado pero no añades el costo
            if (vals['state_matriculation'] == "closed"):
                if (float_is_zero(self.amount, 2)):
                    raise exceptions.UserError('Matriculation cannot be done without cost. Set cost and try again!')
        else:
            if vals.get('amount') and vals.get('state_matriculation'):
                if (vals['state_matriculation'] == "closed"):
                    if not(float_is_zero(vals['amount'], 2)):
                        vals['date']=fields.date.today()
                else:
                    raise exceptions.UserError('Matriculation cannot be done without cost. Set cost and try again!')
            print("Antes de actualizar! \n", vals)
        record = super(InheritedFleetLogMatriculation, self).write(vals) #if done return true
        #si cambia deberia actualizar el último proceso de matricula
        # #create matriculation
        #     mycost = vals.get('date')
        if (vals.get('date')):
            Vehicle = self.env["fleet.vehicle"]
            for record in self:
                if record.vehicle_id:
                    myvehicle=Vehicle.search([('id','=', record.vehicle_id.id)])
                    myvehicle.write(
                        {
                        "renovation_date": vals["date"],
                        }
                    )
        return record


class FleetVehicleLogMaintenance(models.Model):
    _name = 'fleet.vehicle.log.maintenance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Maintenance for vehicles'    

    # def compute_next_maintenance(self, kms, reference):
    #     return kms + reference
    
    description = fields.Char('Description')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True)
    user_id = fields.Many2one('res.users', 'Fleet Responsible', default=lambda self: self.env.user, index=True)#no manager
    service_id = fields.Many2one('fleet.vehicle.log.services', 'Service', required=True)
    driver_id = fields.Many2one(related='vehicle_id.driver_id', string="Driver", readonly=False, default=lambda self: self.env.user)
    service_type_id = fields.Many2one('fleet.vehicle.log.services', related='service_id.service_type_id')
    service_state= fields.Selection(related='service_id.state')
    odometer_id = fields.Many2one('fleet.vehicle.log.services', related='service_id.odometer_id',
                                 help="Verde, indica los Kilometros que faltan para un futuro mantenimiento. Rojo, indica los Kilometros recorridos sin haber realizado el mantenimiento.")
    kms_next_estimate = fields.Float(
        'Próximo Mantenimiento', compute ='_compute_next_maintenance',
        help='kms when the coverage of the maintenance expirates (por defecto debe ser type.reference + service_id.odometer_id.value)')
    set_kms= fields.Float(
        'Próximo Mantenimiento SETEADO')
    complete = fields.Boolean(default=False, string="Completado")
    kms_left = fields.Integer(compute='_compute_kms_left', string='KMS')
    do_today = fields.Boolean(compute='_compute_kms_left')
    state_maintenance = fields.Selection(
        [('futur', 'Incoming'),
         ('open', 'In Progress'),
         ('expired', 'Expired'),
         ('closed', 'Closed')
        ], 'Status', default='open', readonly=True,
        help='Choose whether the contract is still valid or not',
        tracking=True,
        copy=False, compute='_compute_maintenance_state' )
    
    odometer = fields.Float(compute='_get_odometer', string='Last Odometer',
        help='Odometer measure of the vehicle at the moment of this log')
    

    def _get_odometer(self):
        print("\n *********************************************** \n")
        print("\n **** def _get_odometer(self): Class [maintenance] **** \n")
        print("\n *********************************************** \n")

        FleetVehicalOdometer = self.env['fleet.vehicle.odometer']
        for record in self:
            print("\n Entra en el for de _get_odometer")
            vehicle_odometer = FleetVehicalOdometer.search([('vehicle_id', '=', record.vehicle_id.id)], limit=1, order='value desc')
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

    @api.depends('kms_next_estimate', 'state_maintenance')
    def _compute_kms_left(self):
        """return a dict with as value for each maintenance an integer
        if maintenance is in an open state and is overdue, return 0
        if maintenance is in a closed state, return -1
        otherwise return the number of days before the maintenance expires
        """
        print("\n *********************************************** \n")
        print("\n **** def _compute_kms_left(self):  Class [maintenance]**** \n")
        print("\n *********************************************** \n")


        print("Evaluar la necesidad de manejar cuando es negativo!")
        for record in self:
            for field_name, field in record.fields_get().items():
                if field_name in ["state_maintenance", "odometer", "service_state", "set_kms"]:
                    if field_name in record:
                        try:
                            print(f"Campo: {field_name}, Valor: {record[field_name]}")
                        except ValueError:
                            print("ValueError: Wrong value for fleet.vehicle.log.maintenance.service_type_id: fleet.service.type(47,)")
                        else:
                            print("Continue!")


        today = fields.Date.from_string(fields.Date.today())
        for record in self:
            print("\n Entra en el for de _compute_kms_left")
            renew_kms = record.set_kms
            # print("\n3. record.kms_next_estimate", record.kms_next_estimate)

            # if record.state_maintenance == "expired":
            #     diff_kms = (renew_kms - record.odometer)
            #     print("DIFF KMS 1", diff_kms, "diff_kms = (renew_kms - record.odometer)")
            #     record.kms_left = diff_kms if diff_kms > 0 else diff_kms
            #     record.do_today = diff_kms <= 0
            # elif record.state_maintenance == "futur":    
            #     diff_kms = (renew_kms - record.odometer)
            #     print("DIFF KMS 2", diff_kms)        
            #     record.kms_left = diff_kms if diff_kms > 0 else diff_kms * -1
            # else:
            #     diff_kms = (renew_kms - record.odometer)
            #     print("DIFF KMS 3", diff_kms)
            diff_kms = (renew_kms - record.odometer)
            record.kms_left = diff_kms if diff_kms > 0 else diff_kms
            record.do_today = diff_kms <= 0

    
    @api.depends('service_state','odometer_id', 'service_type_id')
    def _compute_next_maintenance(self):
        print("\n *********************************************** \n")
        print("\n **** def _compute_next_maintenance(self): Class [maintenance]**** \n")
        print("\n *********************************************** \n")

        FleetVehicleMaintenance = self.env['fleet.vehicle.log.maintenance']
        
        for record in self:
            print("\n Entra en el for de _compute_next_maintenance")
            last_main = FleetVehicleMaintenance.search([('service_id', '=', record.service_id.id)])
            # self.verify_output_values(last_main)
            print(record.kms_next_estimate,"vs last estimate", last_main.kms_next_estimate)

            if record.service_state == "done":
                record.kms_next_estimate = (record.service_id.odometer_id.value + record.service_id.service_type_id.reference)
                print(record.kms_next_estimate,"vs last estimate", last_main.kms_next_estimate)
            elif record.service_state == "new":#sin realizar
                record.kms_next_estimate = (record.service_id.odometer_id.value - record.service_id.service_type_id.reference)
                # print(record.kms_next_estimate,"vs last estimate", last_main.kms_next_estimate)
            else:
                record.kms_next_estimate= (record.service_id.odometer_id.value + record.service_id.service_type_id.reference)

            

    @api.depends('service_state')
    def _compute_maintenance_state(self):
        print("\n *********************************************** \n")
        print("\n **** def _compute_maintenance_state(self): Class [maintenance]**** \n")
        print("\n *********************************************** \n")



        
        for maintenance in self:
            print("\n Entra en el for de _compute_maintenance_state")
            print("\n SERVICE DESCRIPTION:", maintenance.description)
            if maintenance.service_state:
                if maintenance.service_state == "new":
                    maintenance.state_maintenance = "open"
                elif maintenance.service_state == "done":
                    maintenance.state_maintenance = "futur"
                    # if maintenance.complete 
                    print("\n Here is where the data is chnaged!!")
                elif maintenance.service_state == "cancelled":
                    maintenance.state_maintenance = "expired"
                else: # closed
                    maintenance.state_maintenance = "expired"


class InheritedFleetServiceType(models.Model):
    _inherit = 'fleet.service.type'

    reference = fields.Integer(string="Referencia (KM)", help="Referencia de Kilometrajes para próximos manteniemientos")

    _sql_constraints = [
        ('inherited_fleet_service_type_check_reference', 'CHECK(reference > 0 AND reference < 30000)', 'The reference for maintenance must be POSITIVE but Lower Than 30000')
    ]
        
