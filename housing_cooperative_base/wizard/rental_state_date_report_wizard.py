# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import logging

from odoo import api, fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)


class RentalStateDateReportWizardBuilding(models.TransientModel):
    _name = "hc.rental.state.date.report.wizard.building"
    _description = "Contain Rental State Report Building Data"

    rental_state_date_report_wizard_id = fields.Many2one(
        comodel_name="hc.rental.state.date.report.wizard"
    )
    building_id = fields.Many2one(
        comodel_name="hc.building", string="Building"
    )
    lease_line_ids = fields.Many2many(
        string="Leases", comodel_name="hc.lease.line"
    )

    @api.multi
    def get_data(self):
        data = {
            "date": self.rental_state_date_report_wizard_id.date.strftime(
                DEFAULT_SERVER_DATE_FORMAT
            )
        }
        return data

    @api.multi
    def create_report(self):
        action = self.env.ref(
            "housing_cooperative_base.rental_state_date_report"
        ).report_action(self)
        return action


class RentalStateDateReportWizard(models.TransientModel):
    _name = "hc.rental.state.date.report.wizard"
    _description = "Create Rental State Date Report"

    name = fields.Char(compute="_compute_name", store=True)
    date = fields.Date(
        string="Date", required=True, default=fields.Date.today()
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
    rental_state_date_report_wizard_building_ids = fields.One2many(
        comodel_name="hc.rental.state.date.report.wizard.building",
        inverse_name="rental_state_date_report_wizard_id",
    )

    @api.multi
    @api.depends("date")
    def _compute_name(self):
        for wizard in self:
            wizard.name = "rental_state_date_report_%s" % wizard.date

    @api.multi
    @api.depends("date", "building_ids")
    def _compute_lease_line_ids(self):
        self.ensure_one()
        if not self.date:
            self.date = fields.Date.today()
        self.lease_line_ids = self.env["hc.lease.line"].search(
            [
                ("start", "<=", self.date),
                ("end", ">=", self.date),
                ("building_id", "in", self.building_ids.ids),
                ("lease_state", "not in", ["new"]),
            ]
        )
        return True

    @api.multi
    def create_report(self):
        self.ensure_one()
        _logger.info("Creating %s" % self.name)

        for building in self.building_ids:
            self.env["hc.rental.state.date.report.wizard.building"].create(
                {
                    "rental_state_date_report_wizard_id": self.id,
                    "building_id": building.id,
                    "lease_line_ids": [
                        (
                            6,
                            0,
                            self.lease_line_ids.filtered(
                                lambda ll: ll.building_id == building
                            ).ids,
                        )
                    ],
                }
            )

        return (
            self.rental_state_date_report_wizard_building_ids.create_report()
        )
