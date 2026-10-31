# Driving Licence — Odoo 18

Migration of the `driving_licence` module from Odoo 13.0 to Odoo 18.0.

## Preserved data and compatibility

- Technical model: `driving.licence`.
- Existing field names, including `implied_ids`, `match_country` and `implied_count`.
- Many-to-many SQL relation: `driving_licence_implied_rel`.
- Spanish category records and their XML IDs (15 categories).
- Original model access policy: internal users read, Contact Creation group manages.
- XML IDs for views, window action and settings view.

## Odoo 18 changes

- Uses list views (`list`) instead of `tree`.
- Uses `invisible` expressions instead of `attrs`.
- Replaces `name_get` with `_compute_display_name`.
- Uses standard `many2many_tags`; no dependency on `base_field_m2m_view`.
- Settings view uses `app`, `block` and `setting`.
- Archived filter sets `active_test=False`.

## Install and test

The module depends on `base` and `base_setup`. Place `modules` in the
Odoo 18 addons path, update the Apps list, and install `driving_licence`.

To test with a dedicated database:

```sh
odoo-bin -d test_driving_licence_18 -i driving_licence --test-enable --stop-after-init
```

Runtime installation has **not** been executed as part of this migration.
The existing XML data about driving permissions is migrated as-is; it is
not an independent legal review of current Spanish licensing rules.

The SQL uniqueness constraint is retained from Odoo 13.0. Because translated
Char fields are stored differently in Odoo 18, its cross-language uniqueness
semantics should be reviewed separately.
