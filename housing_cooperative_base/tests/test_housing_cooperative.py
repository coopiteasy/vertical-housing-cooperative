# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import common


class HousingCooperativeCase(common.TransactionCase):
    def setUp(self):
        super(HousingCooperativeCase, self).setUp()
        self.lease1 = self.env.ref("housing_cooperative_base.demo_lease_1")
        self.lease2 = self.env.ref("housing_cooperative_base.demo_lease_2")
        self.lease3 = self.env.ref("housing_cooperative_base.demo_lease_3")

        self.default_rent_product = self.env.ref(
            "housing_cooperative_base.product_product_rent"
        )
        self.default_charges_product = self.env.ref(
            "housing_cooperative_base.product_product_charges"
        )

        self.housing1 = self.env.ref("housing_cooperative_base.demo_housing_1")
        self.building2 = self.env.ref(
            "housing_cooperative_base.demo_building_2"
        )

    def test_contract_product_set_to_default(self):
        self.lease2.create_contract()

        contract_lines = self.lease2.contract_id.contract_line_ids
        # any line will do for test purpose
        # we might need to be more precise in the future
        rent_line = contract_lines.filtered(lambda l: "rent" in l.name)[0]
        charges_line = contract_lines.filtered(lambda l: "charges" in l.name)[
            0
        ]

        self.assertEqual(rent_line.product_id, self.default_rent_product)
        self.assertEqual(charges_line.product_id, self.default_charges_product)

    def test_contract_product_set_to_premise_product(self):
        self.lease1.create_contract()

        # only one premise
        contract_lines = self.lease1.contract_id.contract_line_ids
        rent_line = contract_lines.filtered(lambda l: "rent" in l.name)[0]
        charges_line = contract_lines.filtered(lambda l: "charges" in l.name)[
            0
        ]

        self.assertEqual(rent_line.product_id, self.housing1.rent_product_id)
        self.assertEqual(
            charges_line.product_id, self.housing1.charges_product_id
        )

    def test_contract_product_set_to_building_product(self):
        self.lease3.create_contract()

        # only one premise
        contract_lines = self.lease3.contract_id.contract_line_ids
        rent_line = contract_lines.filtered(lambda l: "rent" in l.name)[0]
        charges_line = contract_lines.filtered(lambda l: "charges" in l.name)[
            0
        ]

        self.assertEqual(rent_line.product_id, self.building2.rent_product_id)
        self.assertEqual(
            charges_line.product_id, self.building2.charges_product_id
        )

    def test_create_second_contract_fails(self):
        self.assertFalse(self.lease2.contract_id)
        self.lease2.create_contract()
        with self.assertRaises(ValidationError):
            self.lease2.create_contract()

    def test_create_deposit_invoice(self):
        deposit_account = self.env["account.account"].search(
            [("name", "=", "Account Receivable")]
        )
        self.housing1.deposit_product_id.property_account_income_id = (
            deposit_account
        )

        self.lease1.create_deposit_invoice()

        invoice = self.lease1.deposit_invoice_id
        line_account = (
            invoice.invoice_line_ids.product_id.property_account_income_id
        )
        self.assertEqual(line_account, deposit_account)

    def test_create_contract_across_month(self):
        lease = self.lease1
        lease_start = date(2030, 3, 14)
        lease_end = date(2030, 5, 14)
        lease.start = lease_start
        lease.expected_end = lease_end
        lease.create_contract()

        # relying on contract line and invoice line order, not very robust
        contract_line = lease.contract_id.contract_line_ids[0]

        self.assertEqual(contract_line.next_period_date_start, lease_start)
        self.assertEqual(contract_line.next_period_date_end, date(2030, 3, 31))
        res = lease.create_invoice()
        invoice = self.env["account.invoice"].browse(res["res_id"])
        self.assertEqual(invoice.date_invoice, lease_start)
        invoiced_line_quantity = invoice.invoice_line_ids[0].quantity
        self.assertEqual(invoiced_line_quantity, round(18 / 31, 3))

        self.assertEqual(
            contract_line.next_period_date_start, date(2030, 4, 1),
        )
        self.assertEqual(contract_line.next_period_date_end, date(2030, 4, 30))
        res = lease.create_invoice()
        invoice = self.env["account.invoice"].browse(res["res_id"])
        self.assertEqual(
            invoice.date_invoice, date(2030, 4, 1),
        )
        invoiced_line_quantity = invoice.invoice_line_ids[0].quantity
        self.assertEqual(invoiced_line_quantity, 1)

        self.assertEqual(
            contract_line.next_period_date_start, date(2030, 5, 1)
        )
        self.assertEqual(contract_line.next_period_date_end, lease_end)
        res = lease.create_invoice()
        invoice = self.env["account.invoice"].browse(res["res_id"])
        self.assertEqual(invoice.date_invoice, lease_end)
        invoiced_line_quantity = invoice.invoice_line_ids[0].quantity
        self.assertEqual(invoiced_line_quantity, round(14 / 31, 3))

        with self.assertRaises(ValidationError):
            lease.create_invoice()
