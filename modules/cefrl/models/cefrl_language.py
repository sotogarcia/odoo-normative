# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields
from odoo.tools.translate import _
from logging import getLogger


_logger = getLogger(__name__)


class CefrlLanguage(models.Model):
    """Language"""

    _name = "cefrl.language"
    _description = "CEFRL - language"

    _rec_name = "name"
    _order = "name ASC"

    name = fields.Char(
        string="Name",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help=False,
        size=255,
        translate=True,
    )

    code = fields.Char(
        string="Code",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="ISO 639-1 language code",
        size=2,
        translate=False,
    )

    dialect = fields.Char(
        string="Dialect",
        required=True,
        readonly=False,
        index=True,
        default=None,
        help="ISO 639-6 language code",
        size=4,
        translate=False,
    )

    parent_id = fields.Many2one(
        string="Parent",
        required=False,
        readonly=False,
        index=True,
        default=None,
        help="Parent language",
        comodel_name="cefrl.language",
        domain=[],
        context={},
        ondelete="restrict",
        auto_join=False,
    )

    active = fields.Boolean(
        string="Active",
        required=False,
        readonly=False,
        index=True,
        default=True,
        help="Check it to show this attempt or uncheck to archivate",
    )

    description = fields.Text(
        string="About",
        required=False,
        readonly=False,
        index=False,
        default=None,
        help="Something about this language",
        translate=True,
    )

    _sql_constraints = [
        (
            "unique_code_dialect",
            "UNIQUE(code, dialect)",
            "A language with this code or dialect already exists",
        ),
        (
            "unique_name",
            "UNIQUE(name)",
            "A language with this name already exists",
        ),
    ]

    def name_get(self):
        result = []

        for record in self:
            if record._origin:
                code = record.dialect if record.parent_id else record.code
                name = "{} ({})".format(record.name, code)
                result.append((record.id, name))
            else:
                result.append((record.id, _("New certificate group")))

        return result
