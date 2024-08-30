# -*- coding: utf-8 -*-
# from odoo import http


# class RsCustomMaintenance(http.Controller):
#     @http.route('/rs_custom_maintenance/rs_custom_maintenance', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rs_custom_maintenance/rs_custom_maintenance/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('rs_custom_maintenance.listing', {
#             'root': '/rs_custom_maintenance/rs_custom_maintenance',
#             'objects': http.request.env['rs_custom_maintenance'].search([]),
#         })

#     @http.route('/rs_custom_maintenance/rs_custom_maintenance/objects/<model("rs_custom_maintenance"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rs_custom_maintenance.object', {
#             'object': obj
#         })
