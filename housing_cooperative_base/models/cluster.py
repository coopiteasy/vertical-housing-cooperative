# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Cluster(models.Model):
    _name = 'hc.cluster'
    _description = 'Cluster'

    name = fields.Char()
    building_id = fields.Many2one(
        comodel_name='hc.building',
        string='Building',
        required=True)
    code = fields.Char(
        string='Code',
        required=True)
    keys = fields.Char(
        string='Keys',
        required=False)
    housing_ids = fields.One2many(
        comodel_name='hc.housing',
        inverse_name='cluster_id',
        string='Housings',
        required=False)
    room_ids = fields.One2many(
        comodel_name='hc.room',
        inverse_name='cluster_id',
        string='Common Rooms',
        required=False)
