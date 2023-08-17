{
    'name': "Fleet Maintenance",
    'version': '1.0',
    'depends': ['base','fleet'],
    'author': "Joseph González",
    'category': 'App',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',
        #tree views
        'views/views_tree/inherited_fleet_service_type.xml',
        
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        #'demo/demo_data.xml',
    ],
    'application': False,

}