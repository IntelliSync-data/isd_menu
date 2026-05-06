# -*- coding: utf-8 -*-
{
    'name': 'ISD Menu Manager',
    'version': '18.0.1.0.0',
    'category': 'ISD Modules',
    'summary': 'Custom menu visibility management per user',
    'description': """
ISD Menu Manager
================

This module allows administrators to configure menu visibility for each user individually.

Features:
* Add "Menu Config" tab in user form
* Show/hide menus per user with checkboxes
* Override default menu visibility logic
* Easy menu configuration interface
    """,
    'author': 'IntelliSyncData',
    'website': 'https://intellisyncdata.com',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_users_views.xml',
        'views/webclient_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
