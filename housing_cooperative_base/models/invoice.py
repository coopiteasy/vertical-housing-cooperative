# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    lease_id = fields.Many2one(comodel_name="hc.lease", string="Lease")
