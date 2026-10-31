###############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2015  Jorge Soto Garcia
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
#    along with this program. If not, see https://www.gnu.org/licenses/agpl.
#
###############################################################################
{
    "name": "Driving Licence",
    "summary": "Manage driving licence categories and implied licences",
    "version": "18.0.1.0.0",
    "description": """
Driving Licence
===============

Manage country-specific driving licence categories and the licences
implied by each category.

The module includes the Spanish driving licence catalogue, retains the
historical XML identifiers, and provides a configuration shortcut to
manage the catalogue.
    """,
    "author": "Jorge Soto Garcia",
    "maintainer": "Jorge Soto Garcia",
    "contributors": ["Jorge Soto Garcia <sotogarcia@gmail.com>"],
    "website": "https://github.com/sotogarcia/odoo-normative",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        "base",
        "base_setup",
    ],
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "data": [
        "security/driving_licence.xml",
        "data/driving_licence_data.xml",
        "views/driving_licence_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
