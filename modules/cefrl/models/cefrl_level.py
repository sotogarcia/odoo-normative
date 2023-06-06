# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields
from odoo.tools.translate import _
from logging import getLogger


_logger = getLogger(__name__)


class CefrlLevel(models.Model):
    """ Secondary classification
    """

    _name = 'cefrl.level'
    _description = u'CEFRL - Level'

    _rec_name = 'code'
    _order = 'sequence ASC, code ASC'

    code = fields.Char(
        string='Code',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='Level code',
        size=2,
        translate=False
    )

    name = fields.Char(
        string='Name',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='Level name',
        size=24,
        translate=True
    )

    sequence = fields.Integer(
        string='Sequence',
        required=True,
        readonly=False,
        index=False,
        default=1,
        help='Level sequence'
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
        help='Description of the level',
        translate=True
    )

    group_id = fields.Many2one(
        string='Group',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='Group to which the level belongs',
        comodel_name='cefrl.level.group',
        domain=[],
        context={},
        ondelete='restrict',
        auto_join=False
    )

    _sql_constraints = [
        (
            'unique_code',
            'UNIQUE(code)',
            _('A level with this code already exists')
        ),
        (
            'unique_name_by_group',
            'UNIQUE(name, group_id)',
            _('A level with this name already exists')
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
