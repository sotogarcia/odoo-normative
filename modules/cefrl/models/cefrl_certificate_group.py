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


class CefrlCertificateGroup(models.Model):
    """ Language certificate group
    """

    _name = 'cefrl.certificate.group'
    _description = u'Language certificate group'

    _rec_name = 'name'
    _order = 'language_id ASC, code ASC'

    code = fields.Char(
        string='Code',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='Level code',
        size=24,
        translate=False
    )

    name = fields.Char(
        string='Name',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='Certificate name',
        size=255,
        translate=True
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
        help='Description of the certificate',
        translate=True
    )

    language_id = fields.Many2one(
        string='Language',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='Related language',
        comodel_name='cefrl.language',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    certificate_ids = fields.One2many(
        string='Certificates',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='List of certificates in this group',
        comodel_name='cefrl.certificate',
        inverse_name='group_id',
        domain=[],
        context={},
        auto_join=False,
        limit=None
    )

    certificate_count = fields.Integer(
        string='Certificate count',
        required=False,
        readonly=True,
        index=False,
        default=0,
        help='Number of certificates in this group',
        compute='_compute_certificate_count'
    )

    @api.depends('certificate_ids')
    def _compute_certificate_count(self):
        for record in self:
            record.certificate_count = len(record.certificate_ids)

    _sql_constraints = [
        (
            'unique_code',
            'UNIQUE(code)',
            _('A certificate group with this code already exists')
        ),
        (
            'unique_name',
            'UNIQUE(name)',
            _('A certificate group with this name already exists')
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
                ('language_id', operator, name)
            ]
            if operator in NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
            domain = AND([domain, args])

        group_ids = self._search(domain, limit=limit,
                                 access_rights_uid=name_get_uid)
        group_set = self.browse(group_ids).with_user(name_get_uid)

        return models.lazy_name_get(group_set)
