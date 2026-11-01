###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestCefrlCompatibility(TransactionCase):

    def test_display_names(self):
        language = self.env.ref("cefrl.cefrl_language_ca")
        self.assertEqual(
            language.display_name,
            "{} ({})".format(language.name, language.code),
        )

        level_group = self.env.ref("cefrl.cefrl_level_group_A")
        self.assertEqual(
            level_group.display_name,
            "{} ({})".format(level_group.code, level_group.name),
        )

        level = self.env.ref("cefrl.cefrl_level_A1")
        self.assertEqual(
            level.display_name,
            "{} ({})".format(level.code, level.name),
        )

        certificate_group = self.env.ref("cefrl.cefrl_certificate_group_celga")
        self.assertEqual(
            certificate_group.display_name,
            "{} ({})".format(certificate_group.code, certificate_group.name),
        )

    def test_certificate_display_name_search(self):
        certificate = self.env.ref("cefrl.cefrl_certificate_celga_1")
        model = self.env["cefrl.certificate"]
        self.assertIn(
            certificate,
            model.search([("display_name", "ilike", "CELGA 1")]),
        )
        self.assertNotIn(
            certificate,
            model.search([("display_name", "not ilike", "CELGA 1")]),
        )

    def test_certificate_group_display_name_search(self):
        certificate_group = self.env.ref("cefrl.cefrl_certificate_group_celga")
        model = self.env["cefrl.certificate.group"]
        self.assertIn(
            certificate_group,
            model.search([("display_name", "ilike", "CELGA")]),
        )
        self.assertNotIn(
            certificate_group,
            model.search([("display_name", "not ilike", "CELGA")]),
        )
