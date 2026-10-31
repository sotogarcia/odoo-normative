###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class EducationClassificationScheme(models.Model):
    """
    Define an educational classification scheme independently of its editions.

    A scheme identifies a classification system, its educational dimension,
    geographical scope, and responsible authority.

    International schemes provide common reference classifications, while
    national schemes adapt educational classifications to specific countries.

    Editions, classification items, and mappings are managed separately.
    """

    _name = "education.classification.scheme"
    _description = "Education Classification Scheme"

    _rec_name = "name"
    _order = "name, id"
    _rec_names_search = ["name", "code"]  # noqa: RUF012

    code = fields.Char(
        string="Code",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Unique scheme identifier (e.g., ISCED-P or CNED-A).",
        translate=False,
    )

    name = fields.Char(
        string="Name",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Official name of the classification scheme.",
        translate=True,
    )

    description = fields.Text(
        string="Description",
        required=False,
        readonly=False,
        default=None,
        help="Purpose and scope of the classification scheme.",
        translate=True,
    )

    active = fields.Boolean(
        string="Active",
        required=False,
        readonly=False,
        index=True,
        default=True,
        help="Inactive schemes are hidden but retained for historical use.",
    )

    dimension = fields.Selection(
        string="Dimension",
        required=True,
        readonly=False,
        index=True,
        default=False,
        help="Educational aspect classified: programmes, attainment, or fields.",
        selection=[
            ("p", "Educational Programmes"),
            ("a", "Educational Attainment"),
            ("f", "Fields of Education and Training"),
        ],
    )

    scope = fields.Selection(
        string="Scope",
        required=True,
        readonly=False,
        index=True,
        default=False,
        help="Geographical scope of the classification scheme.",
        selection=[
            ("international", "International"),
            ("national", "National"),
            ("other", "Other"),
        ],
    )

    country_id = fields.Many2one(
        string="Country",
        required=False,
        readonly=False,
        index=True,
        default=None,
        help="Country associated with the scheme, when applicable.",
        comodel_name="res.country",
        domain=[],
        context={},
        ondelete="restrict",
    )

    geographical_area = fields.Char(
        string="Geographical Area",
        required=False,
        readonly=False,
        index=True,
        default=None,
        help="Geographical area covered by the classification scheme.",
        translate=True,
    )

    authority_id = fields.Many2one(
        string="Authority",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Organisation responsible for the classification scheme.",
        comodel_name="res.partner",
        domain=[],
        context={},
        ondelete="restrict",
    )

    website = fields.Char(
        string="Website",
        related="authority_id.website",
        help="Official website of the responsible organisation.",
    )

    edition_ids = fields.One2many(
        string="Editions",
        required=False,
        readonly=False,
        default=None,
        help="Editions belonging to this classification scheme.",
        comodel_name="education.classification.edition",
        inverse_name="scheme_id",
        domain=[],
        context={},
        auto_join=False,
    )

    edition_count = fields.Integer(
        string="Edition count",
        required=True,
        readonly=True,
        index=False,
        default=0,
        help="Total number of classification editions related to the schema.",
        compute="_compute_edition_count",
    )

    @api.depends("edition_ids")
    def _compute_edition_count(self):
        for record in self:
            record.edition_count = len(record.edition_ids)

    _sql_constraints = [  # noqa: RUF012
        (
            "code_unique",
            "UNIQUE(code)",
            "The classification scheme code must be unique.",
        ),
    ]

    @api.constrains("scope", "country_id", "geographical_area")
    def _check_geographical_scope(self):
        """
        Validate the geographical scope of the classification scheme.

        International schemes have no geographical assignment.
        National schemes require a country.
        Other schemes require a geographical area and may specify a country.
        """

        for record in self:
            if record.scope == "international" and (
                record.country_id or record.geographical_area
            ):
                raise ValidationError(
                    _(
                        "International classification schemes cannot "
                        "have a specific geographical assignment."
                    )
                )

            if record.scope == "national" and not record.country_id:
                raise ValidationError(
                    _(
                        "A country must be specified for national "
                        "classification schemes."
                    )
                )

            if (
                record.scope == "other"
                and not (record.geographical_area or "").strip()
            ):
                raise ValidationError(
                    _(
                        "A geographical area must be specified "
                        "for other classification schemes."
                    )
                )
