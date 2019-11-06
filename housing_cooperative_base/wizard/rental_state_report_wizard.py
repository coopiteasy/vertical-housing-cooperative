from odoo import api, exceptions, fields, models


class RentalStateReportWizard(models.TransientModel):
    _name = "hc.rental.state.report.wizard"
    _description = "Create Rental State Report"

    building_ids = fields.Many2many(
        comodel_name="hc.building", string="Buildings"
    )
    start = fields.Date(string="Start", required=True)
    end = fields.Date(string="End", required=True)

    lease_line_ids = fields.Many2many(
        comodel_name="hc.lease.line", compute="_compute_lease_line_ids"
    )

    @api.multi
    @api.depends("building_ids", "start", "end")
    def _compute_lease_line_ids(self):
        self.ensure_one()

        # print("Computing lease_line_ids")

        today = fields.Date.today()
        lease_line_ids = self.env["hc.lease.line"].search([])
        # print(lease_line_ids)
        lease_line_ids = lease_line_ids.filtered(
            lambda lease_line_id: lease_line_id.start
            <= today
            <= lease_line_id.end
        )
        # print(lease_line_ids)

        # if self.building_ids:
        #     lease_line_ids = lease_line_ids.filtered(
        #         lambda lease_line_id: lease_line_id.premise_id.building_id
        # # Todo: .building_id of premise not accessible yet
        #         in self.building_ids
        #     )

        # print(lease_line_ids)
        self.lease_line_ids = lease_line_ids
        return True

    @api.multi
    def create_report(self):
        self.ensure_one()
        # print("Creating report")
        # print(self.lease_line_ids) # Returns a record set with 5 records

        data = {"lease_line_ids": self.lease_line_ids}

        return self.env.ref(
            "housing_cooperative_base.rental_state_report"
        ).report_action(self, data=data)
        # Todo: passing data like this apparently passes it as a string, as seen by outputting <span t-esc="o" /> in report
