# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import api, exceptions, fields, models
import logging

_logger = logging.getLogger(__name__)


class RentalStateReportWizard(models.TransientModel):
    _name = "hc.rental.state.report.wizard"
    _description = "Create Rental State Report"

    name = fields.Char(compute="_compute_name", store=True)
    building_ids = fields.Many2many(
        comodel_name="hc.building", string="Buildings"
    )
    start = fields.Date(string="Start", required=True)
    end = fields.Date(string="End", required=True)
    lease_line_ids = fields.Many2many(
        comodel_name="hc.lease.line", compute="_compute_lease_line_ids"
    )

    @api.multi
    @api.depends("start", "end")
    def _compute_name(self):
        for wizard in self:
            wizard.name = "rental_state_report_%s_%s" % (
                wizard.start,
                wizard.end,
            )

    @api.multi
    @api.depends("building_ids", "start", "end")
    def _compute_lease_line_ids(self):
        self.ensure_one()

        today = fields.Date.today()
        lease_line_ids = self.env["hc.lease.line"].search([])
        lease_line_ids = lease_line_ids.filtered(
            lambda lease_line_id: lease_line_id.start
            <= today
            <= lease_line_id.end
        )

        # if self.building_ids:
        #     lease_line_ids = lease_line_ids.filtered(
        #         lambda lease_line_id: lease_line_id.premise_id.building_id
        # # Todo: .building_id of premise not accessible yet
        #         in self.building_ids
        #     )

        self.lease_line_ids = lease_line_ids
        return True

    @api.multi
    def create_report(self):
        self.ensure_one()
        _logger.info("Creating %s" % self.name)

        action = self.env.ref(
            "housing_cooperative_base.rental_state_report"
        ).report_action(self)

        return action
