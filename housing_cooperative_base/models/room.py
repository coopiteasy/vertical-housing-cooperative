# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Room(models.Model):
    _name = 'hc.room'
    _description = 'Room'

    name = fields.Char(
        string='Name',
        required=True)
    building_id = fields.Many2one(
        comodel_name='hc.building',
        string='Building',
        required=True)
    housing_id = fields.Many2one(
        comodel_name='hc.housing',
        string='Housing',
        domain="[('building_id', '=', building_id)]",
        required=False)
    cluster_id = fields.Many2one(
        comodel_name='hc.cluster',
        string='Cluster',
        domain="[('building_id', '=', building_id)]",
        required=False)
    lease_ids = fields.Many2many(
        comodel_name='hc.lease',
        string='Leases')
    rent = fields.Float(
        string='Rent',
        required=False)
    charges = fields.Float(
        string='Charges',
        required=False)
    state = fields.Selection(
        string='State',
        selection=[('available', 'Available'),
                   ('busy', 'Busy'),
                   ('unavailable', 'Unavailable')],
        compute='_compute_state',
        store=True)

    @api.multi
    @api.depends('cluster_id', 'lease_ids')
    def _compute_state(self):
        for room in self:
            if room.cluster_id:
                room.state = 'busy'
            elif 'ongoing' in room.lease_ids.mapped('state'):
                room.state = 'busy'
            else:
                room.state = 'available'

    @api.constrains('cluster_id', 'housing_id')
    def _constrain_unique(self):
        for room in self:
            if room.cluster_id and room.housing_id:
                raise ValidationError(
                    'A room can not be linked '
                    'to a housing and a cluster at the same time'
                )
