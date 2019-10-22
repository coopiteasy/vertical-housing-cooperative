# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.exceptions import ValidationError
import logging


class HousingCooperativeTests(common.TransactionCase):

    def setUp(self):
        super(HousingCooperativeTests, self).setUp()
        self.housing1 = self.env.ref('housing_cooperative_base.demo_housing_1')
        self.housing2 = self.env.ref('housing_cooperative_base.demo_housing_2')
        self.cluster1 = self.env.ref('housing_cooperative_base.demo_cluster_1')
        self.room1 = self.env.ref('housing_cooperative_base.demo_room_1')
        self.room2 = self.env.ref('housing_cooperative_base.demo_room_2')
        self.room6 = self.env.ref('housing_cooperative_base.demo_room_6')
        self.cellar2 = self.env.ref('housing_cooperative_base.demo_cellar_2')
        self.lease2 = self.env.ref('housing_cooperative_base.demo_lease_2')

    def test_suggested_rent(self):
        rent = self.housing2.rent + self.room2.rent + self.room6.rent + self.cellar2.rent
        self.assertEqual(self.lease2.suggested_rent, rent)

    def test_create_contract(self):
        self.lease2.create_contract()
        self.assertTrue(self.lease2.contract_id)

        with self.assertRaises(ValidationError):
            self.lease2.create_contract()

    def test_adding_room_of_cluster_to_housing_error(self):
        with self.assertRaises(ValidationError):
            self.room1.housing_id = self.housing1
