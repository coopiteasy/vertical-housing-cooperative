# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class RentalStateYearReportWizard(models.TransientModel):
    _name = "hc.rental.state.year.report.wizard"
    _description = "Create Rental State Year Report"

    name = fields.Char(compute="_compute_name", store=True)
    year = fields.Integer(
        string="Year", required=True, default=fields.Date.today().year
    )
    building_ids = fields.Many2many(
        comodel_name="hc.building",
        string="Buildings",
        required=True,
        default=lambda s: s.env["hc.building"].search([]),
    )
    lease_line_ids = fields.Many2many(
        string="Selected Leases",
        comodel_name="hc.lease.line",
        compute="_compute_lease_line_ids",
    )
    premise_ids = fields.Many2many(
        string="Selected Premises",
        comodel_name="hc.premise",
        compute="_compute_premise_ids",
    )

    @api.multi
    @api.depends("year")
    def _compute_name(self):
        for wizard in self:
            wizard.name = "rental_state_year_report_%s" % wizard.year

    @api.multi
    @api.depends("year", "building_ids")
    def _compute_lease_line_ids(self):
        self.ensure_one()
        if not self.year:
            self.year = fields.Date.today().year
        self.lease_line_ids = (
            self.env["hc.lease.line"]
            .search(
                [
                    ("building_id", "in", self.building_ids.ids),
                    ("lease_state", "not in", ["new"]),
                ]
            )
            .filtered(
                lambda lease_line_id: lease_line_id.start.year
                <= self.year
                <= lease_line_id.end.year
            )
        )
        return True

    @api.multi
    @api.depends("year", "building_ids")
    def _compute_premise_ids(self):
        self.ensure_one()
        self.premise_ids = (
            self.env["hc.premise"]
            .search([])
            .filtered(
                lambda lease_line_id: lease_line_id.building_id
                in self.building_ids
            )
        )
        return True

    @api.multi
    def get_data(self):

        data_details = []

        # Note: this should be improved to store leases in the same premise together
        # and maybe adapted to manage multiple concurrent leases in the same premise

        for lease_line in self.lease_line_ids:
            data_details.append(
                {
                    lease_line.building_id.name
                    + " / "
                    + lease_line.premise_id.name: {
                        "months": [month for month in range(1, 12)],
                        "total_rent": 0,
                        "total_charges": 0,
                        "total_rent_charges": 0,
                    }
                }
            )

        data = {"data_details": data_details}
        return data

    @api.multi
    def create_report(self):
        self.ensure_one()
        _logger.info("Creating %s" % self.name)

        action = self.env.ref(
            "housing_cooperative_base.rental_state_year_report"
        ).report_action(self)

        return action
