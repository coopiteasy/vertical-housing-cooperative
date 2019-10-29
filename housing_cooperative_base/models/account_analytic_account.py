# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"
    _description = "AccountAnalyticAccount"

    lease_id = fields.Many2one(comodel_name="hc.lease", string="Lease")

    @api.multi
    def _create_invoice(self, invoice=False):
        res = super(AccountAnalyticAccount, self)._create_invoice(invoice)
        res.lease_id = self.lease_id
        return res


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    lease_id = fields.Many2one(comodel_name="hc.lease", string="Lease")
