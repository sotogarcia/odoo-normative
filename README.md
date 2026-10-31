# Odoo Normative

Odoo Normative is a collection of reusable reference-data modules for Odoo 18.0.
It brings public classifications and regulated catalogues into Odoo models so
other applications can reuse them without duplicating the underlying records.

## Modules

The repository currently contains three addons in [`modules/`](modules/).
Each addon has its own models, initial data, views and access controls, and
can be installed independently when its dependencies are available.

| Addon | Purpose | Dependencies declared in its manifest |
| --- | --- | --- |
| [`cefrl`](modules/cefrl/) | Common European Framework of Reference for Languages (CEFR): level groups, levels, languages, certificate groups, certificates and implied-certificate relationships. | `base`, `base_setup`, `base_field_m2m_view` |
| [`driving_licence`](modules/driving_licence/) | Country-specific driving licence categories and implied licences; includes the Spanish catalogue. | `base`, `base_setup` |
| [`education_classification`](modules/education_classification/) | Educational classification schemes, editions, hierarchical categories, and rules mapping categories between editions. | `base`, `web_hierarchy` |

All three manifests declare version `18.0.1.0.0` and license `AGPL-3`.
The `base_field_m2m_view` dependency of `cefrl` is **not included** in
this repository and must be supplied separately.

### CEFR for Languages (`cefrl`)

This addon holds reusable CEFR language and qualification reference data.
It includes the A/B/C level groups, A1–C2 levels, languages, certificate groups,
and a registry of certificates with implied-certificate relationships.

The addon includes Spanish translations, security declarations, list and form
views, a Settings integration, and
[migration notes](modules/cefrl/migration.md). Its records are reference data:
installing it does not independently implement an HR or education workflow.

### Driving Licence (`driving_licence`)

This addon defines the `driving.licence` model, country-related licence
categories, and many-to-many relationships between licences implied by a
category. Its initial data include 15 Spanish licence categories.

It includes views, a Settings shortcut, Spanish translations, and a Python test
module. See the [module README](modules/driving_licence/README.md) for its
migration notes, preserved identifiers and testing instructions.

The catalogue records are not a substitute for verifying current national
driving-licence regulations.

### Education Classification (`education_classification`)

This addon provides a generic model for educational classification schemes,
including international and national classifications, successive editions,
hierarchical categories, and correspondence mappings. The six models present
in the repository are:

| Model | Role |
| --- | --- |
| `education.classification.scheme` | Classification identity, educational dimension, geographical scope and publishing authority |
| `education.classification.edition` | Version, publication/validity dates and predecessor edition |
| `education.classification.item` | Edition-specific category with `parent_id`, `child_ids`, `parent_path`, `sequence_path`, hierarchy level and child count |
| `education.classification.mapping` | Correspondence between a source and target edition, provenance, attachments, state and supersession |
| `education.classification.rule` | Mapping rule, including rule type, semantic relationship, conditions and validation |
| `education.classification.rule.line` | Source/target category assignments within a mapping rule |

The bundled UNESCO/UIS reference catalogues are:

- **ISCED-P 2011** — educational programmes.
- **ISCED-A 2011** — educational attainment.
- **ISCED-F 2013** — fields of education and training.

The source URLs for the international catalogues are recorded in the edition
data. The model also accommodates national schemes such as Spain's CNED,
but **this repository does not currently ship CNED category data**.

The addon has an `Education Classification Manager` security group.
The access-control file grants read-only access to internal, portal and public
groups, and create/write/delete permissions to classification managers.
The Settings integration provides shortcuts to schemes, editions, categories,
mappings, rules and rule lines for system administrators.

#### Hierarchical views and implementation status

Category management currently defines a standard Odoo list and form view and
an Odoo 18 `hierarchy` view, supplied by the standard `web_hierarchy` addon.

In addition, the following **adapted recursive-list resources** are included
under `modules/education_classification/static/src/`:

```text
css/
    tree_recursive_styles.css
js/
    list_controller.js
    list_renderer.js
    relational_model.js
xml/
    recursive_tree_templates.xml
```

These are registered as backend assets by the module manifest. They provide
custom controller, renderer and model classes; deferred descendant retrieval;
and dedicated OWL templates and styles for expanding multiple hierarchy levels.

