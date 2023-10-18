# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, SUPERUSER_ID

#
# Conditional installation of enterprise modules.
#
# This module is defined in community but some steps (defined with 'edition: "enterprise"')
# are only used to test enterprise. As it's not possible to direcly add enterprise
# modules dependencies, this post install hook will install account_accountant if exists.
#
def _auto_install_enterprise_dependencies(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    print("\n \n \n \n")
    print("CR", cr)
    print("**************")
    print("\n \n \n \n")
    print("registry", registry)
    module_list = ['account_accountant']
    module_ids = env['ir.module.module'].search([('name', 'in', module_list)])
    module_ids.sudo().button_install()
