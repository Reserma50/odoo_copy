# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class FleetVehicleAssignationLog(models.Model):
    _inherit = 'fleet.vehicle.assignation.log'

    driver_employee_id = fields.Many2one('hr.employee', string='Driver (Employee)', compute='_compute_driver_employee_id', store=True, readonly=False)
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
#signature
    signature = fields.Image('Signature', help='Signature', copy=False, attachment=True)
    is_signed = fields.Boolean('Is Signed', compute="_compute_is_signed")
    is_locked = fields.Boolean(default=True, help='When the changes is not done this allows changing the '
                               'initial fields. When the changes is done this allows '
                               'changing the done fields.')

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
    @api.depends('driver_id')
    def _compute_driver_employee_id(self):
        employees = self.env['hr.employee'].search([('address_home_id', 'in', self.driver_id.ids)])

        for log in self:
            employee = employees.filtered(lambda e: e.address_home_id.id == log.driver_id.id)
            log.driver_employee_id = employee and employee[0] or False

    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment']._read_group([
            ('res_model', '=', 'fleet.vehicle'),
            ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        #verify data
        for data in attachment_data:
            print("The data, has ", data)

        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for doc in self:
            doc.attachment_number = attachment.get(doc.id, 0)

    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['views'] = [[self.env.ref('fleet_maintenance.view_attachment_kanban_inherit_hr').id, 'kanban']]
        res['domain'] = [('res_model', '=', 'fleet.vehicle.assignation.log'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'fleet.vehicle.assignation.log', 'default_res_id': self.id}
        return res
