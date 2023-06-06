# -*- coding: utf-8 -*-
###############################################################################
#    Licence, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.osv.expression import FALSE_DOMAIN
from logging import getLogger


_logger = getLogger(__name__)


class AcademyDrivingLicence(models.Model):

    _name = 'driving.licence'
    _description = u'Driving licence'

    _rec_name = 'name'
    _order = 'country_id ASC, sequence ASC, name ASC'

    name = fields.Char(
        string='Name',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help=False,
        size=50,
        translate=True
    )

    country_id = fields.Many2one(
        string='Country',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='Country that has granted the licence',
        comodel_name='res.country',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    sequence = fields.Integer(
        string='Sequence',
        required=False,
        readonly=False,
        index=False,
        default=0,
        help='Driving licence sequence'
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
        help='Description of the driving licence',
        translate=True
    )

    implied_ids = fields.Many2many(
        string='Implied',
        required=False,
        readonly=False,
        index=True,
        default=None,
        help='Other licenses that are implicit with this one',
        comodel_name='driving.licence',
        relation='driving_licence_implied_rel',
        column1='licence_id',
        column2='implied_id',
        domain="[('id', '!=', id)]",
        context={},
        limit=None
    )

    implied_count = fields.Integer(
        string='Implied count',
        required=False,
        readonly=True,
        index=False,
        default=0,
        help='Number of implied licences',
        compute='_compute_implied_count'
    )

    @api.depends('implied_ids')
    def _compute_implied_count(self):
        for record in self:
            record.implied_count = len(record.implied_ids)

    match_country = fields.Boolean(
        string='Match country',
        required=False,
        readonly=True,
        index=False,
        default=False,
        help='Check if has the same country of the current company',
        compute='_compute_match_country',
        search='_search_match_country'
    )

    @api.depends('country_id')
    def _compute_field(self):
        company_id = self.env.company.id

        for record in self:
            record.match_country = (record.company_id.id == company_id)

    @api.model
    def _search_match_country(self, operator, value):
        domain = FALSE_DOMAIN

        if self.env.company and self.env.company.country_id:
            country_id = self.env.company.country_id.id

            if operator == '=' and value or operator == '!=' and not value:
                domain = [('country_id', '=', country_id)]
            else:
                domain = [('country_id', '!=', country_id)]

        return domain

    _sql_constraints = [
        (
            'unique_name_by_country',
            'UNIQUE(country_id, name)',
            _('There is already a licence with that name for this country')
        )
    ]

    def name_get(self):
        result = []

        for record in self:
            if record.country_id:
                country = record.country_id
                name = '{} - {}'.format(country.name, record.name)
            else:
                name = record.name

            result.append((record.id, name))

        return result
