###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class EducationClassificationItem(models.Model):
    """
    Define a category within an educational classification edition.

    Each item has a unique code within its edition and may belong to a
    hierarchical structure of parent and child categories.

    Hierarchy levels and parent paths are managed automatically.
    Categories from different editions cannot share parent-child
    relationships.
    """

    _name = "education.classification.item"
    _description = "Education Classification Item"

    _rec_name = "name"
    _order = "edition_id, sequence_path, sequence, id"
    _rec_names_search = ["name", "code"]  # noqa: RUF012

    _parent_name = "parent_id"
    _parent_store = True

    code = fields.Char(
        string="Code",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Official category code within the classification edition.",
        translate=False,
    )

    name = fields.Char(
        string="Name",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Official name of the classification category.",
        translate=True,
    )

    description = fields.Text(
        string="Description",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Definition and explanatory notes for this category.",
        translate=True,
    )

    parent_id = fields.Many2one(
        string="Parent",
        required=False,
        readonly=False,
        index=True,
        default=None,
        help="Parent category within the same classification edition.",
        comodel_name="education.classification.item",
        domain="[('edition_id', '=', edition_id), ('id', '!=', id)]",
        context={},
        ondelete="restrict",
    )

    parent_path = fields.Char(
        string="Parent Path",
        required=False,
        readonly=True,
        index=True,
        default=False,
        help="Technical path used for hierarchical searches.",
        copy=False,
    )

    sequence_path = fields.Char(
        string="Sequence Path",
        compute="_compute_sequence_path",
        store=True,
        recursive=True,
        index=True,
        copy=False,
    )

    @api.depends(
        "sequence",
        "code",
        "parent_id",
        "parent_id.sequence_path",
    )
    def _compute_sequence_path(self):
        for record in self:
            # Normalizar el entero para mantener el orden,
            # incluso con secuencias negativas.
            sequence = record.sequence + 2**31

            segment = f"{sequence:010d}:{record.code or ''}/"

            if record.parent_id:
                record.sequence_path = (
                    record.parent_id.sequence_path or ""
                ) + segment
            else:
                record.sequence_path = segment

    edition_id = fields.Many2one(
        string="Edition",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Classification edition to which this category belongs.",
        comodel_name="education.classification.edition",
        domain=[],
        context={},
        ondelete="restrict",
    )

    scheme_id = fields.Many2one(
        comodel_name="education.classification.scheme",
        string="Scheme",
        related="edition_id.scheme_id",
        store=True,
        precompute=True,
        readonly=True,
        index=True,
    )

    dimension = fields.Selection(
        string="Dimension",
        required=True,
        help="Educational aspect classified: programmes, attainment, or fields.",
        related="edition_id.scheme_id.dimension",
        store=True,
        precompute=True,
        readonly=True,
        index=True,
    )

    level = fields.Integer(
        string="Hierarchy Level",
        required=True,
        readonly=True,
        index=True,
        compute="_compute_level",
        store=True,
        recursive=True,
        precompute=True,
        help="Depth in the classification hierarchy, starting at zero.",
    )

    sequence = fields.Integer(
        string="Sequence",
        required=True,
        readonly=False,
        index=True,
        default=0,
        help="Display order of categories within the classification.",
    )

    external_url = fields.Char(
        string="External URL",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Official reference URL for this category.",
        translate=False,
    )

    active = fields.Boolean(
        string="Active",
        required=False,
        readonly=False,
        index=True,
        default=True,
        help="Inactive categories are hidden but retained for historical use.",
    )

    child_ids = fields.One2many(
        string="Children",
        required=False,
        readonly=False,
        default=None,
        help="Categories directly subordinate to this category.",
        comodel_name="education.classification.item",
        inverse_name="parent_id",
        domain=[],
        context={},
        auto_join=False,
    )

    child_count = fields.Integer(
        string="Child count",
        required=True,
        readonly=True,
        index=False,
        default=0,
        help="Total number of child items related to this item.",
        compute="_compute_child_count",
    )

    @api.depends("child_ids")
    def _compute_child_count(self):
        for record in self:
            record.child_count = len(record.child_ids)

    _sql_constraints = [  # noqa: RUF012
        (
            "edition_code_unique",
            "UNIQUE(edition_id, code)",
            "The category code must be unique within its edition.",
        ),
    ]

    @api.depends("parent_id", "parent_id.level")
    def _compute_level(self):
        """
        Compute the hierarchical depth of each category.

        Root categories have level zero. Each child has a level one
        greater than its parent.
        """

        for record in self:
            record.level = (
                record.parent_id.level + 1 if record.parent_id else 0
            )

    @api.constrains("parent_id", "edition_id")
    def _check_hierarchy(self):
        """
        Validate the hierarchical structure of classification categories.

        Circular references are forbidden. Parents and children must
        belong to the same edition, including archived categories.
        """

        if self._has_cycle():
            raise ValidationError(
                _("Circular category relationships are not allowed.")
            )

        for record in self:
            if (
                record.parent_id
                and record.parent_id.edition_id != record.edition_id
            ):
                raise ValidationError(
                    _(
                        "Parent and child categories must belong "
                        "to the same classification edition."
                    )
                )

            if any(
                child.edition_id != record.edition_id
                for child in record.with_context(active_test=False).child_ids
            ):
                raise ValidationError(
                    _(
                        "All child categories must belong "
                        "to the same classification edition."
                    )
                )

    display_name = fields.Char(
        string="Display Name",
        automatic=True,
        compute="_compute_display_name",
        search="_search_display_name",
        recursive=True,
    )

    @api.depends("name", "parent_id", "parent_id.display_name")
    @api.depends_context("lang")
    def _compute_display_name(self):
        """Display the full classification hierarchy."""

        for record in self:
            if record.parent_id:
                record.display_name = (
                    f"{record.parent_id.display_name} / {record.name}"
                )
            else:
                record.display_name = record.name or ""
