# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from dateutil.relativedelta import relativedelta


class Contract(models.Model):
    _inherit = "contract.contract"

    lease_id = fields.Many2one(comodel_name="hc.lease", string="Lease")

    @api.multi
    def recurring_create_invoice(self):
        res = super(Contract, self).recurring_create_invoice()
        res.write({"lease_id": self.lease_id.id})
        return res


class ContractLine(models.Model):
    _inherit = "contract.line"

    lease_line_id = fields.Many2one(
        comodel_name="hc.lease.line", string="Lease Line", required=False,
    )

    @api.multi
    def _get_quantity_to_invoice(
        self, period_first_date, period_last_date, invoice_date
    ):
        if self.lease_line_id:
            days_in_month = (period_first_date + relativedelta(day=31)).day
            days_to_invoice = (period_last_date - period_first_date).days + 1
            quantity = self.quantity * (days_to_invoice / days_in_month)
        else:
            quantity = super()._get_quantity_to_invoice(
                period_first_date, period_last_date, invoice_date
            )
        return quantity
