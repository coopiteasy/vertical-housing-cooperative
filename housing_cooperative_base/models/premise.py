# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Premise(models.Model):
    _name = "hc.premise"
    _description = "Premise"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Active?", default=True)
    lease_ids = fields.Many2many(comodel_name="hc.lease", string="Leases")
    rent = fields.Float(string="Rent", required=False)
    charges = fields.Float(string="Charges", required=False)
    state = fields.Selection(
        string="State",
        selection=[
            ("available", "Available"),
            ("busy", "Busy"),
            ("unavailable", "Unavailable"),
        ],
        compute="_compute_state",
        store=True,
    )

    @api.multi
    # @api.depends("lease_ids")
    def _compute_state(self):
        return "available"
