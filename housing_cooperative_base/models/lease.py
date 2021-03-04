# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import logging


_logger = logging.getLogger(__name__)


class LeaseLine(models.Model):
    _name = "hc.lease.line"
    _description = "Lease Line"
    _order = "building_id, premise_id, start desc"

    lease_id = fields.Many2one(
        comodel_name="hc.lease",
        string="Lease",
        ondelete="cascade",
        required=True,
    )
    premise_id = fields.Many2one(
        comodel_name="hc.premise",
        string="Premise",
        ondelete="restrict",
        required=True,
    )

    tenant_id = fields.Many2one(related="lease_id.tenant_id")
    start = fields.Date(related="lease_id.start")
    end = fields.Date(related="lease_id.end")
    lease_state = fields.Selection(
        related="lease_id.state", string="Lease State"
    )

    code = fields.Char(related="premise_id.code")
    building_id = fields.Many2one(related="premise_id.building_id")
    state = fields.Selection(related="premise_id.state")
    suggested_rent = fields.Float(
        related="premise_id.rent", string="Suggested Rent"
    )
    suggested_charges = fields.Float(
        related="premise_id.charges", string="Suggested Charges"
    )
    rent = fields.Float()
    charges = fields.Float()
    deposit = fields.Float()

    @api.onchange("premise_id")
    def onchange_premise_id(self):
        self.rent = self.suggested_rent
        self.charges = self.suggested_charges


