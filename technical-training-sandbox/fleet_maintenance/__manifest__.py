{
    'name': "Fleet Maintenance",
    'version': '1.0',
    'depends': ['base','fleet', 'hr'],
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
        'views/views_tree/inherited_fleet_vehicle_maintenance.xml',
        # 'views/views_tree/inherited_fleet_vehicle_matriculation.xml',
        'views/views_tree/inherited_fleet_vehicle_image.xml',
        'views/views_tree/inherited_fleet_new_driver_id.xml',
        'views/fleet_maintenance.xml',
        'views/fleet_matriculation.xml',
        'views/driver_licence/fleet_menu_view_tree_search.xml',
        #estate fleet licence
        'views/driver_licence/fleet_drivers_action_menu.xml',
        #log hr fleet
        'views/hr_fleet/fleet_log_assignation.xml',
        # user fleet driver
        # 'views/driver_licence/new_form_user_fleet.xml', You don't need to use ... this because the field does not exist!

        #report
        'report/images_report.xml',
        'report/images_template.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'fleet_maintenance/static/src/views/**/*',]},
    # data files containing optionally loaded demonstration data
    'demo': [
        #'demo/demo_data.xml',
    ],
    'application': False,
    'license': 'LGPL-3',

}