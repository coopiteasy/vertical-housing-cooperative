# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Cellar(models.Model):
    _name = "hc.cellar"
    _description = "Cellar"
    _inherit = "hc.premise"

    floor = fields.Integer(string="Floor number", required=False)
    surface = fields.Integer(string="Surface", required=False, help="m²")

    street = fields.Char(string="Street", required=False)
    street_number = fields.Char(string="Street Number", required=False)
    municipality = fields.Char(string="Municipality", required=False)
    zip_code = fields.Char(string="Zip Code", required=False)
    country_id = fields.Many2one(
        comodel_name="res.country", string="Country", required=False
    )
    state_id = fields.Many2one(
        domain="[('country_id', '=', country_id)]",
        comodel_name="res.country.state",
        string="Country State",
        required=False,
    )
