{
    'name': "State Account",
    'version': '1.0',
    'depends': ['estate', 'account'],
    'author': "Joseph González",
    'category': 'App',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',

        #inherit res_users
        # 'views/my_users_maniputation_view/new_page_inside_notebook_users.xml',
        # 'views/my_users_maniputation_view/users_order.xml',
        
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        #'demo/demo_data.xml',
    ],
    'application': False,
    'license': 'LGPL-3',

}