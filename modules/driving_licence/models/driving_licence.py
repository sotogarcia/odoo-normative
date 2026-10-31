###############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2015  Jorge Soto Garcia
#
#    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#
###############################################################################

from odoo import api, fields, models, _


class DrivingLicence(models.Model):
    """Country-specific driving licence categories."""

    _name = "driving.licence"
    _description = "Driving licence"
    _rec_name = "name"
    _order = "country_id ASC, sequence ASC, name ASC"

    name = fields.Char(
        string="Name",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Official category of the driving licence.",
        size=50,
        translate=True,
    )

    country_id = fields.Many2one(
        string="Country",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Country that has granted the licence.",
        comodel_name="res.country",
        domain=[],
        context={},
        ondelete="cascade",
        auto_join=False,
    )

    sequence = fields.Integer(
        string="Sequence",
        required=False,
        readonly=False,
        index=False,
        default=0,
        help="Driving licence sequence.",
    )

    active = fields.Boolean(
        string="Active",
        required=False,
        readonly=False,
        index=True,
        default=True,
        help="Uncheck to archive the driving licence.",
    )

    description = fields.Text(
        string="Description",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Description of the driving licence.",
        translate=True,
    )

    implied_ids = fields.Many2many(
        string="Implied",
        required=False,
        readonly=False,
        index=True,
        default=None,
        help="Other licences that are implied by this licence.",
        comodel_name="driving.licence",
        relation="driving_licence_implied_rel",
        column1="licence_id",
        column2="implied_id",
        domain="[('id', '!=', id)]",
        context={},
    )

    implied_count = fields.Integer(
        string="Implied count",
        required=False,
        readonly=True,
        index=False,
        help="Number of implied licences.",
        compute="_compute_implied_count",
    )

    match_country = fields.Boolean(
        string="Match country",
        required=False,
        readonly=True,
        index=False,
        help="Whether the licence belongs to the current company's country.",
        compute="_compute_match_country",
        search="_search_match_country",
    )

    _sql_constraints = [
        (
            "unique_name_by_country",
            "UNIQUE(country_id, name)",
            "There is already a licence with that name for this country.",
        ),
    ]

    @api.depends("name", "country_id.name")
    def _compute_display_name(self):
        for record in self:
            if record.country_id:
                record.display_name = (
                    f"{record.country_id.name} - {record.name or ''}"
                )
            else:
                record.display_name = record.name or ""

    @api.depends("implied_ids")
    def _compute_implied_count(self):
        for record in self:
            record.implied_count = len(record.implied_ids)

    @api.depends("country_id")
    @api.depends_context("company")
    def _compute_match_country(self):
        country = self.env.company.country_id
        for record in self:
            record.match_country = bool(
                country and record.country_id == country
            )

    @api.model
    def _search_match_country(self, operator, value):
        if operator not in ("=", "!="):
            raise NotImplementedError(
                _("Unsupported match country search operator: %s") % operator
            )

        country = self.env.company.country_id
        if not country:
            return [("id", "=", 0)]

        matches = bool(value)
        if operator == "!=":
            matches = not matches

        return [
            ("country_id", "=" if matches else "!=", country.id)
        ]
