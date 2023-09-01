# -*- coding: utf-8 -*-
{
    'name': "sale_fields",

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
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',"web", 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',

        #custom external_layout_standard
        # 'views/custom/custom_sale_report.xml',

        #custom external layout boxed
        # 'report/inherit_report/external_layout_boxed_heredado.xml',

        #my own external layout
        'report/external_layout_proposal.xml',
        #report extend from my own layout
        'report/proposal_template_v2.xml',


        #Change Anexos Page
        'views/custom/views_tree_propuesta_ejecutiva.xml',

        #template and report PROPOSAL
        # 'report/proposal_template.xml',  #uncomment main template
        'report/proposal_report.xml',

        #edición 
        'report/proposal_template_edit.xml',

 
        
    ],
    'css': ['static/css/bootstrap.min.css'],


    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
