# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger


_logger = getLogger(__name__)


class CefrlLevelGroup(models.Model):
    """ Main classification
    """

    _name = 'cefrl.level.group'
    _description = u'CEFRL - Level group'

    _rec_name = 'code'
    _order = 'sequence ASC, code ASC'

    code = fields.Char(
        string='Code',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='Level group code',
        size=2,
        translate=False
    )

    name = fields.Char(
        string='Name',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='Level group name',
        size=24,
        translate=True
    )

    sequence = fields.Integer(
        string='Sequence',
        required=True,
        readonly=False,
        index=False,
        default=1,
        help='Level group sequence'
    )

    active = fields.Boolean(
        string='Active',
        required=False,
        readonly=False,
        index=True,
        default=True,
        help='Check it to show this attempt or uncheck to archivate'
    )

    description = fields.Text(
        string='Description',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Description of the group level',
        translate=True
    )

    level_ids = fields.One2many(
        string='Levels',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='List of levels in this group',
        comodel_name='cefrl.level',
        inverse_name='group_id',
        domain=[],
        context={},
        auto_join=False,
        limit=None
    )

    level_count = fields.Integer(
        string='Level count',
        required=False,
        readonly=True,
        index=False,
        default=0,
        help='Number of levels in this group',
        compute='_compute_level_count'
    )

    @api.depends('level_ids')
    def _compute_level_count(self):
        for record in self:
            record.level_count = len(record.level_ids)

    _sql_constraints = [
        (
            'unique_code',
            'UNIQUE(code)',
            _('A level group with this code already exists')
        ),
        (
            'unique_name',
            'UNIQUE(name)',
            _('A level group with this name already exists')
        ),
    ]

    def name_get(self):
        result = []

        for record in self:
            if record._origin:
                name = '{} ({})'.format(record.code, record.name)
                result.append((record.id, name))
            else:
                result.append((record.id, _('New certificate group')))

        return result
