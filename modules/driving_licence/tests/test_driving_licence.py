###############################################################################
#
#    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
#
###############################################################################

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDrivingLicence(TransactionCase):

    def test_spanish_catalogue_and_existing_xml_ids(self):
        licence_am = self.env.ref("driving_licence.driving_licence_am")
        licence_a1 = self.env.ref("driving_licence.driving_licence_a1")
        licence_a2 = self.env.ref("driving_licence.driving_licence_a2")

        self.assertEqual(licence_am._name, "driving.licence")
        self.assertEqual(licence_a2.name, "A2")
        self.assertEqual(licence_a2.implied_count, 2)
        self.assertIn(licence_am, licence_a2.implied_ids)
        self.assertIn(licence_a1, licence_a2.implied_ids)

    def test_display_name_contains_country(self):
        licence = self.env.ref("driving_licence.driving_licence_am")
        self.assertEqual(
            licence.display_name,
            f"{licence.country_id.name} - {licence.name}",
        )

    def test_inactive_b1_remains_accessible(self):
        licence = self.env.ref("driving_licence.driving_licence_b1")
        self.assertFalse(licence.active)
        self.assertTrue(licence.with_context(active_test=False).exists())

    def test_match_country_domain(self):
        country = self.env.ref("base.es")
        company = self.env.company
        original_country = company.country_id
        try:
            company.country_id = country
            licences = self.env["driving.licence"].search([
                ("match_country", "=", True),
            ])
            self.assertIn(
                self.env.ref("driving_licence.driving_licence_am"),
                licences,
            )
        finally:
            company.country_id = original_country
