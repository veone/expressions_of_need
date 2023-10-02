import datetime
import uuid
import logging
from datetime import date, time, datetime, timedelta
from odoo import api, fields, models, tools, exceptions, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

STATE = [('draft', 'Draft'),
         ('waiting', 'Waiting for validation'),
         ('validated', 'Validated'),
         ('canceled', 'Canceled')]

STATUS = [('not_delivered', 'Not delivered'),
          ('in_delivered', 'In delivered'),
          ('delivered', 'Delivered'),
          ('canceled', 'Canceled')]


class ExpressionOfNeed(models.Model):
    _name = 'expression.of.need'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Expression of need'

    name = fields.Char("Code")
    date = fields.Date("Date", default=fields.Datetime.now)
    state = fields.Selection(STATE, default='draft', string="State", tracking=True)
    status_validation = fields.Selection(STATUS, string="Status validation", compute="_compute_status_validation",
                                         tracking=True)
    filter_validation = fields.Selection(STATUS, string="Filter validation", compute='_compute_status_validation',
                                         store=True)
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user.id)
    need_line_ids = fields.One2many('expression.of.need.line', 'need_id', string="Need line", copy=True)
    company_id = fields.Many2one('res.company', readonly=True, string="Company", default=lambda self: self.env.company)

    expression_of_need_count = fields.Integer("Expressions", compute='get_expression_of_need_count')
    stock_picking_ids = fields.One2many('stock.picking', 'expression_of_need_id', string='Stocks Pickings')

    total_quantity = fields.Integer("Total Quantity", compute='_compute_total_quantities')
    total_quantity_validate = fields.Integer("Total Quantity Validate", compute='_compute_total_quantities')
    total_quantity_remaining = fields.Integer("Total Quantity Remaining", compute='_compute_total_quantities')

    @api.depends('need_line_ids', 'need_line_ids.quantity', 'need_line_ids.quantity_validate',
                 'need_line_ids.quantity_remaining')
    def _compute_total_quantities(self):
        for record in self:
            record.total_quantity = 0
            record.total_quantity_validate = 0
            record.total_quantity_remaining = 0

            if record.need_line_ids:
                record.total_quantity = sum(line.quantity for line in record.need_line_ids)
                record.total_quantity_validate = sum(line.quantity_validate for line in record.need_line_ids)
                record.total_quantity_remaining = sum(line.quantity_remaining for line in record.need_line_ids)

    @api.depends('total_quantity_remaining', 'total_quantity_validate', 'total_quantity', 'state')
    def _compute_status_validation(self):
        for record in self:
            record.filter_validation = 'not_delivered'
            record.status_validation = 'not_delivered'
            if record.total_quantity_remaining == 0:
                record.status_validation = 'delivered'
                record.filter_validation = 'delivered'
            elif record.total_quantity_remaining > 0 and record.total_quantity > record.total_quantity_remaining:
                record.status_validation = 'in_delivered'
                record.filter_validation = 'in_delivered'

            if record.state == 'canceled':
                record.status_validation = 'canceled'
                record.filter_validation = 'canceled'

    def action_open_transfers(self):
        res = self.env.ref('stock.action_picking_tree_all')
        res = res.sudo().read()[0]
        res.update({
            'context': {
                'default_expression_of_need_id': self.id,
            },
            'domain':
                [('expression_of_need_id', '=', self.id)]
        })
        return res

    @api.depends('stock_picking_ids')
    def get_expression_of_need_count(self):
        for line in self:
            line.expression_of_need_count = len(line.stock_picking_ids)

    @api.model_create_multi
    def create(self, vals):
        records = super(ExpressionOfNeed, self).create(vals)
        for record in records:
            record.name = self.env['ir.sequence'].next_by_code('expression.of.need') or _('New')
        return records

    def generate_intern_transfer(self):
        """ Open wizard window for Intern Transfer Generation. """
        res = self.env.ref('expressions_of_need.action_wizard_interne_transfer_generation')
        res = res.sudo().read()[0]

        stock_picking = self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1)
        the_picking_type = False
        if stock_picking:
            the_picking_type = stock_picking.id

        res.update({
            'context': {
                'default_partner_id': self.user_id.partner_id.id,
                'default_picking_type_id': the_picking_type,
                'default_expression_of_need_id': self.id,
                'default_scheduled_date': self.date,
                'default_location_id': self.company_id.partner_id.property_stock_supplier.id,
                'default_location_dest_id': self.user_id.partner_id.property_stock_customer.id,
                'default_expression_of_need_line': [(6, 0, self.need_line_ids.ids)]
            }
        })
        return res

    def put_in_waiting_state(self):
        for line in self:
            if len(self.need_line_ids):
                line.state = 'waiting'
            else:
                raise ValidationError("Veuillez renseigner les articles de l'expression de besoins")

    def put_in_validated_state(self):
        for line in self:
            if len(self.need_line_ids):
                line.state = 'validated'
            else:
                raise ValidationError("Veuillez renseigner les articles de l'expression de besoins")

    def put_in_canceled_state(self):
        for line in self:
            line.state = 'canceled'

    def put_in_draft_state(self):
        for line in self:
            line.state = 'draft'


class ExpressionOfNeedline(models.Model):
    _name = 'expression.of.need.line'
    _description = 'Expression of need line'

    date = fields.Date("Date")
    quantity = fields.Float("Desired quantity")
    quantity_validate = fields.Float("Quantity validate", compute="_compute_quantity_validate")
    quantity_remaining = fields.Float("Quantity remaining", invisible=True, compute="_compute_quantity_remaining")
    need_id = fields.Many2one('expression.of.need', string="Expression of need")
    product_id = fields.Many2one('product.product', string="Product")
    uom_id = fields.Many2one('uom.uom', string="Unit of measure")
    user_id = fields.Many2one('res.users', string="User")

    @api.depends('quantity', "quantity_validate")
    def _compute_quantity_remaining(self):
        for record in self:
            record.quantity_remaining = int(record.quantity - record.quantity_validate) if 0 < int(
                record.quantity - record.quantity_validate) else 0

    @api.depends('quantity', "need_id.stock_picking_ids")
    def _compute_quantity_validate(self):
        for record in self:
            somme = 0
            transfers = record.need_id.stock_picking_ids.sudo().search(
                [('expression_of_need_id', '=', record.need_id.id), ('state', '=', 'done')])
            for any_tranfer in transfers:
                for any_line in any_tranfer.move_ids_without_package:
                    if any_line.product_id.id == record.product_id.id:
                        somme = somme + any_line.quantity_done
            record.quantity_validate = somme

    @api.constrains('quantity', 'quantity_validate', 'quantity_remaining')
    def _check_quantities(self):
        for record in self:
            if record.quantity <= 0 or record.quantity_validate < 0 or record.quantity_remaining < 0:
                raise ValidationError("La quantité doit être supérieure à zéro")

    @api.onchange('product_id')
    def get_onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
            my_uoms_domain = [('category_id', '=', self.product_id.uom_id.category_id.id)]
            my_uoms = self.env['uom.uom'].search(my_uoms_domain, order='id desc')
            return {'domain': {'uom_id': [('id', 'in', my_uoms.ids)]}}

    @api.onchange('uom_id')
    def get_onchange_uom_id(self):
        if self.uom_id and not self.product_id:
            my_products_ids_domain = [('id', '=', self.uom_id.id)]
            my_products_ids = self.env['product.product'].search(my_products_ids_domain, order='id desc')
            return {'domain': {'product_id': [('id', 'in', my_products_ids.ids)]}}
