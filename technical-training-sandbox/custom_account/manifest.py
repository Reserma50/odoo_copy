{
    'name': 'Custom Account',
    'version': '1.0',
    'summary': 'Modificación del plan de cuentas',
    'depends': ['account'],  # Si el módulo depende de otros, agrégalos aquí
    'data': [
        'account_data.xml',  # Asegúrate de que este archivo exista y contenga los datos del plan de cuentas
    ],
    'installable': True,
    'auto_install': False,
}
