# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Room(models.Model):
    _name = "hc.room"
    _description = "Room"
    _inherits = {"hc.premise": "premise_id"}

    premise_id = fields.Many2one(
        "hc.premise",
        auto_join=True,
        index=True,
        required=True,
        ondelete="cascade",
    )

    # TODO: (maybe) implement this type of constraint on lease level, or remove
    # @api.constrains("cluster_id", "housing_id")
    # def _constrain_unique(self):
    #     for room in self:
    #         if room.cluster_id and room.housing_id:
    #             raise ValidationError(
    #                 "A room can not be linked "
    #                 "to a housing and a cluster at the same time"
    #             )
