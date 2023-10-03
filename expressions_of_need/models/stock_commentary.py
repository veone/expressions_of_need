from odoo import api, fields, models, tools, exceptions, _
from odoo.exceptions import UserError, ValidationError


class StockCommentary(models.Model):
    _name = 'stock.commentary'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Stock Commentary'

    name = fields.Char("Numéro de commentaire", readonly=True)
    stock_location_id = fields.Many2one('stock.location', string='Stock Location', readonly=True)
    product_id = fields.Many2one('product.product', string='Article', readonly=True)
    inventory_diff_quantity = fields.Float(string="Différence", readonly=True,
                                           help="Différence de stock lors de l'inventaire")
    commentary = fields.Text(string='Commentaire')

    @api.model_create_multi
    def create(self, vals):
        records = super().create(vals)
        for record in records:
            record.name = 'Commentaire ' + self.env['ir.sequence'].next_by_code('stock.commentary.sequence') or _('New')
        return records
