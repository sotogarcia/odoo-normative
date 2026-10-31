# Odoo Normative

Reusable Odoo modules for managing reference data associated with public standards,
qualifications and regulatory catalogues.

This repository contains **three Odoo 18.0 modules** under [\`modules/\`](modules/).
They are independently installable and are intended to supply reusable reference
models rather than a complete business application.

## Modules

| Module | Purpose | Included content |
| --- | --- | --- |
| [\`cefrl\`](modules/cefrl/) | Common European Framework of Reference for Languages (CEFR). | Language records, level groups (A/B/C), levels (A1–C2), certificate groups, certificates and implied-certificate relationships. |
| [\`driving_licence\`](modules/driving_licence/) | Country-specific driving-licence categories and implied permissions. | A Spanish driving-licence catalogue, reference views and a Settings shortcut. |
| [\`education_classification\`](modules/education_classification/) | Educational classification schemes, editions, categories and correspondence mappings. | ISCED-P 2011, ISCED-A 2011 and ISCED-F 2013, hierarchical items, mapping rules, a hierarchy view and work-in-progress recursive-list components. |

For details of the educational classification models, seed data, access
permissions, source attributions and current frontend status, see the
[Education Classification README](modules/education_classification/README.md).
The driving-licence module has its own
[README](modules/driving_licence/README.md).

## Repository layout

\`\`\`text
odoo-normative/
├── README.md
├── assets/                  Shared non-code resources
├── modules/
│   ├── cefrl/               CEFR catalogue and certificate relations
│   ├── driving_licence/     Driving-licence categories and implications
│   └── education_classification/
│       ├── data/            UNESCO/ISCED scheme, edition and category records
│       ├── i18n/            Translation catalogue
│       ├── models/          Classification and correspondence models
│       ├── security/        Access control
│       ├── static/src/
│       │   ├── css/         Recursive-list styles
│       │   ├── js/          Recursive-list controller, renderer and model
│       │   └── xml/         OWL list templates
│       └── views/           Catalogue, mapping and settings views
└── project/                 Project notes and supporting material
\`\`\`

## Installation

Use **Odoo 18.0** and add this repository's \`modules\` directory to your
Odoo \`addons_path\`, alongside the official Odoo addons. For example:

\`\`\`bash
git clone https://github.com/sotogarcia/odoo-normative.git
# Add /path/to/odoo-normative/modules to addons_path in your Odoo configuration.
\`\`\`

Restart Odoo, update the Apps list (remove the default *Apps* filter if
needed), and install the desired module by its technical name.

Dependencies differ by module:

- \`cefrl\`: \`base\`, \`base_setup\`, \`base_field_m2m_view\` (the last
  dependency must be available in your addons path).
- \`driving_licence\`: \`base\`, \`base_setup\`.
- \`education_classification\`: \`base\`, \`web\`, \`web_hierarchy\`.
  The hierarchy component is part of Odoo 18. The separate Bemade
  \`recursive_list_view\` addon is **not required**.

For \`education_classification\`, the recursive-list code is included in
the asset bundle, but the dedicated list view is **not yet registered or
activated**. Its presence should not be interpreted as a completed
expandable-list feature.

## Third-party code and acknowledgements

The educational-classification recursive-list frontend incorporates
adapted components from **\`recursive_list_view\` for Odoo 18**, created
by **Marc Durepos / Bemade Inc.**:

- Upstream: https://github.com/bemade/bemade-addons/tree/18.0/recursive_list_view
- Original copyright: © 2023 Bemade Inc.
- Original source licence: **GNU LGPL v3.0**.

The integration adapts the list controller, list renderer, relational model,
OWL templates and styles, preserving their original attribution. The
detailed file-by-file provenance and adaptation status are documented in
[the module README](modules/education_classification/README.md).

**Bemade is the upstream author of those components, not the author of
the entire \`education_classification\` module.** This work is not
represented as a Bemade or Odoo-endorsed integration.

## Licences

The three module manifests declare **GNU AGPL v3** for their respective
modules. The adapted Bemade components retain the original **GNU LGPL v3**
copyright and licence notices; the module-level AGPL declaration does not
erase third-party authorship or licence obligations.

- AGPL v3: https://www.gnu.org/licenses/agpl-3.0.html
- LGPL v3: https://www.gnu.org/licenses/lgpl-3.0.html

As declared by the repository's earlier README, its own documentation is
made available under [Creative Commons Attribution-NonCommercial-ShareAlike
4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Third-party materials retain their own applicable rights and notices.

## Issues and contributions

Report issues and propose improvements through
[GitHub Issues](https://github.com/sotogarcia/odoo-normative/issues).
When changing incorporated third-party code, retain the upstream source,
copyright and licence notices.
