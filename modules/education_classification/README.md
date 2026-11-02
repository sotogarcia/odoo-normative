# Education Classification — Odoo 18

`education_classification` provides reusable models and initial reference
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
| `education.classification.scheme` | Identifies a classification system, dimension (programmes, attainment or fields), geographical scope and responsible authority. |
| `education.classification.edition` | Maintains versions of a scheme, publication/validity metadata, a previous edition and publication status. |
| `education.classification.item` | Holds the official category code/name, edition, parent/children and structural sequence. |
| `education.classification.mapping` | Defines a mapping between two editions, with publisher, source, version/checksum, attachment, status and supersession. |
| `education.classification.rule` | Describes a simple, composite, conditional or unmatched correspondence, including its semantic relationship and review status. |
| `education.classification.rule.line` | Associates source/target categories with a rule. |

For categories, the model uses `parent_id`, `child_ids`, stored
`parent_path`, calculated `level`, stored `sequence_path` and
`child_count`. The hierarchy has no fixed maximum depth at the model
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

Seed files are stored under `data/` and include stable Odoo XML IDs,
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
`web_hierarchy` addon. The category action exposes
`list,form,hierarchy`, uses an empty search domain and groups categories by
edition by default. A root-only search filter remains available, but it is
not imposed on every query.

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

## Recursive list view (Odoo 18)

