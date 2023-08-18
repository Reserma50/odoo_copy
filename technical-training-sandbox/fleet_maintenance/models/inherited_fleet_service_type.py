from odoo import fields, models, api, Command

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
    _inherit = 'fleet.vehicle.odometer'

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

    def crear_servicios_manteniento(self, my_type):
        
        # To create an service, we need the following information:
        # a description: the customer
        # a service_type_id: it has several possible values
        # a date: the accounting journal
        # a vehicle_id: the vehicle
        # purchaser_i: the driver
        # odometer : last_odometer

        for field_name, field in self.fields_get().items():
            print("CAMPOS COMO LOS DE SELF")
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
                        "odometer" : self.value,
                        "purchaser_id": self.driver_id.id,  # 
                        "service_type_id":my_type.id,   
                    })
                ],
                "kms_recorridos" : self.value,
            }
        )


    def _compute_vehicle_log_name(self):
        '''CALL SUPER METHOD AND ADD FEATURE'''
        print("SE AÑADE UN NUEVO ODOMETRO")

        for field_name, field in self.fields_get().items():
            if field_name in self:
                print(f"Campo: {field_name}, Valor: {self[field_name]}")
            


        
        res = super(InheritedFleetVehicleOdometer, self)._compute_vehicle_log_name()
        #self.odometer
        print(res)
        print(type(res))
                    
        #traer los tipos de servicios
        all_types = self.env['fleet.service.type'].search([('category', '=', 'service')])
        print(all_types)
        #EJECUTAR SERVICIO de la lista
        order = "create_date DESC"
        for my_type in all_types:
            #llamar los registros asociados al vehiculo de la base de datos de mantenimientos por fecha y vehiculo segun odometro
            # mantenimientos = self.env['fleet.vehicle.maintenance'].search([('services_ids', '=', self.vehicle_id.id),('services_ids.service_type_id.id', '=', my_type.id)])
            if my_type.id == 47:
                print(f"BUSCANDO LOS VALORES DE LA TABLA:  {self.vehicle_id.id}", )
                total_len = self.env['fleet.vehicle.maintenance'].search_count([('services_ids.vehicle_id.id', '=', self.vehicle_id.id),('services_ids.service_type_id.id', '=', my_type.id)])
                print("TOTAL, ", total_len)
                
                if total_len == 0: #No existe
                    #service lines
                    print("before")
                    maintenance = self.crear_servicios_manteniento(my_type=my_type)
                    print("after")
                else:
                    last_maintenance = self.env['fleet.vehicle.maintenance'].search([('services_ids.vehicle_id.id', '=', self.vehicle_id.id),('services_ids.service_type_id.id', '=', my_type.id)],order=order)
                    print("Contiene data el último mantenimiento?")
                    for field_name, field in last_maintenance.fields_get().items():
                        if field_name in self:
                            print(f"Campo: {field_name}, Valor: {self[field_name]}")
                    
                    print("LAST MAINTENANCE ", last_maintenance)
                    last_km=last_maintenance.kms_recorridos
                    print("ULTIMO MANTENIMIENTO CONTIENE (Servicios):", last_maintenance.services_ids)
                    # last_maintenance.services_ids.search(order=order, limit=1) #No valid
                    last_maintenance = last_maintenance.services_ids.sorted(key=lambda r: r.create_date, reverse=True)[0]
                    print("")
                    print(last_maintenance)
                    print(f"Para el tipo {my_type.name} existen {last_maintenance.description} con id {last_maintenance.id} with last odometer {last_maintenance.odometer}")
                    if (my_type.id == last_maintenance.service_type_id.id and last_maintenance.state != "done" and my_type.reference > 0):
                        #crear mantenimiento
                        if last_maintenance.odometer == 0:
                            print("Si odometro esta en 0 _ ODOMETRO DE LOS ULTIMO",last_maintenance.odometer)
                            break
                        print(f"({self.value} - {last_maintenance.odometer}) >= {my_type.reference}")
                        if ((self.value - last_maintenance.odometer) >= my_type.reference):
                            print("NO SE CREA MANTENIMIENTO PERO SE ACTUALIZA EL VALOR DEL KILOMETRAJE Y SE ENVIA NOTIFICACIÓN O MENSAJE!")
                            break #se ejecutara el bucle y no queremos eso
                        else:
                            print("FALTAN KILOMETROS.")
                        # print(service)
                    elif last_maintenance.state == "done" and last_maintenance.vehicle_id.id == self.vehicle_id.id:
                        print(f"({self.value} - {last_maintenance.odometer}) >= {my_type.reference}")
                        if ((self.value - last_maintenance.odometer) >= my_type.reference):
                            print("creando mantenimiento a los ", last_maintenance.odometer)
                            #service not create #no se ha hecho
                            maintenance = self.crear_servicios_manteniento(my_type=my_type)
                            # print(maintenance)
                            break #se ejecutara el bucle y no queremos eso
                        else:
                            print("FALTAN KILOMETROS.")
                    elif last_maintenance.state == "done" and last_maintenance.vehicle != self.vehicle_id:
                        print("CAMBIO EN LOS DATOS, NO ES EL MISMO AUTO DE ")
                    else:
                        print("NO SE GENERO PORQUE AÚN NO SE HA EFECTUADO EL MANTENIMIENTO.")

                    #if no exist then -->    
                    #create service obtaint id
                    #create manintenance obtaint id

        return res


    
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

    
    kms_recorridos = fields.Char(string="KM", 
                                 help="Verde, indica los Kilometros que faltan para un futuro mantenimiento. Rojo, indica los Kilometros recorridos sin haber realizado el mantenimiento.")

    # @api.depends("services_ids.odometer")
    # def _compute_km_maintenance(self):

    #     'dependiendo del valor del odometro y de cuando el servicio se genero (si existe) calcular kms'
    #     print("computando")
    #     self.kms_recorridos = 190


