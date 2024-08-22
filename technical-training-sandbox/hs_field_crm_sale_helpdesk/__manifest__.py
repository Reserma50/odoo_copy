# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
# 

{
	'name': 'HS News Fields CRM-Ventas-Helpdesk',
	'version': '1.0',
	'summary':'News Fields CRM-Ventas-Helpdesk',
	'category': 'Tool',
	'depends': ['base','product','stock'],
	'description': """
		Módulo para agregar nuevos campos en CRM, Ventas y Helpdesk
	""",

	'author': 'H S.A.',
	# 'license': 'OPL-1',
	'data': [
        'security/ir.model.access.csv',
		#'views/sale_fields.xml',
		#'views/helpdesk_fields.xml',
  		'views/crm_lead_fields.xml',
	  	'views/crm_menu_comentarios.xml',
    	'views/crm_menu_eva_infra.xml',
        'views/crm_menu_pendientes.xml',
		'views/crm_menu_interesado.xml',
		'views/crm_comentarios.xml',
	    'views/crm_seguimientos.xml',
     	'views/crm_eva_infra.xml',
	    'views/crm_pendientes.xml',
	    'views/crm_interesado.xml',
        #Add
        'views/crm_inherit_stage.xml',



        #'views/helpdesk_fields_products.xml',

		#'views/product_product.xml',
	],
	'qweb': [
		# 'static/src/xml/pos_hide_tax.xml'
	],
		
	'installable': True,
	'auto_install': False,
}