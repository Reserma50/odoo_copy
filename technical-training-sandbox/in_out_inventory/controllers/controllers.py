# -*- coding: utf-8 -*-
# from odoo import http


# class InOutInventory(http.Controller):
#     @http.route('/in_out_inventory/in_out_inventory', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/in_out_inventory/in_out_inventory/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('in_out_inventory.listing', {
#             'root': '/in_out_inventory/in_out_inventory',
#             'objects': http.request.env['in_out_inventory.in_out_inventory'].search([]),
#         })

#     @http.route('/in_out_inventory/in_out_inventory/objects/<model("in_out_inventory.in_out_inventory"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('in_out_inventory.object', {
#             'object': obj
#         })
