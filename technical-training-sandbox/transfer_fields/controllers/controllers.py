# -*- coding: utf-8 -*-
# from odoo import http


# class TransferFields(http.Controller):
#     @http.route('/transfer_fields/transfer_fields', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/transfer_fields/transfer_fields/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('transfer_fields.listing', {
#             'root': '/transfer_fields/transfer_fields',
#             'objects': http.request.env['transfer_fields.transfer_fields'].search([]),
#         })

#     @http.route('/transfer_fields/transfer_fields/objects/<model("transfer_fields.transfer_fields"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('transfer_fields.object', {
#             'object': obj
#         })
