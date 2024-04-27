# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class FleetVehicleAssignationLog(models.Model):
    _inherit = ['fleet.vehicle.assignation.log','mail.thread', 'mail.activity.mixin']
    _name = "fleet.vehicle.assignation.log"
    

    driver_employee_id = fields.Many2one('hr.employee', string='Driver (Employee)', compute='_compute_driver_employee_id', store=True, readonly=False)
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
#signature
    signature = fields.Image('Signature', help='Signature', copy=False, attachment=True)
    is_signed = fields.Boolean('Is Signed', compute="_compute_is_signed")
    is_locked = fields.Boolean(default=True, help='When the changes is not done this allows changing the '
                               'initial fields. When the changes is done this allows '
                               'changing the done fields.')
    image_front = fields.Binary(string='Frontal',
        help='Front side image of the vehicle at the moment of this log', attachment=True)
    image_back = fields.Binary(string='Posterior',attachment=True,
        help='Back side  image of the vehicle at the moment of this log')
    image_right_side = fields.Binary(string='Lado Derecho',attachment=True,
        help='right (copilot) side image of the vehicle at the moment of this log')
    image_lefth_side = fields.Binary(string='Lado Izquierdo',attachment=True,
        help='lefth (pilot) side image of the vehicle at the moment of this log')
    image_fuel_level = fields.Binary(string='Nivel de Combustible',attachment=True,
        help='Fuel image level of the vehicle at the moment of this log')
    

    @api.depends('signature')
    def _compute_is_signed(self):
        for vehicle in self:
            vehicle.is_signed = vehicle.signature

    def write(self, vals):
        # print("My vals", vals)
        res = super(FleetVehicleAssignationLog, self).write(vals)
        if vals.get('signature'):
            for vehicle in self:
                vehicle._attach_sign()
                # vehicle._create_activity_notification(True)
        return res

    def _attach_sign(self):
        """ Render the changes report in pdf and attach it to the picking in `self`. """
        self.ensure_one()
        # report = self.env['ir.actions.report']._render_qweb_pdf("stock.action_report_delivery", self.id) #modificando el reporte
        report = self.env['ir.actions.report']._render_qweb_pdf("fleet_maintenance.action_report_images_2_0", self.id) #modificando el reporte
        
        filename = "%s_signed_car_changes" % self.vehicle_id.name
        if self.driver_id:
            message = _('Asignacion de vehiculo firmada por %s') % (self.driver_id.name)
        else:
            message = _('Asignación Firmada')
        data = [('%s.pdf' % filename, report[0])]
        self.message_post(
            attachments=[('%s.pdf' % filename, report[0])],
            body=message,
        )
        #enviar mediante correo
        

        return True

    
    # def _create_activity_notification(self, created):
    #     '''CREATE ACTIVITY'''

    #     for attachment in :
    #         file_name, file_content = attachment 
    #         # Convirtiendo el contenido del archivo a base64
    #         file_content_base64 = base64.b64encode(file_content)

    #     if self.id:
    #         my_log_assignation=self.env["fleet.vehicle.assignation.log"].search([('id', '=', self.id)])
    #         my_vehicle = self.env["fleet.vehicle"].search([('id', '=', self.vehicle_id.id)])

    #     if created:
    #         my_log_assignation.activity_schedule(
    #         'mail.mail_activity_data_todo',
    #         summary = 'Ha firmado el documento de asignación. Ver pdf.',
    #         user_id=my_log_assignation.diver_id.id, #my_vehicle.manager_id.id or 
    #         res_model_id = _('ADC[%s]') % (my_log_assignation),
    #         note=_('Asignación de vehículo (%s), por %s el día %s') % (my_vehicle.name ,my_vehicle.driver_id.name, fields.date.today()),
    #         attachment_ids= [(0, 0, {
    #         'name': file_name,
    #         'type': 'binary',
    #         'datas': file_content_base64,
    #         'datas_fname': file_name,
    #         'res_model': 'mail.mail_activity_data_todo',
    #     })])


    @api.depends('driver_id')
    def _compute_driver_employee_id(self):
        employees = self.env['hr.employee'].search([('address_home_id', 'in', self.driver_id.ids)])

        for log in self:
            employee = employees.filtered(lambda e: e.address_home_id.id == log.driver_id.id)
            log.driver_employee_id = employee and employee[0] or False

    def _compute_attachment_number(self):
        print("self",self)
        attachment_data = self.env['ir.attachment']._read_group([
            ('res_model', '=', 'fleet.vehicle.assignation.log'),
            ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        
        print("in calculate number self.ids", self.ids)
        print("atachment :", attachment_data)
        #verify data
        for data in attachment_data:
            print("The data, has ", data)

        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        print("el attachment", attachment)

        for doc in self:
            print("Searching log id", doc.id)
            doc.attachment_number = attachment.get(doc.id, 0)

    def action_get_attachment_view(self):
        print("GET DATA FILES!!")
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['views'] = [[self.env.ref('fleet_maintenance.view_attachment_kanban_inherit_hr_v2').id, 'kanban']]
        res['domain'] = [('res_model', '=', 'fleet.vehicle.assignation.log'), ('res_id', 'in', self.ids)]
        print("self.ids", self.ids)
        res['context'] = {'default_res_model': 'fleet.vehicle.assignation.log', 'default_res_id': self.id}
        print("self.id", self.id)
        return res

    # Work around to open the model
    def open_form_action(self):
        # Retrieve the record ID from the context or any other source
        # print("THIS IS MY ID", self.id)
        # print("SELF.CONTEXT", self._context)
        # print("SELF.CONTEXT", self.env.context)
        # record_id = self._context.get('active_id')
        # print("THIS IS MY RECORD_ID", record_id)
        if self.id:
            action = self.open_record_form_view(self.id)
            return action
        return False

    @api.model
    def open_record_form_view(self, record_id):
        print("WE ARE HERE")
        action = {
            'name': 'Edit Record',
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle.assignation.log',
            'view_mode': 'form',
            'res_id': record_id,
            'target': 'current',
        }
        return action
