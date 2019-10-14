# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HousingPlan(models.Model):
    _name = 'hc.plan'
    _description = 'HousingPlan'

    name = fields.Char()


class Housing(models.Model):
    _name = 'hc.housing'
    _description = 'Housing'

    name = fields.Char(
        string='Name',
        required=False)
    code = fields.Char(
        string='code',
        required=True)
    building_id = fields.Many2one(
        comodel_name='hc.building',
        string='Building',
        required=True)
    keys = fields.Char(
        string='Keys',
        required=False)

    nb_rooms = fields.Integer(
        string='Number of Rooms',
        required=False)
    surface = fields.Integer(
        string='Surface',
        required=False,
        help='m²')
    suggested_social_share = fields.Float(
        string='Suggested Social Share',
        compute='_compute_suggested_social_share')
    social_share = fields.Float(
        string='Social Share',
        default=lambda x: x.suggested_social_share)
    cluster_id = fields.Many2one(
        comodel_name='hc.cluster',
        string='Cluster',
        domain="[('building_id', '=', building_id)]",
        required=False)
    housing_plan_id = fields.Many2one(
        comodel_name='hc.plan',
        string='Housing Plan',
        required=False)
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
        default='available')
    tenant_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Tenants',
        compute='_compute_tenant_ids',
        store=True)
    lease_ids = fields.One2many(
        comodel_name='hc.lease',
        inverse_name='housing_id',
        string='Leases')

    @api.multi
    @api.depends('surface', 'nb_rooms',
                 'building_id.social_share', 'building_id.regime')
    def _compute_suggested_social_share(self):
        for housing in self:
            if housing.building_id.regime == 'square_meters':
                housing.suggested_social_share = (
                    housing.building_id.social_share * housing.nb_rooms
                )
            elif housing.building_id.regime == 'nb_rooms':
                housing.suggested_social_share = (
                    housing.building_id.social_share * housing.surface
                )
            else:
                raise ValidationError('Unknown building regime')

    @api.multi
    @api.depends('lease_ids', 'lease_ids.tenant_id')
    def _compute_tenant_ids(self):
        for housing in self:
            housing.tenant_ids = housing.lease_ids.mapped('tenant_id').ids
