from odoo import fields, models, api, Command, _, exceptions
from collections import defaultdict

# class InheritedFleetVehicle(models.Model):
#     _inherit = 'fleet.vehicle'

#     def _compute_vehicle_log_name(self):
#         print("SE AÑADE UN NUEVO ODOMETRO")
#         return super(InheritedFleetVehicle, self)._compute_vehicle_log_name()
    
class InheritedFleetVehicleOdometer(models.Model):
    # _inherit = ['fleet.vehicle.odometer', 'mail.thread','mail.activity.mixin']
    _inherit = ['fleet.vehicle.odometer']
    
    def preparar_servicio(self, val):
        servicio_vals = {
            # 'description':f" Mantenimiento de {val}",
            # 'service_type_id':val,
            # 'date': 'out_invoice',
            # 'vehicle_id': self.buyer_id.id,
            # 'purchaser_i': val,  # company comes from the journal
            # 'odometer' : val
        }

        return servicio_vals

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
        print("\n *********************************************** \n")
        print("\n **** def create_maintenance(self, my_type, record):   CLASS [ODOMETER] **** \n")
        print("\n *********************************************** \n")
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
                                elif calculate <= 0 and calculate >= -10: #actualizar manteniemiento creando servicios nuevos
                                    maintenance = self.update_service_maintenance(my_type=my_type, last_maintenance=last_maintenance_to_update, record=record, state="new", update=True)
                                    self.send_service_mail_notification(created=True, updated=False, service_type = my_type)
                                    self.create_activity_notification(created=True, updated=False, service_name=my_type.name) 
                                else: #sobrepaso el standard y no realizo el mantenieminto #actualizar manteniemiento creando servicios nuevos
                                    maintenance = self.update_service_maintenance(my_type=my_type, last_maintenance=last_maintenance_to_update, record=record, state="cancelled", update=True)
                                    self.send_service_mail_notification(created=True, updated=False, service_type = my_type)
                                    self.create_activity_notification(created=True, updated=False, service_name=my_type.name)
                            elif last_maintenance.state in ['running']:# Service
                                if (result >= my_type.reference):
                                    print("NO SE CREA MANTENIMIENTO PERO SE ACTUALIZA (solo) EL VALOR DEL KILOMETRAJE Y SE ENVIA NOTIFICACIÓN O MENSAJE!")
                                    self.send_service_mail_notification(created=False, updated=True, service_type = my_type) #message
                                    # Chatter
                                    self.message_post_after_service_maintenance(record=last_maintenance_to_update, new_message="Warning. Runnig Without Execute Maintenance !", message_values=last_maintenance)
                                else:
                                    # last_maintenance_to_update.write({'kms_recorridos':(my_type.reference - (self.value - last_maintenance.odometer))})
                                    print('FALTAN KILOMETROS:',(my_type.reference - (self.value - last_maintenance.odometer)))
                            elif last_maintenance.state in ['cancelled']:# Service
                                maintenance = self.update_service_maintenance(my_type=my_type, last_maintenance=last_maintenance_to_update, record=record, state="cancelled", update=True)
                                self.send_service_mail_notification(created=False, updated=True, service_type = my_type)
                                self.create_activity_notification(created=False, updated=True, service_name=my_type.name)
                                print('FALTAN KILOMETROS:',(my_type.reference - (self.value - last_maintenance.odometer)))
                            else:# State  = "New"  
                                if calculate > 0:  #aviso_km means kilometer before reach the End (10kms).  #solo actualizar mantenimiento, no crear servicio
                                    print("\n NO DEBERÍA suceder este escenario! ")
                                elif calculate <= 0 and calculate >= -10: #actualizar manteniemiento creando servicios nuevos
                                    maintenance = self.update_service_maintenance(my_type=my_type, last_maintenance=last_maintenance_to_update, record=record, state="new", update=True)
                                else: #sobrepaso el standard y no realizo el mantenieminto #actualizar manteniemiento creando servicios nuevos
                                    maintenance = self.update_service_maintenance(my_type=my_type, last_maintenance=last_maintenance_to_update, record=record, state="cancelled", update=True)
                                    self.send_service_mail_notification(created=False, updated=True, service_type = my_type)

        return True

    
    def odometer_service_procedure(self, record):
        #self.odometer
        # print(res)
        # print(type(res))
        print("Ejecutando después de la creación")            
        #traer los tipos de servicios
        all_types = self.env['fleet.service.type'].search([('category', '=', 'service')])
        print(all_types)
        #EJECUTAR SERVICIO de la lista
        order = "create_date DESC"
        for my_type in all_types:
            #llamar los registros asociados al vehiculo de la base de datos de mantenimientos por fecha y vehiculo segun odometro
            # mantenimientos = self.env['fleet.vehicle.maintenance'].search([('services_ids', '=', self.vehicle_id.id),('services_ids.service_type_id.id', '=', my_type.id)])
            if my_type.id == 47 and my_type.reference > 0: #validar que el registro de typo contenga una referencia de Kilometrajes
                print(f"BUSCANDO LOS VALORES DE LA TABLA PARA VEHÍCULO TAL:  {self.vehicle_id.id}", )
                total_len = self.env['fleet.vehicle.maintenance'].search_count([('services_ids.vehicle_id.id', '=', self.vehicle_id.id),('services_ids.service_type_id.id', '=', my_type.id)])
                print("TOTAL DE REGISTROS, ", total_len)
                
                if total_len == 0: #No existe registro
                    #service lines
                    print("Before, CREATE MAINTENANCE SERVICE, total len 0!")
                    maintenance = self.crear_servicios_manteniento(my_type=my_type, record=record)
                    self.send_service_mail_notification(created=True, updated=False, service_type = my_type)
                    self.create_activity_notification(created=True, updated=False, service_name=my_type.name) #activity
                    #chatter

                else:
                    last_maintenance = self.env['fleet.vehicle.maintenance'].search([('services_ids.vehicle_id.id', '=', self.vehicle_id.id),('services_ids.service_type_id.id', '=', my_type.id)],order=order)
                    print("Contiene data el último mantenimiento?")
                    for field_name, field in last_maintenance.fields_get().items():
                        if field_name in self:
                            print(f"Campo: {field_name}, Valor: {self[field_name]}")
                    
                    print("LAST MAINTENANCE (model)", last_maintenance)
                    last_maintenance_to_update=last_maintenance
                    print("ULTIMO MANTENIMIENTO CONTIENE (Servicios):", last_maintenance.services_ids)
                    # last_maintenance.services_ids.search(order=order, limit=1) #No valid
                    # last_maintenance_services = last_maintenance.search([('service_type_id', '=', my_type.id)]) #extract only required type
                    # services = self.env['fleet.vehicle.log.services'].browse(last_maintenance_services.services_ids) #services only
                    # print(services)
                    # last_maintenance = services.sorted(key=lambda r: r.create_date, reverse=True)[0]
                    last_maintenance = last_maintenance.services_ids.sorted(key=lambda r: r.create_date, reverse=True)[0]
                    print("\n",last_maintenance)
                    print(f"Para el tipo {my_type.name} existen {last_maintenance.description} con id {last_maintenance.id} with last odometer {last_maintenance.odometer}")
                    if (my_type.id == last_maintenance.service_type_id.id and last_maintenance.state != "done" and my_type.reference > 0):
                        #crear mantenimiento
                        if last_maintenance.odometer == 0:
                            print("Es 0? Si odometro esta ODOMETRO DE LOS ÚLTIMO",last_maintenance.odometer)

                            break
                        print(f"({self.value} - {last_maintenance.odometer}) >= {my_type.reference}")
                        if ((self.value - last_maintenance.odometer) >= my_type.reference):
                            print("NO SE CREA MANTENIMIENTO PERO SE ACTUALIZA EL VALOR DEL KILOMETRAJE Y SE ENVIA NOTIFICACIÓN O MENSAJE!")
                            last_maintenance_to_update.write({'kms_recorridos':((self.value - last_maintenance.odometer)-my_type.reference)*-1})
                            self.send_service_mail_notification(created=False, updated=True, service_type = my_type) #message

                            #chatter
                            self.message_post_after_service_maintenance(record=last_maintenance_to_update, new_message="Warning. Runnig Without Execute Maintenance !", message_values=last_maintenance)

                            break #se ejecutara el bucle y no queremos eso
                        else:
                            # last_maintenance_to_update.write({'kms_recorridos':(my_type.reference - (self.value - last_maintenance.odometer))})
                            print("FALTAN KILOMETROS.",(my_type.reference - (self.value - last_maintenance.odometer)))
                        # print(service)
                    elif last_maintenance.state == "done" and last_maintenance.vehicle_id.id == self.vehicle_id.id:
                        print(f"({self.value} - {last_maintenance.odometer}) >= {my_type.reference}")
                        if ((self.value - last_maintenance.odometer) >= my_type.reference):
                            print("Actualizando mantenimiento a los ", last_maintenance.odometer)
                            #service not create #no se ha hecho
                            print(self.vehicle_id, "id del vehículo", self.vehicle_id.id)
                            maintenance = self.actualizar_servicios_manteniento(my_type=my_type, last_maintenance=last_maintenance_to_update)
                            
                            # self.actualizar_servicios_manteniento(created=False, updated=True, service_type = my_type)
                            self.create_activity_notification(created=True, updated=False, service_name=my_type.name) #activity

                            #chatter
                            self.message_post_after_service_maintenance(record=maintenance, new_message="Create a new service to accomplish Maintenance!", message_values=last_maintenance)
                            
                            
                            # print(maintenance)
                            break #se ejecutara el bucle y no queremos eso
                        else:
                            k=last_maintenance_to_update.write({'kms_recorridos':(my_type.reference - (self.value - last_maintenance.odometer))})
                            print("Valor actualizado:",k) #this value cannot be True, is not an isntance
                            print("FALTAN KILOMETROS.",(my_type.reference - (self.value - last_maintenance.odometer)))
                            
                            #chatter
                            self.message_post_after_service_maintenance(record=k, new_message="Warning. Runnig Without Execute Maintenance !", message_values=last_maintenance)

                    elif last_maintenance.state == "done" and last_maintenance.vehicle != self.vehicle_id:
                        print("CAMBIO EN LOS DATOS, NO ES EL MISMO AUTO DE ")
                    else:
                        print("NO SE GENERO PORQUE AÚN NO SE HA EFECTUADO EL MANTENIMIENTO.")
                        # Generar actividad!

                    #if no exist then -->    
                    #create service obtaint id
                    #create manintenance obtaint id

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

    def action_set_done(self):
        '''isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface'''
        for record in self:
            if not record.amount > 0.0:
                raise exceptions.UserError('Services cannot be done without cost. Set cost and try again!')
        # isn’t prefixed with an underscore (_). This makes our method a public method, which can be called directly from the Odoo interface
        return True
    

class InheritedFleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    # image_ids = fields.One2many(comodel_name='fleet.vehicle.image',
    #                             inverse_name="",
    #                             string='Imagenes', 
    #                             domain=lambda self: [('state', 'in', ['offer_received', 'offer_accepted', 'sold'])]
    #                             )
    log_maintenance = fields.One2many('fleet.vehicle.log.maintenance', 'vehicle_id', 'Maintenances Logs') 
    maintenance_count = fields.Integer(compute="_compute_count_maintenance", string='Maintenance')     
    log_images = fields.One2many('fleet.vehicle.log.images', 'vehicle_id', 'Images Logs') 
    last_image_front = fields.Binary(compute='_get_last_front_image',inverse='_set_front_image', string='Last Front Image',
        help='Front image of the vehicle at the moment of this log')
    last_image_back = fields.Binary(string='Last back Image',
        help='Back image of the vehicle at the moment of this log')
    last_image_right_side = fields.Binary(string='Last right_side Image',
        help='right_side image of the vehicle at the moment of this log')
    last_image_lefth_side = fields.Binary(string='Last lefth_side Image',
        help='lefth_side image of the vehicle at the moment of this log')
    
    # last_image_back = fields.Binary(compute='_get_last_back_image')
    # last_image_left = fields.Binary(compute='_get_last_left_image')
    # last_image_right = fields.Binary(compute='_get_last_right_image')


    @api.model
    def create(self, vals):
        print("\n *********************************************** \n")
        print("\n **** def create(self, vals):     [Class SERVICES ] **** \n")
        print("\n *********************************************** \n")

        record = super(InheritedFleetVehicle, self).create(vals)
        print("ADD CHATTER!!")
        # record.enviar_mi_nueva_notificacion_chatter()
    
        return record
    
    def enviar_mi_nueva_notificacion_chatter(self):
        try:
            subject = _("Nueva lectura de %s, el servicio de %s " % (self.vehicle_id.name, self.service_type.name, ))
            body = _("Una nueva lectura de %s fue registrada para el vechiculo %s y genero un servicio de %s" % (self.odometer, self.vehicle_id.name, self.service_type.name, ))
            self.message_post(subject=subject, body=body, message_type='notification') #'fleet.vehicle.odometer' object has no attribute 'message_post'
        except AttributeError:
            print("No driver in vehicle!")


        # for record in self
        #     record.message_post(subject=subject, body=body)

        # self.env['fleet.vehicle'].browse([])

            # self.env['fleet.vehicle'].message_post(subject=subject, body=body) #wrong
        
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

    def _get_last_front_image(self):
        FleetVehicalImage = self.env['fleet.vehicle.log.images']
        for record in self:
            vehicle_image = FleetVehicalImage.search([('vehicle_id', '=', record.id)], limit=1, order='create_date desc')
            if vehicle_image:
                record.last_image_front = vehicle_image.car_image_front
                record.last_image_back =  vehicle_image.car_image_back
                record.last_image_right_side = vehicle_image.car_image_izq
                record.last_image_lefth_side = vehicle_image.car_image_der
            else:
                record.last_image_front = None
                record.last_image_back = None
                record.last_image_right_side = None
                record.last_image_lefth_side = None

    def _set_front_image(self):
        for record in self:
            if record.last_image_front:
                date = fields.Date.context_today(record)
                data = {
                    'car_image_front': record.last_image_front,
                    'car_image_back':record.last_image_back,
                    'car_image_izq':record.last_image_right_side,
                    'car_image_der':record.last_image_lefth_side,

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



        today = fields.Date.from_string(fields.Date.today())
        for record in self:
            print("\n Entra en el for de _compute_kms_left")
            # print("\n1. record.kms_next_estimate", record.kms_next_estimate )
            # print("\n2. record.state_maintenance", record.state_maintenance )
            # if record.kms_next_estimate and record.state_maintenance in ['open', 'closed', 'expired','futur']:
            renew_kms = record.set_kms
            # print("\n3. record.kms_next_estimate", record.kms_next_estimate)
            diff_kms = (renew_kms - record.odometer)
            record.kms_left = diff_kms if diff_kms > 0 else diff_kms
            record.do_today = diff_kms <= 0
            # else:
                # record.kms_left = -1
                # record.do_today = False
    
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
                
            # else:
            #     print("LATEST VALUES ", last_main.kms_next_estimate, last_main.service_id)
            #     if not last_main.kms_next_estimate > 0:
            #         record.kms_next_estimate=20000
            #         # raise exceptions.UserError('No se puede asignar el valor de Cero a el proximo mantenimiento!')
            #     else:
            #         record.kms_next_estimate=20000
            

    @api.depends('service_state')
    def _compute_maintenance_state(self):
        print("\n *********************************************** \n")
        print("\n **** def _compute_maintenance_state(self): Class [maintenance]**** \n")
        print("\n *********************************************** \n")
        for record in self:
            print("\n Entra en el for de _compute_maintenance_state")
            print("\n SERVICE DESCRIPTION:", record.description)
            if record.service_state:
                if record.service_state == "new":
                    record.state_maintenance = "open"
                elif record.service_state == "done":
                    record.state_maintenance = "futur"
                    # if record.complete 
                    print("\n Here is where the data is chnaged!!")
                elif record.service_state == "cancelled":
                    record.state_maintenance = "expired"
                else: # cancelled
                    record.state_maintenance = "expired"


class InheritedFleetServiceType(models.Model):
    _inherit = 'fleet.service.type'

    reference = fields.Integer(string="Referencia (KM)", help="Referencia de Kilometrajes para próximos manteniemientos")

    _sql_constraints = [
        ('inherited_fleet_service_type_check_reference', 'CHECK(reference > 0 AND reference < 30000)', 'The reference for maintenance must be POSITIVE but Lower Than 30000')
    ]
        
