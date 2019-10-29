# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HousingPlan(models.Model):
    _name = "hc.plan"
    _description = "HousingPlan"

    name = fields.Char()


class Housing(models.Model):
    _name = "hc.housing"
    _description = "Housing"

    name = fields.Char(string="Name", required=False)
    active = fields.Boolean(string="Active?", default=True)
    code = fields.Char(string="code", required=True)
    building_id = fields.Many2one(
        comodel_name="hc.building", string="Building", required=True
    )
    floor = fields.Integer(string="Floor number", required=False)
    keys = fields.Char(string="Keys", required=False)
    nb_keys = fields.Integer(string="Number of Keys", required=False)
    industrial_services = fields.Html(
        string="Industrial Services", required=False
    )

    nb_rooms = fields.Integer(
        string="Number of Rooms",
        required=False,
        help="Counting all rooms in this housing",
    )
    surface = fields.Integer(string="Surface", required=False, help="m²")
    suggested_social_share = fields.Float(
        string="Suggested Social Share",
        compute="_compute_suggested_social_share",
    )
    social_share = fields.Float(
        string="Social Share", default=lambda x: x.suggested_social_share
    )
    cluster_id = fields.Many2one(
        comodel_name="hc.cluster", string="Cluster", required=False
    )
    room_ids = fields.One2many(
        comodel_name="hc.room",
        inverse_name="housing_id",
        string="Common Rooms",
        required=False,
    )
    cellar_ids = fields.One2many(
        comodel_name="hc.cellar",
        inverse_name="housing_id",
        string="Cellars",
        required=False,
    )
    housing_plan_id = fields.Many2one(
        comodel_name="hc.plan", string="Housing Plan", required=False
    )
    rent = fields.Float(string="Rent", required=False)
    charges = fields.Float(string="Charges", required=False)
    state = fields.Selection(
        string="State",
        selection=[
            ("available", "Available"),
            ("busy", "Busy"),
            ("unavailable", "Unavailable"),
        ],
        default="available",
    )
    tenant_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Tenants",
        compute="_compute_tenant_ids",
        store=True,
    )
    lease_ids = fields.One2many(
        comodel_name="hc.lease", inverse_name="housing_id", string="Leases"
    )

    @api.multi
    @api.depends(
        "surface", "nb_rooms", "building_id.social_share", "building_id.regime"
    )
    def _compute_suggested_social_share(self):
        for housing in self:
            if housing.building_id:
                if housing.building_id.regime == "square_meters":
                    housing.suggested_social_share = (
                        housing.building_id.social_share * housing.surface
                    )
                elif housing.building_id.regime == "nb_rooms":
                    housing.suggested_social_share = (
                        housing.building_id.social_share * housing.nb_rooms
                    )
                else:
                    raise ValidationError("Unknown building regime")
            else:
                housing.suggested_social_share = None

    @api.multi
    @api.depends("lease_ids", "lease_ids.tenant_id")
    def _compute_tenant_ids(self):
        for housing in self:
            housing.tenant_ids = housing.lease_ids.mapped("tenant_id").ids

    @api.constrains("room_ids")
    def _constrain_room_in_same_building(self):
        for housing in self:
            for room in housing.room_ids:
                if room.building_id != housing.building_id:
                    raise ValidationError(
                        _(
                            'Room "%s" can\'t be linked '
                            "to a housing from a different building."
                            % room.name
                        )
                    )
