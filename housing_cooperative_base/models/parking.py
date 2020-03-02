# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Manuel Claeys Bouuaert <manuel@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Parking(models.Model):
    _name = "hc.parking"
    _description = "Parking"
    _inherits = {"hc.premise": "premise_id"}

    premise_id = fields.Many2one(
        "hc.premise",
        auto_join=True,
        index=True,
        required=True,
        ondelete="cascade",
    )

    keys = fields.Char(string="Keys", required=False)
    nb_keys = fields.Integer(string="Number of Keys", required=False)
    location = fields.Text(string="Location", required=False)
