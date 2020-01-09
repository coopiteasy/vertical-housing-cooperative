# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LeaseLine(models.Model):
    _name = "hc.lease.line"
    _description = "Lease Line"
    _order = "building_id, premise_id, start desc"

    name = fields.Char(string="Name", compute="_compute_name", store=False)
    lease_id = fields.Many2one(
        comodel_name="hc.lease", string="Lease", required=True
    )
    premise_id = fields.Many2one(
        comodel_name="hc.premise", string="Premise", required=True
    )

    tenant_id = fields.Many2one(related="lease_id.tenant_id")
    start = fields.Date(related="lease_id.start")
    end = fields.Date(related="lease_id.end")
    lease_state = fields.Selection(
        related="lease_id.state", string="Lease State"
    )

    building_id = fields.Many2one(related="premise_id.building_id")
    state = fields.Selection(related="premise_id.state")
    rent = fields.Float(related="premise_id.rent")
    charges = fields.Float(related="premise_id.charges")

    @api.multi
    @api.depends("premise_id", "lease_id")
    def _compute_name(self):
        for leaseline in self:
            premise = leaseline.premise_id.name
            lease = leaseline.lease_id.name
            leaseline.name = "%s in Lease %s" % (premise, lease)
