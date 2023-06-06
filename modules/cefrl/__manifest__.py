# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2015
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses
#
###############################################################################
{
    'name': 'CEFR for Languages',
    'summary': 'Common European Framework of Reference for Languages',
    'version': '13.0.1.0.0',

    'description': 'Common European Framework of Reference for Languages',

    'author': 'Jorge Soto Garcia',
    'maintainer': 'Jorge Soto Garcia',
    'contributors': ['Jorge Soto Garcia <sotogarcia@gmail.com>'],

    'website': 'http://www.gitlab.com/',

    'license': 'AGPL-3',
    'category': 'Extra Tools',

    'depends': [
        'base',
        'base_setup',
        'base_field_m2m_view'
    ],

    'data': [
        'data/cefrl_level_group_data.xml',
        'data/cefrl_level_data.xml',
        'data/cefrl_language_data.xml',
        # 'data/cefrl_certificate_group_data.xml',
        # 'data/cefrl_certificate_data.xml',

        'security/cefrl_level_group.xml',
        'security/cefrl_level.xml',
        'security/cefrl_language.xml',
        'security/cefrl_certificate_group.xml',
        'security/cefrl_certificate.xml',
        'security/cefrl_certificate_implied_certificate_rel.xml',

        'views/cefrl.xml',

        'views/cefrl_level_group_view.xml',
        'views/cefrl_level_view.xml',
        'views/cefrl_language_view.xml',
        'views/cefrl_certificate_group_view.xml',
        'views/cefrl_certificate_view.xml',

        'views/res_config_settings_view.xml'
    ],

    'css': [
        'static/src/css/backend-styles.css'
    ],

    'installable': True
}
