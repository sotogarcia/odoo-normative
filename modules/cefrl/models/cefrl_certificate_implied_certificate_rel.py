# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.tools import drop_view_if_exists
from logging import getLogger


_logger = getLogger(__name__)


class CefrlCertificateImpliedCertificateRel(models.Model):
    """ Relationship
    """

    _name = 'cefrl.certificate.implied.certificate.rel'
    _description = u'Cefrl certificate implied certificate rel'

    _auto = False
    _table = 'cefrl_certificate_implied_certificate_rel'

    _view_sql = '''
        SELECT DISTINCT
            crt1."id" AS certificate_id,
            crt2."id" AS implied_id
        FROM
            cefrl_certificate AS crt1
        INNER JOIN cefrl_certificate_group AS grp
            ON grp."id" = crt1.group_id
        INNER JOIN cefrl_certificate AS crt2
            ON crt2.group_id = grp."id"
            AND crt2."sequence" <= crt1."sequence"
    '''

    certificate_id = fields.Many2one(
        string='Certificate',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='Parent certificate',
        comodel_name='cefrl.certificate',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    implied_id = fields.Many2one(
        string='Implied',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help='Child certificate',
        comodel_name='cefrl.certificate',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    def init(self):
        sentence = 'CREATE or REPLACE VIEW {} as ( {} )'

        drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute(sentence.format(self._table, self._view_sql))

        self.prevent_actions()

    def prevent_actions(self):
        actions = ['INSERT', 'UPDATE', 'DELETE']

        BASE_SQL = '''
            CREATE OR REPLACE RULE {table}_{action} AS
                ON {action} TO {table} DO INSTEAD NOTHING
        '''

        for action in actions:
            sql = BASE_SQL.format(table=self._table, action=action)
            self.env.cr.execute(sql)
