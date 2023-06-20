{
    'name': "Real State",
    'version': '1.0',
    'depends': ['base'],
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
        'views/estate_menu_view_tree_search.xml',

        
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        #'demo/demo_data.xml',
    ],
    'application': True,

}