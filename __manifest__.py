# -*- coding: utf-8 -*-
{
    'name': "reservation",
    'application': True,

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale_management',
        'sale',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/reservation_security.xml',
        'security/reservation_groups.xml',
        'views/reservation_views.xml',
        'views/reporting_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/reservation_menus.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
