# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2025 Jorge Soto Garcia
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
    "name": "CEFR for Languages",
    "summary": "Common European Framework of Reference for Languages",
    "version": "18.0.1.0.0",
    "description": """
CEFR for Languages
==================

Master data for the **Common European Framework of Reference for Languages (CEFR)**.

This module provides CEFR level groups, levels, languages and a registry of
certificates (with implied/derived relations) to be reused by other apps
(HR, Academy, LMS, CRM, etc.).

Key Features
------------

- **Level groups** (A, B, C).
- **Levels** A1 … C2.
- **Languages**: a curated base list ready to use.
- **Certificates** with *implied certificate* relations to model hierarchies
  (e.g., C1 ⇒ B2 ⇒ B1).
- **Configuration panel** in *Settings* to tailor basic options.
- List and form views for all models; improved many2many selection UX.

Use Cases
---------

- Store CEFR level and certificates for people (students, employees, candidates).
- Classify training actions or course requirements by CEFR level.
- Express equivalences via implied certificates.

Configuration
-------------

1. Go to **Settings ▸ General Settings ▸ CEFR** and review defaults.
2. (Optional) Extend languages/certificates with your own records.

Access Rights
-------------

The module defines separate security groups for CEFR *level groups*, *levels*,
*languages* and *certificates* to allow fine-grained permissions.

Compatibility & Dependencies
----------------------------

- **Odoo**: 18.0
- **Depends on**: ``base``, ``base_setup``, ``base_field_m2m_view``
- **License**: AGPL-3

Notes
-----

This module ships **reference data** and generic models; it does not alter
business flows by itself. Other modules can depend on it to link CEFR
information to their own records.
    """,
    "author": "Jorge Soto Garcia",
    "maintainer": "Jorge Soto Garcia",
    "contributors": ["Jorge Soto Garcia <sotogarcia@gmail.com>"],
    "website": "https://www.github.com/sotogarcia",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": ["base", "base_setup", "base_field_m2m_view"],
    "data": [
        "data/cefrl_level_group_data.xml",
        "data/cefrl_level_data.xml",
        "data/cefrl_language_data.xml",
        "data/cefrl_certificate_group_data.xml",
        "data/cefrl_certificate_data.xml",
        "security/cefrl_level_group.xml",
        "security/cefrl_level.xml",
        "security/cefrl_language.xml",
        "security/cefrl_certificate_group.xml",
        "security/cefrl_certificate.xml",
        "security/cefrl_certificate_implied_certificate_rel.xml",
        "views/cefrl_level_group_view.xml",
        "views/cefrl_level_view.xml",
        "views/cefrl_language_view.xml",
        "views/cefrl_certificate_group_view.xml",
        "views/cefrl_certificate_view.xml",
        "views/res_config_settings_view.xml",
    ],
    "assets": {
        # Common assets (shared by backend, website, PoS...)
        "web.assets_common": ["cefrl/static/src/css/backend-styles.css"],
    },
    "installable": True,
}