This module includes an **adapted recursive list frontend** based on
[**`recursive_list_view`**](https://github.com/bemade/bemade-addons/tree/18.0/recursive_list_view),
originally developed by **Marc Durepos (Bemade Inc.)**, © 2023 Bemade Inc.,
under **LGPL-3.0**. See [Origin and licence](#origin-of-the-adapted-recursive-list-code)
below for file-by-file attribution. The adaptation displays hierarchical
categories in a single expandable table without patching Odoo's global
list-view components.

The following source files are present:

```text
static/src/
├── css/
│   └── tree_recursive_styles.css
├── js/
│   ├── list_controller.js
│   ├── list_renderer.js
│   ├── recursive_list_view.js
│   └── relational_model.js
└── xml/
    └── recursive_tree_templates.xml
```

The JavaScript files export dedicated controller, renderer and model
classes rather than globally patching Odoo's corresponding prototypes.
The XML contains primary-inheritance OWL templates scoped to the custom
renderer, and the CSS supplies the expansion-column styling and indentation
rules for arbitrary hierarchy depths using a CSS custom property.

**Status: registered and activated in the classification-item list.**
The dedicated view `education_classification_recursive_list` is enabled
through `js_class`; it is separate from the `hierarchy` view supplied by
`web_hierarchy`.

### Capabilities

- **Expand and collapse any depth:** render matching parent/child records
  recursively in the same list, with depth-based indentation and accessible
  expanded/busy indicators. Children are fetched on demand, in batches of
  200, rather than loading every child row for display at once.
- **Respect searches and filters:** the active domain and context define the
  eligible records. The result is rendered as a forest: a matching record
  whose parent does not match becomes a *visual root*, and expansion shows
  only matching descendants. Filters are not silently replaced with
  `parent_id = False`.
- **Paginate visual roots:** list and compatible group pagers count the
  visible forest roots, not all matching descendants. Domain-wide selection
  can still account for the full matching set.
- **Work with compatible groupings:** grouping by `edition_id` preserves
  recursive expansion inside edition groups. Grouping by `parent_id` or
  `level` falls back to Odoo's standard flat grouped list; it does not
  display children beneath an incompatible group header.
- **Select and act on descendants:** individual checkboxes, Shift selection,
  select-all on the visible page, domain-wide selection (including loaded
  or folded descendants), deselection and mass actions include descendant
  records as appropriate.
- **Open, edit and delete:** clicking a displayed descendant opens its
  record with navigation IDs in displayed order. Standard save and
  deletion/confirmation flows remain available; canceling deletion must
  leave records intact. Inline editing is subject to Odoo's normal list
  configuration and field permissions.
- **Use standard list controls:** optional columns, filters, grouping and
  the list action controls remain based on Odoo 18's native list view.
  The expander column also works in layouts without record selectors.

The recursive `list` view is **not** Odoo's separate `hierarchy` view:
the former displays expandable table rows; the latter uses `web_hierarchy`.

### Enable it in another view of the same model

The frontend is registered in
`static/src/js/recursive_list_view.js` under the name
`education_classification_recursive_list`. Its JavaScript, OWL templates
and CSS are included in `web.assets_backend` by this module's
`__manifest__.py`.

To reuse it in a **different list view of `education.classification.item`**:

1. Ensure `education_classification` is installed. If the view belongs to a
   separate addon, add `education_classification` to that addon's
   `depends` in `__manifest__.py`.
2. Add `js_class="education_classification_recursive_list"` to the
   `<list>` element of the desired view (not to its form or hierarchy
   view). For example, in that addon's view XML:

   ```xml
   <record id="view_classification_item_recursive_example" model="ir.ui.view">
       <field name="name">education.classification.item.recursive.example</field>
       <field name="model">education.classification.item</field>
       <field name="arch" type="xml">
           <list string="Classification Items"
                 js_class="education_classification_recursive_list"
                 default_order="edition_id,sequence_path,sequence,id">
               <field name="code"/>
               <field name="name"/>
               <field name="edition_id"/>
               <field name="parent_id" optional="hide"/>
               <field name="child_count" readonly="1" optional="hide"/>
           </list>
       </field>
   </record>
   ```

3. Associate that list view with the required `ir.actions.act_window`
   (for example, through its `view_id` or `ir.actions.act_window.view`
   entries). Merely creating an additional `ir.ui.view` does not guarantee
   that an existing action will select it. Update the addon so Odoo loads
   the view definition.

The module's working example is the `<list>` of
`view_edication_classification_item_list` in
`views/education_classification_item_view.xml`. You can use other
columns, filters and actions; the important parts are the list's
`js_class` and the model's hierarchical fields. There is **no need**
to install the original Bemade addon. Unlike that upstream addon, which
documents `recursive="1"`, this local Odoo 18 adaptation activates the
feature with **`js_class`**.

### Reuse with a different model: limitations

**Adding `js_class` alone is not sufficient for arbitrary models.**
The current implementation is specialised for
`education.classification.item`:

- `static/src/js/relational_model.js` explicitly expects
  `parent_id` (a self-referencing `Many2one`) and `child_count`, uses
  them to project the filtered forest and fetch children, and pages
  child reads in groups of 200.
- `static/src/js/relational_model.js`, in
  `setup()`/`canExpandRecursively()`, treats only `edition_id` grouping
  as compatible with recursion. This rule is specific to classifications;
  other models may need different compatible grouping fields.
- The record hierarchy, field availability, access rights and active
  domain must remain consistent. Large result sets require particular
  care: `_buildRecursiveIndex()` reads **all matching record IDs and
  parent IDs** (in batches), even when only a small page of visual roots
  is shown. This can be expensive for very large datasets.

Reusing the frontend for another hierarchical model therefore requires
adapting/parameterising these assumptions, choosing the correct
grouping rules and adding model-specific HOOT and UI tests. It is **not**
currently a drop-in general-purpose tree widget.

### Tests and verification

The HOOT test bundle is
`static/tests/recursive_list.test.js`; run it on Odoo 18 at:

```text
/web/tests?filter=education_classification
```

The **40 HOOT tests passed in a local Odoo 18 execution reported on
2 November 2026**. They exercise expansion, pagination, filters,
groupings, selection, navigation, deletion/cancelation and styling.
This is not a claim of exhaustive manual integration testing.
In particular, validate the intended action and a Many2one
**Search More** dialog with the actual target database, including
groupings, saved filters and access permissions.

## Origin of the adapted recursive-list code

The recursive frontend is **based on** the open-source addon
[`recursive_list_view` (branch 18.0)](https://github.com/bemade/bemade-addons/tree/18.0/recursive_list_view),
developed by **Marc Durepos of Bemade Inc.** (© 2023 Bemade Inc.).

The original source is licensed under the **GNU Lesser General Public
License, version 3 (LGPL-3.0)**:
https://www.gnu.org/licenses/lgpl-3.0.html.

The following provenance is preserved:

| File in this module | Upstream source in `recursive_list_view/static/src/` | Adaptation |
| --- | --- | --- |
| `js/list_controller.js` | `list_controller.js` | Dedicated controller class and model-scoped expansion events. |
| `js/list_renderer.js` | `list_renderer.js` | Dedicated renderer; category child count drives expansion controls. |
| `js/relational_model.js` | `relational_model.js` | Dedicated model; lazy, paginated children and no `parent.field.service` dependency. |
| `xml/recursive_tree_templates.xml` | `recursive_tree_templates.xml` | Dedicated primary-inheritance templates rather than global extensions. |
| `css/tree_recursive_styles.css` | `tree_recursive_styles.css` | Scoped CSS and adjusted indentation/control styling. |

Original author and copyright notices are retained in the adapted
files. These acknowledgements identify the **origin of the reused
code**, not authorship of the remaining education classification models,
data, views or documentation. The integration is maintained independently
and is not presented as endorsed by Bemade.

The module's `__manifest__.py` declares **AGPL-3** for
`education_classification`; the incorporated upstream material retains
the LGPL-3.0 notices and obligations described above.

## Installation and dependencies

- **Odoo version:** 18.0.
- **Manifest dependencies:** `base`, `web`, `web_hierarchy`.
- **No dependency on the separate `recursive_list_view` addon.**

Place the repository's `modules` directory in the Odoo addons path,
update the Apps list, and install `education_classification`. For
installation on an existing database, use your normal Odoo module update
procedure after changing the manifest or assets.

The local HOOT result above is distinct from end-to-end verification
of every action, access profile and Many2one dialog. Review the
[Tests and verification](#tests-and-verification) section when extending
the frontend or deploying it in another context.
