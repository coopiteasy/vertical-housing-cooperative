# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Contract(models.Model):
    _inherit = "contract.contract"

    lease_id = fields.Many2one(comodel_name="hc.lease", string="Lease")

    @api.multi
    def recurring_create_invoice(self):
        res = super(Contract, self).recurring_create_invoice()
        res.write({"lease_id": self.lease_id.id})
        return res


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    lease_id = fields.Many2one(comodel_name="hc.lease", string="Lease")
