# -*- coding: utf-8 -*-
# from odoo import http


# class PeriodLock(http.Controller):
#     @http.route('/period_lock/period_lock', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/period_lock/period_lock/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('period_lock.listing', {
#             'root': '/period_lock/period_lock',
#             'objects': http.request.env['period_lock.period_lock'].search([]),
#         })

#     @http.route('/period_lock/period_lock/objects/<model("period_lock.period_lock"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('period_lock.object', {
#             'object': obj
#         })
