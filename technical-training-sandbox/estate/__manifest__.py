{
    'name': "Real State",
    'version': '1.0',
    'depends': ['base','crm'],
    'author': "Joseph González",
    'category': 'App',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',

        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',

        'views/estate_menus.xml',

        'views/estate_menu_tree.xml',

        'views/estate_menu_tree_type.xml',
        'views/estate_menu_tree_tag.xml',
        'views/estate_menu_tree_offer.xml',

        # 'views/estate_menu_form.xml', #uncomment this line!!
        #no comment link
        # http://localhost:8069/web#id=19&cids=1&menu_id=70&action=85&model=estate.property&view_type=form
        #comment link
        # http://localhost:8069/web#id=19&cids=1&menu_id=70&action=85&model=estate.property&view_type=form
        'views/estate_menu_view_tree_search.xml',

        #external layout modifications
        # 'views/custom_external_layout.xml',


        # 'views/custom_sale_report.xml',

        'views/crm_lead_fields.xml',
        # 'views/crm_lead_fields_hide.xml'
        # my views Three
        'views/my_crm_view_three/crm_menu_tree_comentario.xml',
        'views/my_crm_view_three/crm_menu_tree_seguimiento.xml',
        'views/my_crm_view_three/crm_menu_tree_competidor.xml',
        #my forms 
        'views/my_crm_view_forms/crm_menu_form_comentario.xml',
        'views/my_crm_view_forms/crm_menu_form_seguimiento.xml',
        'views/my_crm_view_forms/crm_menu_form_competidor.xml',
        
        #tutorial 12
        'views/my_state_view_form/estate_menu_form_type.xml'
        
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        #'demo/demo_data.xml',
    ],
    'application': True,

}