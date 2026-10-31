###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class EducationClassificationRule(models.Model):
    """
    Define a correspondence rule between classification categories.

    Each rule belongs to a correspondence mapping and relates source
    and target categories through its component lines.

    Rules may describe simple, composite, conditional, or explicitly
    unmatched correspondences. Semantic relations follow SKOS concepts.

    Draft rules may be incomplete, while validated rules must satisfy
    their structural and semantic requirements.
    """

    _name = "education.classification.rule"
    _description = "Education Classification Mapping Rule"

    _rec_name = "mapping_id"
    _order = "mapping_id, sequence, id"

    mapping_id = fields.Many2one(
        string="Mapping",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Correspondence mapping to which this rule belongs.",
        comodel_name="education.classification.mapping",
        domain=[],
        context={},
        ondelete="restrict",
    )

    sequence = fields.Integer(
        string="Sequence",
        required=True,
        readonly=False,
        index=True,
        default=0,
        help="Display order of rules within the mapping.",
    )

    rule_type = fields.Selection(
        string="Rule Type",
        required=True,
        readonly=False,
        index=True,
        default="simple",
        help="Structure of the correspondence between categories.",
        selection=[
            ("simple", "Simple"),
            ("composite", "Composite"),
            ("conditional", "Conditional"),
            ("no_match", "No Match"),
        ],
    )

    relation_type = fields.Selection(
        string="Relation Type",
        required=False,
        readonly=False,
        index=True,
        default=False,
        help="Semantic relationship between source and target categories.",
        selection=[
            ("exact", "Exact Match"),
            ("close", "Close Match"),
            ("broader", "Broader Match"),
            ("narrower", "Narrower Match"),
            ("related", "Related Match"),
        ],
    )

    condition_description = fields.Text(
        string="Condition Description",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Conditions governing the applicability of this rule.",
        translate=True,
    )

    notes = fields.Text(
        string="Notes",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Additional explanations or observations about the rule.",
        translate=True,
    )

    state = fields.Selection(
        string="State",
        required=True,
        readonly=False,
        index=True,
        default="draft",
        help="Validation status of the correspondence rule.",
        selection=[
            ("draft", "Draft"),
            ("review", "Under Review"),
            ("validated", "Validated"),
            ("obsolete", "Obsolete"),
        ],
    )

    line_ids = fields.One2many(
        string="Lines",
        required=False,
        readonly=False,
        default=None,
        help="Source and target categories involved in this rule.",
        comodel_name="education.classification.rule.line",
        inverse_name="rule_id",
        domain=[],
        context={},
        auto_join=False,
    )

    @api.constrains("rule_type", "relation_type")
    def _check_unmatched_rule_has_no_semantic_relation(self):
        """
        Unmatched rules cannot define a semantic relationship.
        """

        for record in self:
            if record.rule_type == "no_match" and record.relation_type:
                raise ValidationError(
                    _(
                        "Rules without a match cannot define "
                        "a semantic relationship."
                    )
                )

    @api.constrains("state", "rule_type", "relation_type")
    def _check_validated_rule_has_semantic_relation(self):
        """
        Validated matched rules must define a semantic relationship.
        """

        for record in self:
            if (
                record.state == "validated"
                and record.rule_type != "no_match"
                and not record.relation_type
            ):
                raise ValidationError(
                    _(
                        "A semantic relationship is required "
                        "for validated correspondence rules."
                    )
                )

    @api.constrains("state", "rule_type", "condition_description")
    def _check_validated_conditional_rule_has_description(self):
        """
        Validated conditional rules must describe their conditions.
        """

        for record in self:
            if (
                record.state == "validated"
                and record.rule_type == "conditional"
                and not (record.condition_description or "").strip()
            ):
                raise ValidationError(
                    _(
                        "Conditional rules must describe "
                        "their applicability conditions."
                    )
                )

    @api.constrains("state", "rule_type", "line_ids")
    def _check_validated_rule_has_required_lines(self):
        """
        Validate the presence of source and target categories.
        """

        for record in self:
            if record.state != "validated":
                continue

            source_lines, target_lines = record._get_source_and_target_lines()

            if not source_lines:
                raise ValidationError(
                    _(
                        "Validated correspondence rules require "
                        "at least one source category."
                    )
                )

            if record.rule_type == "no_match" and target_lines:
                raise ValidationError(
                    _(
                        "Rules without a match cannot "
                        "contain target categories."
                    )
                )

            if record.rule_type != "no_match" and not target_lines:
                raise ValidationError(
                    _(
                        "Validated correspondence rules require "
                        "at least one target category."
                    )
                )

    @api.constrains("state", "rule_type", "line_ids")
    def _check_validated_simple_rule_cardinality(self):
        """
        Simple rules must have exactly one source and one target.
        """

        for record in self:
            if record.state != "validated" or record.rule_type != "simple":
                continue

            source_lines, target_lines = record._get_source_and_target_lines()

            if len(source_lines) != 1 or len(target_lines) != 1:
                raise ValidationError(
                    _(
                        "Simple correspondence rules require "
                        "exactly one source and one target category."
                    )
                )

    @api.constrains("state", "rule_type", "line_ids")
    def _check_validated_composite_rule_cardinality(self):
        """
        Composite rules must involve multiple categories.
        """

        for record in self:
            if record.state != "validated" or record.rule_type != "composite":
                continue

            source_lines, target_lines = record._get_source_and_target_lines()

            if len(source_lines) == 1 and len(target_lines) == 1:
                raise ValidationError(
                    _(
                        "Composite correspondence rules require "
                        "multiple source or target categories."
                    )
                )

    @api.depends(
        "mapping_id",
        "mapping_id.name",
        "sequence",
        "rule_type",
        "relation_type",
    )
    def _compute_display_name(self):
        """
        Compute a descriptive name for each correspondence rule.

        The display name combines the mapping name, rule sequence,
        structural type, and semantic relationship.
        """

        rule_types = dict(
            self._fields["rule_type"]._description_selection(self.env)
        )
        relation_types = dict(
            self._fields["relation_type"]._description_selection(self.env)
        )

        for record in self:
            if not record.mapping_id:
                record.display_name = _("New mapping rule")
                continue

            parts = [record.mapping_id.display_name]

            if record.sequence:
                parts.append(f"#{record.sequence}")

            if record.rule_type:
                parts.append(
                    rule_types.get(record.rule_type, record.rule_type)
                )

            if record.relation_type:
                parts.append(
                    relation_types.get(
                        record.relation_type,
                        record.relation_type,
                    )
                )

            record.display_name = " - ".join(parts)

    def _get_source_and_target_lines(self):
        """
        Return the source and target lines of the rule.
        """

        self.ensure_one()

        source_lines = self.line_ids.filtered(
            lambda line: line.side == "source"
        )
        target_lines = self.line_ids.filtered(
            lambda line: line.side == "target"
        )

        return source_lines, target_lines
