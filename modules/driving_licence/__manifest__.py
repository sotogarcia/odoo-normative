# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2015
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public Licence as
#    published by the Free Software Foundation, either version 3 of the
#    Licence, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public Licence for more details.
#
#    You should have received a copy of the GNU Affero General Public Licence
#    along with this program.  If not, see http://www.gnu.org/licences
#
###############################################################################
{
    'name': 'Driving licence',
    'summary': 'Driver licence information',
    'version': '13.0.1.0.0',

    'description': 'Driver licence information',

    'author': 'Jorge Soto Garcia',
    'maintainer': 'Jorge Soto Garcia',
    'contributors': ['Jorge Soto Garcia <sotogarcia@gmail.com>'],

    'website': 'http://www.gitlab.com/sotogarcia',

    'licence': 'AGPL-3',
    'category': 'Extra Tools',

    'depends': [
        'base',
        'base_setup',
        'base_field_m2m_view'
    ],

    'data': [
        'data/driving_licence_data.xml',

        'security/driving_licence.xml',

        'views/driving_licence_view.xml',
        'views/res_config_settings_view.xml'
    ],

    'installable': True
}
