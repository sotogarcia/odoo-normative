# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields, api
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS, AND
from odoo.tools.translate import _
from logging import getLogger


_logger = getLogger(__name__)


class CefrlCertificate(models.Model):
    """ Language certificate
    """

    _name = 'cefrl.certificate'
    _description = u'Language certificate'

    _rec_name = 'name'
    _order = 'group_id ASC, level_id ASC, code ASC'

    code = fields.Char(
        string='Code',
        required=False,
        readonly=False,
        index=True,
        default=None,
        help='Level code',
        size=24,
        translate=False
    )

    name = fields.Char(
        string='Name',
        required=False,
        readonly=False,
        index=True,
        default=None,
        help='Certificate name',
        size=255,
        translate=True
    )

    group_id = fields.Many2one(
        string='Group',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='Group to which the certificate belongs',
        comodel_name='cefrl.certificate.group',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    language_id = fields.Many2one(
        string='Language',
        help='Related language',
        related='group_id.language_id',
        store=True
    )

    active = fields.Boolean(
        string='Active',
        help='Check it to show this attempt or uncheck to archivate',
        related='group_id.active',
        store=True
    )

    level_id = fields.Many2one(
        string='Level',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help=False,
        comodel_name='cefrl.level',
        domain=[],
        context={},
        ondelete='restrict',
        auto_join=False
    )

    sequence = fields.Integer(
        string='Sequence',
        help='Certificate sequence',
        related="level_id.sequence",
        store=True
    )

    description = fields.Text(
        string='Description',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Description of the certificate',
        translate=True
    )

    recognition = fields.Text(
        string='Recognition',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help='Recognition of certification based on other merits',
        translate=True
    )

    implied_ids = fields.Many2manyView(
        string='Implied',
        required=False,
        readonly=True,
        index=True,
        default=None,
        help='Implied language certificates',
        comodel_name='cefrl.certificate',
        relation='cefrl_certificate_implied_certificate_rel',
        column1='certificate_id',
        column2='implied_id',
        domain=[],
        context={},
        limit=None
    )

    _sql_constraints = [
        # This only works in Postgresql 15 or later
        # (
        #     'unique_name_by_group',
        #     'UNIQUE NULLS NOT DISTINCT (name, group_id)',
        #     _('A certificate with this name already exists in group')
        # ),
        # (
        #     'unique_code_by_group',
        #     'UNIQUE NULLS NOT DISTINCT (code, group_id)',
        #     _('A certificate with this code already exists in group')
        # ),
        (
            'unique_level_id_by_group',
            'UNIQUE(level_id, group_id)',
            _('A certificate with this level already exists in group')
        ),
    ]

    def name_get(self):
        result = []

        for record in self:
            if not record._origin:
                result.append((record.id, _('New certificate group')))
            else:
                lang = record.language_id.name
                if record.name:
                    name = '{} - {}'.format(lang, record.name)
                    result.append((record.id, name))
                else:
                    lang = record.language_id.name
                    code = record.code or record.group_id.code
                    level = record.level_id.code

                    name = '{} - {}: {}'.format(lang, code, level)

                    result.append((record.id, name))

        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100,
                     name_get_uid=None):
        args = args or []
        domain = []

        if name:
            domain = [
                '|',
                '|',
                ('code', operator, name),
                ('name', operator, name),
                ('group_id', operator, name)
            ]
            if operator in NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            domain = AND([domain, args])

        certificate_ids = self._search(domain, limit=limit,
                                       access_rights_uid=name_get_uid)
        certificate_set = self.browse(certificate_ids).with_user(name_get_uid)

        return models.lazy_name_get(certificate_set)
