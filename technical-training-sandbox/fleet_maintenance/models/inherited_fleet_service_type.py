from odoo import fields, models, api, Command, _

class InheritedFleetServiceType(models.Model):
    _inherit = 'fleet.service.type'

    reference = fields.Integer(string="Referencia (KM)", help="Referencia de Kilometrajes para próximos manteniemientos")

    _sql_constraints = [
        ('inherited_fleet_service_type_check_reference', 'CHECK(reference > 0 AND reference < 30000)', 'The reference for maintenance must be POSITIVE but Lower Than 30000')
    ]

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
        
        # To create an service, we need the following information:
        # a description: the customer
        # a service_type_id: it has several possible values
        # a date: the accounting journal
        # a vehicle_id: the vehicle
        # purchaser_i: the driver
        # odometer : last_odometer
        print("CAMPOS COMO LOS DE SELF")
        for field_name, field in self.fields_get().items():
            
            if field_name in self:
                print(f"Campo: {field_name}, Valor: {self[field_name]}")
        
        print("My Self", self.vehicle_id.id)


        # servicio_vals = 

        # service = self.env['fleet.vehicle.log.services'].sudo().create(servicio_vals)
        # print(service)
        # maintenance_vals = 
        return self.env['fleet.vehicle.maintenance'].create(
            {
                'services_ids':[
                    Command.create({
                        "vehicle_id": self.vehicle_id.id,
                        "description":f" Mantenimiento de {my_type.name} requerido; Vehiculo alcanzó la referencia de {my_type.reference} ",
                        "odometer_id" : record.id,
                        "purchaser_id": self.driver_id.id,  # 
                        "service_type_id":my_type.id,   
                    })
                ],
                "kms_recorridos" : self.value,
            }
        )
        
    def actualizar_servicios_manteniento(self, my_type, last_maintenance):
        
        print("CAMPOS COMO LOS DE SELF! En la función actualizar!")
        for field_name, field in self.fields_get().items():
            
            if field_name in self:
                print(f"Campo: {field_name}, Valor: {self[field_name]}")
        
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


    # def _compute_vehicle_log_name(self):
    #     '''CALL SUPER METHOD AND ADD FEATURE'''
    #     print("SE AÑADE UN NUEVO ODOMETRO")

    #     for field_name, field in self.fields_get().items():
    #         if field_name in self:
    #             print(f"Campo: {field_name}, Valor: {self[field_name]}")
        
    #     res = super(InheritedFleetVehicleOdometer, self)._compute_vehicle_log_name()
    #     return res
    
    @api.model
    def create(self, vals):
        record = super(InheritedFleetVehicleOdometer, self).create(vals)
        # record.enviar_mi_nueva_notificacion_chatter()
        record.odometer_service_procedure(record)
        
        

        return record
        
        
    
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
                    self.send_service_notificaction(created=True, updated=False, service_type = my_type)
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
                            print("Es 0? Si odometro esta ODOMETRO DE LOS ULTIMO",last_maintenance.odometer)

                            break
                        print(f"({self.value} - {last_maintenance.odometer}) >= {my_type.reference}")
                        if ((self.value - last_maintenance.odometer) >= my_type.reference):
                            print("NO SE CREA MANTENIMIENTO PERO SE ACTUALIZA EL VALOR DEL KILOMETRAJE Y SE ENVIA NOTIFICACIÓN O MENSAJE!")
                            last_maintenance_to_update.write({'kms_recorridos':((self.value - last_maintenance.odometer)-my_type.reference)*-1})
                            self.send_service_notificaction(created=False, updated=True, service_type = my_type) #message

                            #chatter
                            self.message_post_after_service_maintenance(record=last_maintenance_to_update, new_message="Warning. Runnig Without Execute Maintenance !", message_values=last_maintenance)

                            break #se ejecutara el bucle y no queremos eso
                        else:
                            last_maintenance_to_update.write({'kms_recorridos':(my_type.reference - (self.value - last_maintenance.odometer))})
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

    def send_service_notificaction(self, created, updated, service_type):
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


class InheritedFleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    # image_ids = fields.One2many(comodel_name='fleet.vehicle.image',
    #                             inverse_name="",
    #                             string='Imagenes', 
    #                             domain=lambda self: [('state', 'in', ['offer_received', 'offer_accepted', 'sold'])]
    #                             )
                                

    @api.model
    def create(self, vals):
        record = super(InheritedFleetVehicle, self).create(vals)
        print("ADD CHATTER!!")
        record.enviar_mi_nueva_notificacion_chatter()
    
        return record
    
    def enviar_mi_nueva_notificacion_chatter(self):
        subject = _("Nueva lectura de %s, el servicio de %s " % (self.vehicle_id.name, self.service_type.name, ))
        body = _("Una nueva lectura de %s fue registrada para el vechiculo %s y genero un servicio de %s" % (self.odometer, self.vehicle_id.name, self.service_type.name, ))
        
        
        # for record in self:
        #     record.message_post(subject=subject, body=body)

        # self.env['fleet.vehicle'].browse([])

            # self.env['fleet.vehicle'].message_post(subject=subject, body=body) #wrong
        self.message_post(subject=subject, body=body, message_type='notification') #'fleet.vehicle.odometer' object has no attribute 'message_post'
        return True
    
class InheritFleetImage(models.Model):

    _name= "fleet.vehicle.image"
    _description = "Different views"
    _order = 'date desc'

    date = fields.Date(default=fields.Date.context_today)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True)
    car_image_front = fields.Binary(string='Imagen de Frente/Delantera')
    car_image_back = fields.Binary(string='Imagen Posterior/Trasera')
    car_image_izq = fields.Binary(string="Imagen Lado Izquierdo/Conductor")
    car_image_der = fields.Binary(string='Imagen Lado Derecho/Copiloto')

