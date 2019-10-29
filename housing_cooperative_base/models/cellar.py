# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Cellar(models.Model):
    _name = 'hc.cellar'
    _description = 'Cellar'

    name = fields.Char(
        string='Name',
        required=True)
    active = fields.Boolean(
        string='Active?',
        default=True)
    floor = fields.Integer(
        string='Floor number',
        required=False)
    surface = fields.Integer(
        string='Surface',
        required=False,
        help='m²')

    street = fields.Char(
        string='Street',
        required=False)
    street_number = fields.Char(
        string='Street Number',
        required=False)
    municipality = fields.Char(
        string='Municipality',
        required=False)
    zip_code = fields.Char(
        string='Zip Code',
        required=False)
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country',
        required=False)
    state_id = fields.Many2one(
        domain="[('country_id', '=', country_id)]",
        comodel_name='res.country.state',
        string='Country State',
        required=False)

    housing_id = fields.Many2one(
        comodel_name='hc.housing',
        string='Housing',
        required=False)
    cluster_id = fields.Many2one(
        comodel_name='hc.cluster',
        string='Cluster',
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
        for cellar in self:
            if cellar.cluster_id:
                cellar.state = 'busy'
            elif 'ongoing' in cellar.lease_ids.mapped('state'):
                cellar.state = 'busy'
            else:
                cellar.state = 'available'

    @api.constrains('cluster_id', 'housing_id')
    def _constrain_unique(self):
        for cellar in self:
            if cellar.cluster_id and cellar.housing_id:
                raise ValidationError(
                    'A cellar can not be linked '
                    'to a housing and a cluster at the same time'
                )