**The recursive list is not yet enabled in the application's category list.**
Its implementation still requires registering a custom view in the Odoo view
registry, binding the dedicated OWL templates to its renderer, and specifying
that view's `js_class` in the relevant list architecture. The resources have
not been verified by a complete Odoo 18 browser/integration test; simply
installing the addon must not be taken as evidence that recursive expansion
already works.

#### Attribution: recursive_list_view by Bemade

The adapted recursive-list resources are based on
[`recursive_list_view` for Odoo 18](https://github.com/bemade/bemade-addons/tree/18.0/recursive_list_view),
originally developed by **Marc Durepos, Bemade Inc.**

- **Original copyright:** Copyright (C) 2023-June Bemade Inc.
- **Original author:** Marc Durepos (Bemade Inc.).
- **Original project:** [bemade/bemade-addons](https://github.com/bemade/bemade-addons/tree/18.0/recursive_list_view).
- **Original license:** [GNU Lesser General Public License v3.0 (LGPL-3.0)](https://www.gnu.org/licenses/lgpl-3.0.html).
- **Local adaptation:** integration into `education_classification` for Odoo
  18, with dedicated classes/templates and changes to how child categories are
  loaded and displayed.

| Local file | Original Bemade file |
| --- | --- |
| `static/src/js/list_controller.js` | `recursive_list_view/static/src/list_controller.js` |
| `static/src/js/list_renderer.js` | `recursive_list_view/static/src/list_renderer.js` |
| `static/src/js/relational_model.js` | `recursive_list_view/static/src/relational_model.js` |
| `static/src/xml/recursive_tree_templates.xml` | `recursive_list_view/static/src/recursive_tree_templates.xml` |
| `static/src/css/tree_recursive_styles.css` | `recursive_list_view/static/src/tree_recursive_styles.css` |

The original authorship and LGPL-3.0 status of the reused code must be
preserved. The remaining addon functionality is distributed under the
`AGPL-3` license declared in its manifest. The integrated implementation
does **not** require installing the upstream `recursive_list_view` addon.

## Repository structure

The top-level directories separate installable addons from supporting assets
and project notes.

```text
odoo-normative/
├── README.md
├── assets/                # Project-level graphics and other resources
├── modules/
│   ├── cefrl/
│   ├── driving_licence/
│   └── education_classification/
└── project/               # Project notes (currently a short README)
```

The `modules/` directory is the one to add to Odoo's addons path.

## Installation

Use an Odoo **18.0** installation and clone the repository:

```bash
git clone https://github.com/sotogarcia/odoo-normative.git
```

Add the cloned `odoo-normative/modules` directory to your Odoo
`addons_path`. Ensure any separately provided dependencies are available,
update the Apps list, and install the desired addon by its technical name:
`cefrl`, `driving_licence`, or `education_classification`.

For `education_classification`, Odoo's `web_hierarchy` addon is required.
For `cefrl`, `base_field_m2m_view` is an additional external dependency.
There is no requirement to install Bemade's `recursive_list_view` module for
the adapted code included in this repository.

## Development and testing

The repository includes a Python test module for `driving_licence`; it does
not currently contain a comparable automated test suite for the recursive
classification list. Code presence and static review should not be confused
with successful Odoo runtime or browser testing.

The modules contain their own reference-data XML, permissions and translations.
When changing published classifications, check both their source references
and backward compatibility with existing XML IDs.

## Licenses and acknowledgements

The three addon manifests declare the
[GNU Affero General Public License v3](https://www.gnu.org/licenses/agpl-3.0.html)
(`AGPL-3`). The adapted Bemade files retain their original attribution and
license notices; see the dedicated acknowledgment above for their source
and LGPL-3.0 license.

The repository's documentation has previously been stated to be licensed
under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0
International license](https://creativecommons.org/licenses/by-nc-sa/4.0/).
This documentation notice does not replace the software license or the
separate attribution applicable to reused code.

The ISCED classification source references identify UNESCO/UIS as the
publisher of the underlying standards; the data models and source citations
do not imply authorship of the standards by this repository.

## Feedback

Report issues or propose improvements through the
[GitHub issue tracker](https://github.com/sotogarcia/odoo-normative/issues).