class Lease(models.Model):
    _name = "hc.lease"
    _description = "Lease"
    _order = "start desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Name", compute="_compute_name", store=True)
    lease_line_ids = fields.One2many(
        comodel_name="hc.lease.line",
        inverse_name="lease_id",
        string="Lease Lines",
    )
    tenant_id = fields.Many2one(
        comodel_name="res.partner", string="Tenant", required=True
    )
    signatory_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Signatories",
        relation="hc_lease_signatory_ids_rel",
    )
    inhabitant_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Inhabitants",
        relation="hc_lease_inhabitant_ids_rel",
    )
    start = fields.Date(
        string="Start", required=True, track_visibility="onchange"
    )
    expected_end = fields.Date(
        string="Expected End", required=True, track_visibility="onchange"
    )
    effective_end = fields.Date(
        string="Effective End", required=False, track_visibility="onchange"
    )
    end = fields.Date(string="End", compute="_compute_lease_end", store=True)
    automatic_renewal = fields.Boolean(
        string="Automatic Renewal", default=True
    )
    automatic_renewal_months = fields.Integer(
        string="Months Added Each Renewal", default=12, required=True
    )
    note = fields.Text(string="Note", required=False)
    total_rent = fields.Float(
        string="Rent Total", readonly=True, compute="_compute_total_rent"
    )
    total_charges = fields.Float(
        string="Charges Total", readonly=True, compute="_compute_total_rent"
    )
    total_deposit = fields.Float(
        string="Deposit Total", readonly=True, compute="_compute_total_rent"
    )
    state = fields.Selection(
        string="State",
        selection=[("new", "New"), ("ongoing", "Ongoing"), ("done", "Done")],
        compute="_compute_state",
        store=True,
    )
    # fixme this should be computed from a One2Many relation to
    #       contract.contract.lease_id
    contract_id = fields.Many2one(
        comodel_name="contract.contract",
        string="Contract",
        required=False,
        readonly=True,
    )
    invoice_ids = fields.One2many(  # This also includes the deposit invoice
        comodel_name="account.invoice",
        inverse_name="lease_id",
        string="Invoices",
        readonly=True,
    )
    deposit_invoice_id = fields.Many2one(
        comodel_name="account.invoice",
        inverse_name="lease_id",
        string="Deposit invoice",
    )

    attachment_number = fields.Integer(
        compute="_get_attachment_number", string="Number of Attachments"
    )
    attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        inverse_name="res_id",
        string="Attachments",
        domain=[("res_model", "=", "hc.lease")],
    )

    premise_ids = fields.Many2many(
        comodel_name="hc.premise",
        string="Premise",
        relation="hc_lease_premise_ids_rel",
        compute="_compute_premise_ids",
        store=True,
    )
    contains_arcade = fields.Boolean(
        compute="_compute_contains_arcade", store=True
    )

    @api.multi
    def write(self, vals):
        res = super(Lease, self).write(vals)
        for rec in self:
            if (
                "start" in vals
                or "expected_end" in vals
                or "effective_end" in vals
            ):
                rec._update_contract_dates()
        return res

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.signatory_ids |= res.tenant_id
        res.inhabitant_ids |= res.signatory_ids
        return res

    @api.multi
    @api.depends("tenant_id", "start")
    def _compute_name(self):
        for lease in self:
            tenant = lease.tenant_id.name
            date = str(lease.start)[:7]
            lease.name = "%s/%s" % (tenant, date)

    @api.multi
    @api.depends("lease_line_ids")
    def _compute_total_rent(self):
        for lease in self:
            lease.total_rent = sum(line.rent for line in lease.lease_line_ids)
            lease.total_charges = sum(
                line.charges for line in lease.lease_line_ids
            )
            lease.total_deposit = sum(
                line.deposit for line in lease.lease_line_ids
            )

    @api.multi
    @api.depends("expected_end", "effective_end")
    def _compute_lease_end(self):
        for lease in self:
            if lease.effective_end:
                lease.end = lease.effective_end
            else:
                lease.end = lease.expected_end

    @api.multi
    @api.depends("start", "end")
    def _compute_state(self):
        for lease in self:
            today = fields.Date.today()
            if lease.start and lease.end:
                if today < lease.start:
                    lease.state = "new"
                elif lease.start <= today <= lease.end:
                    lease.state = "ongoing"
                elif lease.end < today:
                    lease.state = "done"
                else:
                    False
            else:
                lease.state = "new"

    @api.multi
    @api.depends("lease_line_ids")
    def _compute_premise_ids(self):
        for lease in self:
            lease.premise_ids = lease.lease_line_ids.mapped("premise_id")

    @api.multi
    @api.depends("lease_line_ids")
    def _compute_contains_arcade(self):
        for lease in self:
            premise_ids = lease.lease_line_ids.mapped("premise_id").ids
            lease.contains_arcade = bool(
                self.env["hc.housing"].search(
                    [
                        ("is_arcade", "=", True),
                        ("premise_id", "in", premise_ids),
                    ]
                )
            )

    @api.onchange("tenant_id")
    def onchange_tenant_id(self):
        self.signatory_ids |= self.tenant_id

    @api.onchange("signatory_ids")
    def onchange_signatory_ids(self):
        self.inhabitant_ids |= self.signatory_ids

    @api.multi
    def _update_contract_dates(self):
        for line in self.contract_id.contract_line_ids:
            line.date_start = self.start
            line.date_end = self.end
            # In case the contract already reached it end, reset a next dateg
            if not line.recurring_next_date:
                line.recurring_next_date = (
                    line.last_date_invoiced + relativedelta(days=1)
                )

    @api.multi
    def _get_attachment_number(self):
        read_group_res = self.env["ir.attachment"].read_group(
            [("res_model", "=", "hc.lease"), ("res_id", "in", self.ids)],
            ["res_id"],
            ["res_id"],
        )
        attach_data = dict(
            (res["res_id"], res["res_id_count"]) for res in read_group_res
        )
        for lease in self:
            lease.attachment_number = attach_data.get(lease.id, 0)
            lease.contract_number = 1 if lease.contract_id else 0

    @api.multi
    def action_get_attachment_tree_view(self):
        self.ensure_one()
        attachment_action = self.env.ref("base.action_attachment")
        action = attachment_action.read()[0]
        action["context"] = {
            "default_res_model": self._name,
            "default_res_id": self.ids[0],
        }
        action["domain"] = str(
            ["&", ("res_model", "=", self._name), ("res_id", "in", self.ids)]
        )
        return action

    @api.multi
    def create_contract(self):
        self.ensure_one()
        if self.contract_id:
            raise ValidationError(_("A contract already exists."))

        contract = self.env["contract.contract"].create(
            {
                "name": self.name,
                "partner_id": self.tenant_id.id,
                "contract_type": "sale",
                "lease_id": self.id,
                "journal_id": self._default_journal().id,
            }
        )
        self.contract_id = contract

        rent = self.env.ref("housing_cooperative_base.product_product_rent")
        charges = self.env.ref("housing_cooperative_base.product_product_charges")

        for line in self.lease_line_ids:
            if line.premise_id.rent_product_id:
                rent = line.premise_id.rent_product_id

            self.env["contract.line"].create(
                # todo link lease lines and contract lines
                {
                    "name": "%s - rent" % line.premise_id.name,
                    "date_start": self.start,
                    "date_end": self.end,
                    "recurring_next_date": self.start,
                    "recurring_rule_type": "monthly",
                    "recurring_invoicing_type": "pre-paid",
                    "product_id": rent.id,
                    "uom_id": rent.uom_id.id,
                    "contract_id": contract.id,
                    "price_unit": line.rent,
                }
            )

            if line.premise_id.charges_product_id:
                charges = line.premise_id.charges_product_id

            self.env["contract.line"].create(
                {
                    "name": "%s - charges" % line.premise_id.name,
                    "date_start": self.start,
                    "date_end": self.end,
                    "recurring_next_date": self.start,
                    "recurring_rule_type": "monthly",
                    "recurring_invoicing_type": "pre-paid",
                    "product_id": charges.id,
                    "uom_id": charges.uom_id.id,
                    "contract_id": contract.id,
                    "price_unit": line.charges,
                }
            )

    @api.multi
    def create_invoice(self):
        self.ensure_one()
        if not self.contract_id:
            raise ValidationError(_("Create a contract first."))
        invoice = self.contract_id.recurring_create_invoice()

        return {
            "type": "ir.actions.act_window",
            "res_model": "account.invoice",
            "view_id": self.env.ref(
                "account.invoice_form"
            ).id,  # prefered over account.invoice_supplier_form
            "view_mode": "form",
            "res_id": invoice.id,
            "target": "current",
        }

    @api.multi
    def create_deposit_invoice(self):
        self.ensure_one()
        if self.deposit_invoice_id:
            raise ValidationError(_("A deposit invoice already exists."))

        invoice = self.env["account.invoice"].create(
            {
                "name": "Deposit",
                "partner_id": self.tenant_id.id,
                "date_invoice": fields.Date.today(),
                "lease_id": self.id,
                "journal_id": self._default_journal().id,
            }
        )
        
        self.deposit_invoice_id = invoice

        deposit = self.env.ref("housing_cooperative_base.product_product_deposit")

        for line in self.lease_line_ids:
            if line.premise_id.deposit_product_id:
                deposit = line.premise_id.deposit_product_id

            self.env["account.invoice.line"].create(
                {
                    "name": deposit.name,
                    "product_id": deposit.id,
                    "uom_id": deposit.uom_id.id,
                    "invoice_id": invoice.id,
                    "price_unit": line.deposit,
                    "account_id": self._default_journal().default_credit_account_id.id,
                    # Note: account can also be set by default function, if the journal is passed in the context:
                    # .with_context(journal_id=self._default_journal().id).create()
                }
            )

        return {
            "type": "ir.actions.act_window",
            "res_model": "account.invoice",
            "view_id": self.env.ref(
                "account.invoice_form"
            ).id,  # prefered over account.invoice_supplier_form
            "view_mode": "form",
            "res_id": invoice.id,
            "target": "current",
        }

    @api.model
    def _default_journal(self):
        company_id = self.env.context.get(
            "company_id", self.env.user.company_id.id
        )
        domain = [("type", "=", "sale"), ("company_id", "=", company_id)]
        return self.env["account.journal"].search(domain, limit=1)

    @api.multi
    def _do_automatic_renewal(self):
        for lease in self:
            if (
                lease.state == "ongoing"
                and lease.automatic_renewal
                and fields.Date.today() + relativedelta(days=1)
                >= lease.expected_end
            ):
                # If the end date was the last day of the month, keep it as such
                if lease.expected_end == lease.expected_end + relativedelta(
                    day=31
                ):
                    lease.expected_end += relativedelta(
                        months=lease.automatic_renewal_months, day=31
                    )
                else:
                    lease.expected_end += relativedelta(
                        months=lease.automatic_renewal_months
                    )

    @api.model
    def cron_do_automatic_renewal(self):
        _logger.info("Executing: automatic renewal of leases")
        leases = self.search([])
        leases._do_automatic_renewal()
