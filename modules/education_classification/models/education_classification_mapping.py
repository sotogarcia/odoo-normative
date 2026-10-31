###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class EducationClassificationMapping(models.Model):
    """
    Define a correspondence mapping between classification editions.

    Each mapping relates a source edition to a target edition and contains
    rules describing the relationships between their categories.

    Mappings retain their publication source and may supersede previous
    versions without removing historical correspondence data.
    """

    _name = "education.classification.mapping"
    _description = "Education Classification Mapping"

    _rec_name = "name"
    _order = "name, id"
    _rec_names_search = ["name"]  # noqa: RUF012

    name = fields.Char(
        string="Name",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Descriptive name of the correspondence mapping.",
        translate=True,
    )

    description = fields.Text(
        string="Description",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Purpose and scope of the correspondence mapping.",
        translate=True,
    )

    source_edition_id = fields.Many2one(
        string="Source Edition",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Classification edition from which categories are mapped.",
        comodel_name="education.classification.edition",
        domain=[],
        context={},
        ondelete="restrict",
    )

    target_edition_id = fields.Many2one(
        string="Target Edition",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Classification edition to which categories are mapped.",
        comodel_name="education.classification.edition",
        domain="[('id', '!=', source_edition_id)]",
        context={},
        ondelete="restrict",
    )

    publisher_id = fields.Many2one(
        string="Publisher",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Organisation responsible for publishing the correspondence.",
        comodel_name="res.partner",
        domain=[],
        context={},
        ondelete="restrict",
    )

    source_url = fields.Char(
        string="Source URL",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Official URL of the correspondence documentation.",
        translate=False,
    )

    attachment_id = fields.Many2one(
        string="Attachment",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Document containing the original correspondence data.",
        comodel_name="ir.attachment",
        domain=[],
        context={},
        ondelete="restrict",
        auto_join=False,
    )

    source_version = fields.Char(
        string="Source Version",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Version or revision of the source document.",
        translate=False,
    )

    source_checksum = fields.Char(
        string="Source Checksum",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Checksum of the imported source document.",
        translate=False,
        copy=False,
    )

    state = fields.Selection(
        string="State",
        required=True,
        readonly=False,
        index=True,
        default="draft",
        help="Validation status of the correspondence mapping.",
        selection=[
            ("draft", "Draft"),
            ("review", "Under Review"),
            ("validated", "Validated"),
            ("obsolete", "Obsolete"),
        ],
    )

    supersedes_id = fields.Many2one(
        string="Supersedes",
        required=False,
        readonly=False,
        index=True,
        default=None,
        help="Previous correspondence mapping replaced by this version.",
        comodel_name="education.classification.mapping",
        domain=(
            "[('source_edition_id', '=', source_edition_id), "
            "('target_edition_id', '=', target_edition_id), "
            "('id', '!=', id)]"
        ),
        context={},
        ondelete="restrict",
        copy=False,
    )

    rule_ids = fields.One2many(
        string="Rules",
        required=False,
        readonly=False,
        default=None,
        help="Rules defining correspondences between classification categories.",
        comodel_name="education.classification.rule",
        inverse_name="mapping_id",
        domain=[],
        context={},
        auto_join=False,
    )

    @api.constrains("source_edition_id", "target_edition_id")
    def _check_editions(self):
        """
        Validate the classification editions involved in the mapping.

        Source and target editions must be different.
        """

        for record in self:
            if record.source_edition_id == record.target_edition_id:
                raise ValidationError(
                    _(
                        "Source and target classification editions "
                        "must be different."
                    )
                )

    @api.constrains(
        "supersedes_id",
        "source_edition_id",
        "target_edition_id",
    )
    def _check_supersession(self):
        """
        Validate the correspondence mapping supersession chain.

        Superseded mappings must reference the same classification editions.
        Circular references and incompatible successors are not allowed.
        """

        for record in self:
            visited = {record.id}
            previous = record.supersedes_id

            while previous:
                if previous.id in visited:
                    raise ValidationError(
                        _(
                            "Circular references between correspondence "
                            "mappings are not allowed."
                        )
                    )

                if (
                    previous.source_edition_id != record.source_edition_id
                    or previous.target_edition_id != record.target_edition_id
                ):
                    raise ValidationError(
                        _(
                            "Superseded mappings must reference "
                            "the same source and target editions."
                        )
                    )

                visited.add(previous.id)
                previous = previous.supersedes_id

            successors = self.search(
                [
                    ("supersedes_id", "=", record.id),
                ]
            )

            if any(
                successor.source_edition_id != record.source_edition_id
                or successor.target_edition_id != record.target_edition_id
                for successor in successors
            ):
                raise ValidationError(
                    _(
                        "Successor mappings must reference "
                        "the same source and target editions."
                    )
                )
