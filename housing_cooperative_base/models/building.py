# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Building(models.Model):
    _name = "hc.building"
    _description = "Building"

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Active?", default=True)
    street = fields.Char(string="Street", required=True)
    street_number = fields.Char(string="Street Number", required=True)
    municipality = fields.Char(string="Municipality", required=True)
    zip_code = fields.Char(string="Zip Code", required=True)
    country_id = fields.Many2one(
        comodel_name="res.country", string="Country", required=True
    )
    state_id = fields.Many2one(
        domain="[('country_id', '=', country_id)]",
        comodel_name="res.country.state",
        string="Country State",
        required=False,
    )

    is_rented = fields.Boolean(string="Is Rented", default=False)
    landlord_id = fields.Many2one(
        comodel_name="res.partner", string="Landlord", required=False
    )
    lease_start = fields.Date(string="Lease Start", required=False)
    expected_lease_end = fields.Date(
        string="Expected Lease End", required=False
    )
    effective_lease_end = fields.Date(
        string="Effective Lease End", required=False
    )
    lease_end = fields.Date(string="Lease End", compute="_compute_lease_end")
    rent = fields.Float(string="Rent", required=False)
    charges = fields.Float(
        string="Charges", required=False, help="Monthly charges"
    )

    social_share = fields.Float(string="Social Share", required=False)
    regime = fields.Selection(
        string="Share Regime",
        selection=[
            ("square_meters", "Square Meters"),
            ("nb_rooms", "Number of Room"),
        ],
        default="square_meters",
        required=False,
    )

    nb_rooms = fields.Integer(string="Number of Rooms", required=False)
    surface_activities = fields.Integer(
        string="Surface Activities", required=False, help="m²"
    )
    parking_spaces = fields.Integer(string="Parking Spaces", required=False)
    heating_type = fields.Char(string="Type of Heating", required=False)
    maintenance_contract = fields.Html(
        string="Maintenance Contract", required=False
    )
    residents_association = fields.Html(
        string="Residents Association", required=False
    )
    concierge = fields.Many2one(
        comodel_name="res.partner", string="Concierge", required=False
    )
    architect = fields.Many2one(
        comodel_name="res.partner", string="Architect", required=False
    )

    housing_ids = fields.One2many(
        comodel_name="hc.housing",
        inverse_name="building_id",
        string="Housings",
        required=False,
    )
    room_ids = fields.One2many(
        comodel_name="hc.room",
        inverse_name="building_id",
        string="Rooms",
        required=False,
    )
    cluster_ids = fields.One2many(
        comodel_name="hc.cluster",
        inverse_name="building_id",
        string="Clusters",
        required=False,
    )

    @api.multi
    @api.depends("expected_lease_end", "effective_lease_end")
    def _compute_lease_end(self):
        for building in self:
            if building.effective_lease_end:
                building.lease_end = building.effective_lease_end
            else:
                building.lease_end = building.expected_lease_end
