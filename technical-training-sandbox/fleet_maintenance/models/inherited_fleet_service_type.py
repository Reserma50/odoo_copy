from odoo import fields, models, api

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
            'description':f" Mantenimiento de {val}",
            'service_type_id':val,
            'date': 'out_invoice',
            'vehicle_id': self.buyer_id.id,
            'purchaser_i': val,  # company comes from the journal
            'odometer' : val
        }

        return servicio_vals



    def _compute_vehicle_log_name(self):
        print("SE AÑADE UN NUEVO ODOMETRO")

        # To create an service, we need the following information:
        # a description: the customer
        # a service_type_id: it has several possible values
        # a date: the accounting journal
        # a vehicle_id: the vehicle
        # purchaser_i: the driver
        # odometer : last_odometer




        
        res = super(InheritedFleetVehicleOdometer, self)._compute_vehicle_log_name()
        #self.odometer
        print(res)
        print(type(res))
        all_types = self.env['fleet.service.type'].search([('category', '=', 'service')])
        print(all_types)
        # for record in self:
        #     print(record)
            
            #traer los tipos de servicios
        order = "create_date DESC"
        for my_type in all_types:
            #llamar los registros asociados al vehiculo de la base de datos de mantenimientos 
            # mantenimientos = self.env['fleet.vehicle.maintenance'].search([('services_ids', '=', self.vehicle_id.id),('services_ids.service_type_id.id', '=', my_type.id)])
            last_maintenance = self.env['fleet.vehicle.maintenance'].search([('services_ids', '=', self.vehicle_id.id),('services_ids.service_type_id.id', '=', 47)], order=order, limit=1)
            print("ULTIMO MANTENIMIENTO CANT", len(last_maintenance))
            print(f"Para el tipo {my_type.name} existen alrededor de {len(last_maintenance)}")
            if (my_type.id == 47 and last_maintenance.services_ids.state != "done"):
                #crear mantenimiento
                if self.value - last_maintenance.services_ids.odometer >= my_type.reference:
                    print("creando mantenimiento a los ", last_maintenance.services_ids.odometer)
                    servicio_vals = {
                    'description':f" Mantenimiento de {my_type.name} requerido, vehiculo alcanzo la referencia de {my_type.reference}",
                    'service_type_id':my_type.id,
                    'vehicle_id': self.vehicle_id.id,
                    'purchaser_id': self.driver_id.id,  # company comes from the journal
                    'odometer' : self.value
                    }

                    service = self.env['fleet.vehicle.log.services'].sudo().create(servicio_vals)
                    print(service)
                    maintenance_vals = {
                    'services_ids':service.service_id,
                    'kms_recorridos' : self.value
                    }
                    # maintenance = self.env['fleet.vehicle.maintenance'].sudo().create(maintenance_vals)
                    # print(maintenance)
                    break #se ejecutara el bucle y no queremos eso
                # print(service)
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
    
    kms_recorridos = fields.Char(string="KM", compute='_compute_km_maintenance',
                                 help="Verde, indica los Kilometros que faltan para un futuro mantenimiento. Rojo, indica los Kilometros recorridos sin haber realizado el mantenimiento.")

    # @api.depends("odometros_ids.odometer")
    # def _compute_km_maintenance(self):
    #     'dependiendo del valor del odometro y de cuando el servicio se genero (si existe) calcular kms'



