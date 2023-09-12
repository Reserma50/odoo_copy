# -*- coding: utf-8 -*-
# from odoo import http


# class ComprasFields(http.Controller):
#     @http.route('/compras_fields/compras_fields', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/compras_fields/compras_fields/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('compras_fields.listing', {
#             'root': '/compras_fields/compras_fields',
#             'objects': http.request.env['compras_fields.compras_fields'].search([]),
#         })

#     @http.route('/compras_fields/compras_fields/objects/<model("compras_fields.compras_fields"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('compras_fields.object', {
#             'object': obj
#         })
