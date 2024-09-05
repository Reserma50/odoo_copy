# -*- coding: utf-8 -*-
{
    'name': "transfer_fields",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'account', 'sale','maintenance'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        # Base 

        'views/base/templates.xml',
        # my mantenance
        'views/inherited/modf_view_search_maintenance.xml',

        'views/base/views_tranfer_fields_model.xml',
        'views/base/views_marcaftk_fields_model.xml',
        'views/base/views_location_fields_model.xml',
        #perifericos
        'views/base/periferico_fields_view_tree.xml',
        #Maintenimientos equipos
        'views/inherited/modf_view_maintenence_team.xml',

        'views/inherited/modificar_view_transfer.xml',
        'views/inherited/modificar_view_location_form.xml',
        'views/inherited/modificar_view_maintenence_form.xml',
        'views/inherited/modificar_view_partner_form.xml',
        'views/inherited/modificar_view_lote_form.xml',
        'views/inherited/modificar_view_stock_tree.xml',
        'views/inherited/modificar_view_product_template_form.xml',
        'views/inherited/modificar_view_sale_form.xml',
        # Base 
        # 'views/base/transfer_fields_modalidad_view_tree.xml',
        # 'views/base/transfer_fields_modalidades_views.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
