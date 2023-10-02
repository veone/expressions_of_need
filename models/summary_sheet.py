from odoo import fields, models, api, _

STATE = [('draft', 'Draft'),
         ('validated', 'Validated'),
         ('canceled', 'Canceled')]


class SummarySheet(models.Model):
    _name = 'summary.sheet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Summary sheet of the expression of need'

    name = fields.Char("Code")
    date = fields.Date("Date", default=fields.Datetime.now)
    state = fields.Selection(STATE, default='draft', string="State")
    user_id = fields.Many2one('res.users', string="User", default=lambda self: self.env.user.id)
    sheet_line_ids = fields.One2many('summary.sheet.line', 'sheet_id', string="Sheet line")
    need_line_ids = fields.Many2many('expression.of.need', string="Expression of need")
    number_of_need = fields.Integer("Number of need", compute='get_number_of_need')
    company_id = fields.Many2one('res.company', readonly=True, string="Company", default=lambda self: self.env.company)

    purchase_order_ids = fields.One2many('purchase.order', 'summary_sheet_id', string='Purchase Order')
    number_of_purchases = fields.Integer("Number of purchases", compute='get_number_of_purchases')

    categ_id = fields.Many2one('product.category', string='Product Category')

    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='company_id.currency_id')
    total_amount = fields.Monetary(string="Montant total", compute="_compute_total_amount")

    @api.depends('sheet_line_ids')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(line.quantity * line.product_id.standard_price for line in record.sheet_line_ids)

    @api.depends('purchase_order_ids')
    def get_number_of_purchases(self):
        for line in self:
            line.number_of_purchases = len(line.purchase_order_ids)

    @api.depends('need_line_ids')
    def get_number_of_need(self):
        for line in self:
            line.number_of_need = len(line.need_line_ids)

    @api.model_create_multi
    def create(self, vals):
        records = super(SummarySheet, self).create(vals)
        for record in records:
            record.name = self.env['ir.sequence'].next_by_code('summary.sheet') or _('New')
        return records

    def put_in_validated_state(self):
        for result in self:
            result.state = 'validated'

            the_order_lines = []
            for rec in result.sheet_line_ids:
                vals = {
                    'product_id': rec.product_id.id,
                    'product_qty': rec.quantity
                }
                the_order_lines.append(vals)

            purchases_env = self.env['purchase.order']
            purchases_env.create({
                'partner_id': result.company_id.partner_id.id,
                'order_line': [(0, 0, line) for line in the_order_lines],
                'summary_sheet_id': result.id,
                'summary_field_hider': False
            })

    def put_in_draft_state(self):
        for line in self:
            line.state = 'draft'

    def put_in_canceled_state(self):
        for line in self:
            line.state = 'canceled'

    def get_open_expression_of_need(self):
        # res = self.env.ref('expressions_of_need.expression_of_need_act_window')
        # res = res.sudo().read()[0]
        # res.update({
        #     'domain': [('id', 'in', self.need_line_ids.ids)]
        # })

        return {'name': 'Expressions de besoins',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree',
                'res_model': 'expression.of.need',
                'target': 'current',
                'domain': [('id', 'in', self.need_line_ids.ids)]
                }
        # return res

    def get_open_purchases(self):
        return {'name': 'Purchase order',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'purchase.order',
                'target': 'current',
                'res_id': self.purchase_order_ids[0].id,
                'domain': [('id', '=', self.purchase_order_ids[0].id)],
                }


class SummarySheetLine(models.Model):
    _name = 'summary.sheet.line'
    _description = 'summary sheet line'

    date = fields.Date("Date")
    quantity = fields.Float("Desired quantity")
    sheet_id = fields.Many2one('summary.sheet', string="Summary sheet")
    product_id = fields.Many2one('product.product', string="Product")
    uom_id = fields.Many2one('uom.uom', string="Unit of measure")
    quantity_validate = fields.Float("Quantity validate")
    quantity_remaining = fields.Float("Quantity remaining")

    currency_id = fields.Many2one('res.currency', string="Currency",
                                  related='sheet_id.company_id.currency_id')
    subtotal_amount = fields.Monetary(string="Sous Total", compute="_compute_subtotal_amount")

    @api.depends('quantity', 'product_id')
    def _compute_subtotal_amount(self):
        for record in self:
            record.subtotal_amount = record.quantity * record.product_id.standard_price
