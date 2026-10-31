###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class EducationClassificationEdition(models.Model):
    """
    Define an edition of an educational classification scheme.

    Each edition belongs to a classification scheme and contains its own
    categories, validity period, and official documentation.

    Editions may reference a previous edition to preserve their historical
    sequence and support correspondence mappings between versions.
    """

    _name = "education.classification.edition"
    _description = "Education Classification Edition"

    _rec_name = "name"
    _order = "name, id"
    _rec_names_search = ["name", "version"]  # noqa: RUF012

    name = fields.Char(
        string="Name",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Descriptive name of the classification edition.",
        translate=True,
    )

    version = fields.Char(
        string="Version",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Official edition identifier (e.g., 2011, 2013, or 2014).",
        translate=False,
    )

    active = fields.Boolean(
        string="Active",
        required=False,
        readonly=False,
        index=True,
        default=True,
        help="Inactive editions are hidden but remain available for historical use.",
    )

    scheme_id = fields.Many2one(
        string="Scheme",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Classification scheme to which this edition belongs.",
        comodel_name="education.classification.scheme",
        domain=[],
        context={},
        ondelete="restrict",
    )

    publication_date = fields.Date(
        string="Publication Date",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Date on which the edition was officially published.",
    )

    valid_from = fields.Date(
        string="Valid From",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Date from which the edition became applicable.",
    )

    valid_to = fields.Date(
        string="Valid To",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Last date of applicability, if known.",
    )

    previous_edition_id = fields.Many2one(
        string="Previous Edition",
        required=False,
        readonly=False,
        index=True,
        default=None,
        help="Previous edition of the same classification scheme.",
        comodel_name="education.classification.edition",
        domain="[('scheme_id', '=', scheme_id), ('id', '!=', id)]",
        context={},
        ondelete="restrict",
    )

    source_url = fields.Char(
        string="Source URL",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Official documentation URL for this edition.",
        translate=False,
    )

    state = fields.Selection(
        string="State",
        required=True,
        readonly=False,
        index=True,
        default="draft",
        help="Publication status of the classification edition.",
        selection=[
            ("draft", "Draft"),
            ("published", "Published"),
            ("superseded", "Superseded"),
        ],
    )

    item_ids = fields.One2many(
        string="Items",
        required=False,
        readonly=False,
        default=None,
        help="Classification categories belonging to this edition.",
        comodel_name="education.classification.item",
        inverse_name="edition_id",
        domain=[],
        context={},
        auto_join=False,
    )

    item_count = fields.Integer(
        string="Item count",
        required=True,
        readonly=True,
        index=False,
        default=0,
        help="Total number of classification editions items to the edition.",
        compute="_compute_item_count",
    )

    @api.depends("item_ids")
    def _compute_item_count(self):
        for record in self:
            record.item_count = len(record.item_ids)

    _sql_constraints = [  # noqa: RUF012
        (
            "scheme_version_unique",
            "UNIQUE(scheme_id, version)",
            "The edition version must be unique within its scheme.",
        ),
    ]

    @api.constrains("valid_from", "valid_to")
    def _check_validity_dates(self):
        """
        Validate the applicability period of the edition.

        The end date cannot precede the start date. Missing dates
        are allowed when the official applicability period is unknown.
        """

        for record in self:
            if (
                record.valid_from
                and record.valid_to
                and record.valid_to < record.valid_from
            ):
                raise ValidationError(
                    _(
                        "The validity end date cannot be earlier "
                        "than the start date."
                    )
                )

    @api.constrains("scheme_id", "previous_edition_id")
    def _check_previous_edition(self):
        """
        Validate the relationship with previous editions.

        Previous editions must belong to the same classification scheme.
        Self-references and circular edition chains are not allowed.
        """

        for record in self:
            visited = {record.id}
            previous = record.previous_edition_id

            while previous:
                if previous.scheme_id != record.scheme_id:
                    raise ValidationError(
                        _(
                            "The previous edition must belong "
                            "to the same classification scheme."
                        )
                    )

                if previous.id in visited:
                    raise ValidationError(
                        _(
                            "Circular references between classification "
                            "editions are not allowed."
                        )
                    )

                visited.add(previous.id)
                previous = previous.previous_edition_id
