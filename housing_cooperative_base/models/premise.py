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
    code = fields.Char(string="Code", required=False)
    lease_line_ids = fields.One2many(
        comodel_name="hc.lease.line",
        inverse_name="premise_id",
        string="Lease Lines",
    )
    rent = fields.Float(string="Rent", required=False)
    charges = fields.Float(string="Charges", required=False)
    state = fields.Selection(
        string="State",
        selection=[("available", "Available"), ("busy", "Busy")],
        compute="_compute_state",
        store=True,
    )

    @api.multi
    @api.depends("lease_line_ids", "name")
    def _compute_state(self):
        today = fields.Date.today()
        for premise in self:
            active_lease_line_ids = premise.lease_line_ids.filtered(
                lambda lease_line_id: lease_line_id.lease_id.start
                <= today
                <= lease_line_id.lease_id.end
            )
            premise.state = "busy" if active_lease_line_ids else "available"

            # Todo: understand why this is not computed if it only depends on lease_line_ids
            # print(premise)
            # print(premise.name)
            # print(premise.lease_line_ids)
            # print(active_lease_line_ids)
            # print(any(active_lease_line_ids))
            # print(premise.state)
