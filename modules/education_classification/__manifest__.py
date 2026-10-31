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
#    along with this program.  If not, see http://www.gnu.org/licenses
#
###############################################################################
{  # noqa: B018
    "name": "Education Classification",
    "version": "18.0.1.0.0",
    "summary": (
        "Manage educational classifications, editions, categories, "
        "and correspondence mappings"
    ),
    "description": """
Education Classification
========================

Manage international and national educational classifications through
a common, extensible data model.

The module provides a unified structure for classification schemes,
editions, hierarchical categories, and correspondence mappings.

Classification schemes
----------------------

Classification schemes are organised into three educational dimensions:

* Educational programmes (P).
* Educational attainment (A).
* Fields of education and training (F).

Schemes may have international, national, or other geographical scopes.
National schemes can be associated with a country, while other schemes
may describe their geographical coverage independently.

Each scheme supports multiple editions, allowing historical versions
and their categories to coexist.

International classifications
-----------------------------

The module includes the following UNESCO classifications:

* ISCED-P 2011: Classification of educational programmes.
* ISCED-A 2011: Classification of educational attainment.
* ISCED-F 2013: Classification of fields of education and training.

The corresponding schemes, editions, and hierarchical categories are
provided as initial reference data.

National classifications
------------------------

Additional classifications can be created for individual countries
or other geographical areas.

National classifications maintain their own editions, categories,
and hierarchical structures independently of international schemes.

This allows classifications such as the Spanish CNED to be incorporated
without modifying the international reference catalogues.

Correspondence mappings
-----------------------

The module provides a generic structure for defining correspondences
between different classification editions.

Correspondence mappings support:

* Source and target classification editions.
* Publishing authorities and documentary references.
* Source versions, attachments, and checksums.
* Historical revisions and superseded mappings.
* Simple, composite, conditional, and unmatched rules.
* Exact, close, broader, narrower, and related semantic relationships.
* Multiple source and target categories within individual rules.
* Validation states and explanatory notes.

Mappings preserve their source documentation and distinguish semantic
relationships from automatically resolvable equivalences.

Access control
--------------

All users have read access to the classification catalogues.

Only members of the Education Classification Manager group may create,
modify, or delete classification records.

Integration
-----------

The module depends on Odoo Base, Web, and Web Hierarchy. It can be reused
by educational, training, statistical, and other applications requiring
structured educational classifications, without any specific academic
management module.

A recursive list implementation is being adapted from the LGPL-3.0
recursive_list_view project by Marc Durepos / Bemade Inc.
Its JavaScript, XML, and CSS resources are bundled locally; registration
and activation of this custom view remain pending. See README.md for
the original source, attribution, and integration status.
    """,
    "author": "Jorge Soto Garcia",
    "website": "https://github.com/sotogarcia/odoo-normative",
    "license": "AGPL-3",
    "category": "Academy",
    "maintainer": "Jorge Soto Garcia",
    "contributors": ["Jorge Soto Garcia <sotogarcia@gmail.com>"],
    "depends": ["base", "web", "web_hierarchy"],
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "data": [
        "data/res_groups_data.xml",
        "security/ir.model.access.csv",
        "data/res_partner_data.xml",
        "data/education_classification_scheme_data.xml",
        "data/education_classification_edition_data.xml",
        "data/education_classification_item_isced_a_2011_data.xml",
        "data/education_classification_item_isced_f_2013_data.xml",
        "data/education_classification_item_isced_p_2011_data.xml",
        "views/education_classification_edition_view.xml",
        "views/education_classification_item_view.xml",
        "views/education_classification_mapping_rule_line_view.xml",
        "views/education_classification_mapping_rule_view.xml",
        "views/education_classification_mapping_view.xml",
        "views/education_classification_scheme_view.xml",
        "views/res_config_settigns_view.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "education_classification/static/src/css/tree_recursive_styles.css",
            "education_classification/static/src/js/relational_model.js",
            "education_classification/static/src/js/list_controller.js",
            "education_classification/static/src/js/list_renderer.js",
            "education_classification/static/src/xml/recursive_tree_templates.xml",
        ],
    },
    "application": False,  # True only for top-level apps
    "installable": True,  # visible in Apps
    "auto_install": False,  # or True / or a subset of depends
}
