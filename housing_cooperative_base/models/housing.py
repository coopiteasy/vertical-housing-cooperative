# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HousingPlan(models.Model):
    _name = "hc.plan"
    _description = "HousingPlan"

    name = fields.Char()


class Housing(models.Model):
    _name = "hc.housing"
    _description = "Housing"
    _inherits = {"hc.premise": "premise_id"}

    premise_id = fields.Many2one(
        "hc.premise",
        auto_join=True,
        index=True,
        required=True,
        ondelete="cascade",
    )

    floor = fields.Integer(string="Floor number", required=False)
    keys = fields.Char(string="Keys", required=False)
    nb_keys = fields.Integer(string="Number of Keys", required=False)
    industrial_services = fields.Html(
        string="Industrial Services", required=False
    )
    is_arcade = fields.Boolean(string="Is Arcade", required=False)

    nb_rooms = fields.Float(
        string="Number of Rooms",
        required=False,
        help="Counting all rooms in this housing",
    )
    surface = fields.Float(string="Surface", required=False, help="m²")
    suggested_social_share = fields.Float(
        string="Suggested Social Share",
        compute="_compute_suggested_social_share",
    )
    social_share = fields.Float(
        string="Social Share", default=lambda x: x.suggested_social_share
    )
    # cluster_id = fields.Many2one(
    #     comodel_name="hc.cluster", string="Cluster", required=False
    # )
    housing_plan_id = fields.Many2one(
        comodel_name="hc.plan", string="Housing Plan", required=False
    )

    @api.multi
    @api.depends(
        "surface",
        "nb_rooms",
        "premise_id.building_id.social_share",
        "premise_id.building_id.regime",
    )
    def _compute_suggested_social_share(self):
        for housing in self:
            building = housing.premise_id.building_id
            if building:
                if building.regime == "square_meters":
                    housing.suggested_social_share = (
                        building.social_share * housing.surface
                    )
                elif building.regime == "nb_rooms":
                    housing.suggested_social_share = (
                        building.social_share * housing.nb_rooms
                    )
                else:
                    raise ValidationError(_("Unknown building regime"))
            else:
                housing.suggested_social_share = None

    @api.multi
    @api.depends("lease_ids", "lease_ids.tenant_id")
    def _compute_tenant_ids(self):
        for housing in self:
            housing.tenant_ids = housing.lease_ids.mapped("tenant_id").ids
