###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class EducationClassificationRuleLine(models.Model):
    """
    Define a category participating in a correspondence rule.

    Each line identifies a source or target category within the
    classification editions associated with its mapping.

    Rules may contain multiple source and target lines, allowing
    simple, composite, and conditional correspondences.

    Category assignments must remain consistent with their editions.
    """

    _name = "education.classification.rule.line"
    _description = "Education Classification Rule Line"

    _rec_name = "item_id"
    _order = "rule_id, side, sequence, id"

    rule_id = fields.Many2one(
        string="Rule",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Correspondence rule to which this line belongs.",
        comodel_name="education.classification.rule",
        domain=[],
        context={},
        ondelete="restrict",
    )

    item_id = fields.Many2one(
        string="Item",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Classification category participating in the rule.",
        comodel_name="education.classification.item",
        domain=[],
        context={},
        ondelete="restrict",
    )

    side = fields.Selection(
        string="Side",
        required=True,
        readonly=False,
        index=True,
        default=False,
        help="Indicates whether the category is a source or target.",
        selection=[
            ("source", "Source"),
            ("target", "Target"),
        ],
    )

    sequence = fields.Integer(
        string="Sequence",
        required=True,
        readonly=False,
        index=True,
        default=0,
        help="Display order within the rule.",
    )

    _sql_constraints = [  # noqa: RUF012
        (
            "rule_side_item_unique",
            "UNIQUE(rule_id, side, item_id)",
            "The category cannot be repeated on the same side of a rule.",
        ),
    ]

    @api.depends("side", "item_id", "item_id.code", "item_id.name")
    def _compute_display_name(self):
        """
        Display the category code and name with its correspondence side.
        """

        side_labels = dict(
            self._fields["side"]._description_selection(self.env)
        )

        for record in self:
            if not record.item_id:
                record.display_name = _("New rule line")
                continue

            label = side_labels.get(record.side, _("Rule line"))

            record.display_name = (
                f"{label}: " f"{record.item_id.code} - {record.item_id.name}"
            )

    @api.constrains("rule_id", "item_id", "side")
    def _check_source_item_edition(self):
        """
        Source categories must belong to the mapping's source edition.
        """

        for record in self:
            if (
                record.side == "source"
                and record.item_id
                and record.rule_id
                and record.item_id.edition_id
                != record.rule_id.mapping_id.source_edition_id
            ):
                raise ValidationError(
                    _(
                        "Source categories must belong "
                        "to the mapping's source edition."
                    )
                )

    @api.constrains("rule_id", "item_id", "side")
    def _check_target_item_edition(self):
        """
        Target categories must belong to the mapping's target edition.
        """

        for record in self:
            if (
                record.side == "target"
                and record.item_id
                and record.rule_id
                and record.item_id.edition_id
                != record.rule_id.mapping_id.target_edition_id
            ):
                raise ValidationError(
                    _(
                        "Target categories must belong "
                        "to the mapping's target edition."
                    )
                )

    def _validate_affected_rules(self, rules):
        """
        Revalidate the category structure of affected correspondence rules.
        """

        rules._check_validated_rule_has_required_lines()
        rules._check_validated_simple_rule_cardinality()
        rules._check_validated_composite_rule_cardinality()

    @api.model_create_multi
    def create(self, vals_list):
        """
        Create rule lines and validate the affected correspondence rules.
        """

        records = super().create(vals_list)

        records._validate_affected_rules(records.mapped("rule_id"))

        return records

    def write(self, vals):
        """
        Validate both previous and new rules after modifying their lines.
        """

        previous_rules = self.mapped("rule_id")

        result = super().write(vals)

        affected_rules = previous_rules | self.mapped("rule_id")

        self._validate_affected_rules(affected_rules)

        return result

    def unlink(self):
        """
        Validate the remaining structure after deleting rule lines.
        """

        affected_rules = self.mapped("rule_id")

        result = super().unlink()

        self._validate_affected_rules(affected_rules)

        return result
