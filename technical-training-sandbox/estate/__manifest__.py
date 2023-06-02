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
        'views/estate_menus.xml',
        'views/estate_menu_tree.xml',
        
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        #'demo/demo_data.xml',
    ],
    'application': True,

}