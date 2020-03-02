# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Cellar(models.Model):
    _name = "hc.cellar"
    _description = "Cellar"
    _inherits = {"hc.premise": "premise_id"}

    premise_id = fields.Many2one(
        "hc.premise",
        auto_join=True,
        index=True,
        required=True,
        ondelete="cascade",
    )

    floor = fields.Integer(string="Floor number", required=False)
    surface = fields.Float(string="Surface", required=False, help="m²")
