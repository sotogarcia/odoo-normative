# Education Classification — Odoo 18

\`education_classification\` provides reusable models and initial reference
data for educational classifications. It covers **classification schemes**,
their **editions**, **hierarchical categories**, and **correspondence
mappings** between editions.

It is a reference-data module, not a training-management application. The
module does not provide enrolments, courses, students or an automatic
equivalence/conversion engine.

## Classification model

The six Python models are organised as follows:

| Technical model | Function |
| --- | --- |
| \`education.classification.scheme\` | Identifies a classification system, dimension (programmes, attainment or fields), geographical scope and responsible authority. |
| \`education.classification.edition\` | Maintains versions of a scheme, publication/validity metadata, a previous edition and publication status. |
| \`education.classification.item\` | Holds the official category code/name, edition, parent/children and structural sequence. |
| \`education.classification.mapping\` | Defines a mapping between two editions, with publisher, source, version/checksum, attachment, status and supersession. |
| \`education.classification.rule\` | Describes a simple, composite, conditional or unmatched correspondence, including its semantic relationship and review status. |
| \`education.classification.rule.line\` | Associates source/target categories with a rule. |

For categories, the model uses \`parent_id\`, \`child_ids\`, stored
\`parent_path\`, calculated \`level\`, stored \`sequence_path\` and
\`child_count\`. The hierarchy has no fixed maximum depth at the model
level. Validation prevents cycles and parent-child relationships across
different editions. Category codes are unique **within an edition**.

Mappings may express exact, close, broader, narrower or related semantic
relationships. The model validates conditions and source/target cardinality
when rules are validated. Mapping records and their rules are managed by
users; the module does **not** automatically calculate equivalences.

## Included reference data

The module currently provides three **international** UNESCO/ISCED schemes
and editions:

| Classification | Dimension | Edition | Category records in seed XML |
| --- | --- | --- | ---: |
| ISCED-P | Educational programmes | 2011 | 91 |
| ISCED-A | Educational attainment | 2011 | 66 |
| ISCED-F | Fields of education and training | 2013 | 219 |
| **Total** | | **3 editions** | **376** |

Seed files are stored under \`data/\` and include stable Odoo XML IDs,
hierarchical categories, scheme and edition records, and a partner record
for the UNESCO Institute for Statistics.

The data model also supports national/other geographical scopes, including
future CNED editions, but **no CNED category dataset is included in the
repository at present**. No correspondence-mapping dataset is preloaded.

Data is based on official reference catalogues and should be reviewed
against the relevant published edition when using it for regulated
reporting.

## Views and access

The module defines list/form/search views for classifications and mappings,
plus a **hierarchy** view of classification items using the official Odoo
\`web_hierarchy\` addon. The category action exposes
\`list,form,hierarchy\` and initially applies the root-category filter.

Catalogue management is accessible through the **ISCED** section in
Odoo Settings for system administrators. It provides shortcuts to schemes,
editions, categories, mappings, rules and rule lines. It does not add a
separate top-level application menu.

Access rules grant reading permissions on these models to Odoo's
internal-user, portal and public groups. Members of
**Education Classification Manager** additionally receive create, write
and delete permissions. The Settings shortcut itself is limited to the
system-administrator group. Review deployment security and public exposure
in your own database.

## Recursive list view: implementation status

This repository also includes an **adapted recursive list frontend**, with
lazy loading of children intended to display nested categories in a
single expandable table.

The following source files are present:

\`\`\`text
static/src/
├── css/
│   └── tree_recursive_styles.css
├── js/
│   ├── list_controller.js
│   ├── list_renderer.js
│   └── relational_model.js
└── xml/
    └── recursive_tree_templates.xml
\`\`\`

The JavaScript files export dedicated controller, renderer and model
classes rather than globally patching Odoo's corresponding prototypes.
The XML contains primary-inheritance OWL templates scoped to the custom
renderer, and the CSS supplies the expansion-column styling and indentation
rules (explicitly defined for depths 1–12).

**Status: not yet fully integrated or runtime-tested.** Although these files
are declared in \`web.assets_backend\`, the repository does not yet
provide the custom list-view registry entry, connect the dedicated OWL
templates through the renderer's static properties or set a corresponding
\`js_class\` on the category list view. Therefore the ordinary list view
is still used and the desired in-place expand/collapse interaction is not
yet enabled.

This is distinct from the existing \`hierarchy\` view, which is provided
by \`web_hierarchy\` and remains a module dependency.

Before considering the custom list complete, register the view, bind
the renderer templates, select it in the list XML and verify expansion,
grandchildren, ordering, filtering, refresh and permissions on Odoo 18.

## Origin of the adapted recursive-list code

The recursive frontend is **based on** the open-source addon
[\`recursive_list_view\` (branch 18.0)](https://github.com/bemade/bemade-addons/tree/18.0/recursive_list_view),
developed by **Marc Durepos of Bemade Inc.** (© 2023 Bemade Inc.).

The original source is licensed under the **GNU Lesser General Public
License, version 3 (LGPL-3.0)**:
https://www.gnu.org/licenses/lgpl-3.0.html.

The following provenance is preserved:

| File in this module | Upstream source in \`recursive_list_view/static/src/\` | Adaptation |
| --- | --- | --- |
| \`js/list_controller.js\` | \`list_controller.js\` | Dedicated controller class and model-scoped expansion events. |
| \`js/list_renderer.js\` | \`list_renderer.js\` | Dedicated renderer; category child count drives expansion controls. |
| \`js/relational_model.js\` | \`relational_model.js\` | Dedicated model; lazy, paginated children and no \`parent.field.service\` dependency. |
| \`xml/recursive_tree_templates.xml\` | \`recursive_tree_templates.xml\` | Dedicated primary-inheritance templates rather than global extensions. |
| \`css/tree_recursive_styles.css\` | \`tree_recursive_styles.css\` | Scoped CSS and adjusted indentation/control styling. |

Original author and copyright notices are retained in the adapted
files. These acknowledgements identify the **origin of the reused
code**, not authorship of the remaining education classification models,
data, views or documentation. The integration is maintained independently
and is not presented as endorsed by Bemade.

The module's \`__manifest__.py\` declares **AGPL-3** for
\`education_classification\`; the incorporated upstream material retains
the LGPL-3.0 notices and obligations described above.

## Installation and dependencies

- **Odoo version:** 18.0.
- **Manifest dependencies:** \`base\`, \`web\`, \`web_hierarchy\`.
- **No dependency on the separate \`recursive_list_view\` addon.**

Place the repository's \`modules\` directory in the Odoo addons path,
update the Apps list, and install \`education_classification\`. For
installation on an existing database, use your normal Odoo module update
procedure after changing the manifest or assets.

Runtime installation and end-to-end tests of the adapted recursive view
have **not** been performed as part of this documentation change.
