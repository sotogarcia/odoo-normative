# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields, api
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS, AND
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from logging import getLogger


_logger = getLogger(__name__)


class CefrlCertificate(models.Model):
    """Language certificate"""

    _name = "cefrl.certificate"
    _description = "Language certificate"

    _rec_name = "name"
    _order = "group_id ASC, level_id ASC, code ASC"

    code = fields.Char(
        string="Code",
        required=False,
        readonly=False,
        index=True,
        default=None,
        help="Level code",
        size=24,
        translate=False,
    )

    name = fields.Char(
        string="Name",
        required=False,
        readonly=False,
        index=True,
        default=None,
        help="Certificate name",
        size=255,
        translate=True,
    )

    group_id = fields.Many2one(
        string="Group",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="Group to which the certificate belongs",
        comodel_name="cefrl.certificate.group",
        domain=[],
        context={},
        ondelete="cascade",
        auto_join=False,
    )

    language_id = fields.Many2one(
        string="Language",
        help="Related language",
        related="group_id.language_id",
        store=True,
    )

    active = fields.Boolean(
        string="Active",
        help="Check it to show this attempt or uncheck to archivate",
        related="group_id.active",
        store=True,
    )

    level_id = fields.Many2one(
        string="Level",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help=False,
        comodel_name="cefrl.level",
        domain=[],
        context={},
        ondelete="restrict",
        auto_join=False,
    )

    sequence = fields.Integer(
        string="Sequence",
        help="Certificate sequence",
        related="level_id.sequence",
        store=True,
    )

    description = fields.Text(
        string="Description",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Description of the certificate",
        translate=True,
    )

    recognition = fields.Text(
        string="Recognition",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Recognition of certification based on other merits",
        translate=True,
    )

    implied_ids = fields.Many2manyView(
        string="Implied",
        required=False,
        readonly=True,
        index=True,
        default=None,
        help="Implied language certificates",
        comodel_name="cefrl.certificate",
        relation="cefrl_certificate_implied_certificate_rel",
        column1="certificate_id",
        column2="implied_id",
        domain=[],
        context={},
    )

    _sql_constraints = [
        (
            "unique_level_id_by_group",
            "UNIQUE(level_id, group_id)",
            "A certificate with this level already exists in group",
        ),
    ]

    def name_get(self):
        result = []

        for record in self:
            if not record._origin:
                result.append((record.id, _("New certificate group")))
            else:
                lang = record.language_id.name
                if record.name:
                    name = "{} - {}".format(lang, record.name)
                    result.append((record.id, name))
                else:
                    lang = record.language_id.name
                    code = record.code or record.group_id.code
                    level = record.level_id.code

                    name = "{} - {}: {}".format(lang, code, level)

                    result.append((record.id, name))

        return result

    @api.depends("name", "code")
    @api.depends_context("m2m_tags_display_name")
    def _compute_display_name(self):
        """
        Compute `display_name` using the 'm2m_tags_display_name' context flag.

        Modes (case/space-insensitive):
          - 'name' (default): show Name.
          - 'code'          : show Code (fallback to Name if Code is empty).
          - 'both'          : show 'CODE — Name' (skip missing parts).

        Notes:
          - The flag is normalized with `strip().lower()`; any other value
            falls back to 'name'.
          - If `name` is empty (typically on a new record), the label
            defaults to _("New certificate").
        """
        expected = ("name", "code", "both")
        default_label = _("New certificate")

        display = self.env.context.get("m2m_tags_display_name", "name")
        if isinstance(display, str):
            display = display.strip().lower()

        if display not in expected:
            display = "name"

        for record in self:
            record_name = record.name or default_label
            record_code = getattr(record, "code", False)

            items = []

            if record_code and display in ("code", "both"):
                items.append(record_code)

            if not record_code or display != "code":
                items.append(record_name)

            record.display_name = " — ".join(items)

    def _search_display_name(self, operator, value):
        """Custom search for display_name (Odoo 18+).
        Matches on code, name and group_id; honors negative operators.
        """
        if not value:
            return []

        # Build OR over the three fields
        base = [
            "|",
            "|",
            ("code", operator, value),
            ("name", operator, value),
            ("group_id", operator, value),
        ]

        # Turn the OR into a negated AND when operator is negative
        if operator in NEGATIVE_TERM_OPERATORS:
            base = ["&", "!"] + base[1:]

        # Return as a domain; Odoo will AND this with the caller's domain
        return AND([base])
