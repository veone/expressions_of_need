import datetime
from odoo import fields, models, api, exceptions, _
from odoo.exceptions import UserError


class StockInventoryAdjustmentName(models.TransientModel):
    _inherit = 'stock.inventory.adjustment.name'

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if self.env.context.get('default_quant_ids'):
            quants = self.env['stock.quant'].browse(self.env.context['default_quant_ids'])
            res['show_info'] = any(not quant.inventory_quantity_set for quant in quants)

            commentary_table = []
            for any_quant in quants:
                valeurs = {
                    'location_id': any_quant.location_id.id,
                    'product_id': any_quant.product_id.id,
                    'quantity': any_quant.quantity,
                    'inventory_quantity': any_quant.inventory_quantity,
                    'inventory_diff_quantity': any_quant.inventory_diff_quantity,
                    'stock_quant_id': any_quant.id
                }
                commentary_table.append((0,0,valeurs))
            res['wizard_stock_commentary_ids'] = commentary_table
            
        return res
    
    wizard_stock_commentary_ids = fields.Many2many('wizard.stock.commentary', string="Commentaires" )

    def action_apply(self):
        for any_commentary in self.wizard_stock_commentary_ids:

            stockCommentary = self.env['stock.commentary']
            vals = {
                'stock_location_id': any_commentary.location_id.id,
                'product_id': any_commentary.product_id.id,
                'commentary': any_commentary.commentary,
                'inventory_diff_quantity': any_commentary.inventory_diff_quantity,
            }
            stockCommentary.sudo().create(vals)

        quants = self.env['stock.quant'].browse(self.env.context['default_quant_ids'])
        for any_quant in quants:
            any_quant._apply_inventory()
            any_quant.inventory_quantity_set = False