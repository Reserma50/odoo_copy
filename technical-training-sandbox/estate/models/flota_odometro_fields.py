# from odoo import models, fields, api, exceptions

# class flota_odometro_fields(models.Model):
#     _inherit = 'fleet.vehicle'

#     last_odometer = fields.Float(string="odometer trigger", compute="_compute_odometer")    
#     # @api.depends("odometer")
#     # def _compute_odometer(self):
#     #     for record in self:
#     #         print("NEW ODOMETER", record.odometer)
#     #         raise exceptions.UserError(f'Pay attention:Odometer! {record.odometer}.', )
#     @api.depends("odometer")
#     def _compute_custom_field(self):
#         # a = super()._get_odometer()
#         print("Se ha activado un cambio en el Modelo Odometer Vehicle")
#         for vehicle in self:
#             print(vehicle.odometer)
#         # if a is not None:
#         #     raise exceptions.UserError(f'Pay attention:Odometer! {a}.')
#         # return super()._set_odometer()