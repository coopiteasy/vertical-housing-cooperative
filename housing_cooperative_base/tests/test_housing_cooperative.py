# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import ValidationError


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
