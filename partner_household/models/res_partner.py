# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = "ResPartner"

    is_household = fields.Boolean(string="Household", default=False)

    # company_type = fields.Selection(
    #     selection=[
    #         ('person', 'Individual'),
    #         ('company', 'Company'),
    #         ('household', 'Household')]
    # )
    #
    # @api.depends('is_company', 'is_household')
    # def _compute_company_type(self):
    #     for partner in self:
    #         if partner.is_company:
    #             partner.company_type = 'company'
    #         elif partner.is_household:
    #             partner.company_type = 'household'
    #         else:
    #             partner.company_type = 'person'
    #
    # def _write_company_type(self):
    #     for partner in self:
    #         partner.is_company = partner.company_type == 'company'
    #         partner.is_household = partner.company_type == 'household'
    #
    # @api.onchange('company_type')
    # def onchange_company_type(self):
    #     self.is_company = (self.company_type == 'company')
    #     self.is_household = (self.company_type == 'household')
