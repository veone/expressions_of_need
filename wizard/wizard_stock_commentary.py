from odoo import fields, models, api, _

from odoo import api, fields, models, tools, exceptions, _
from odoo.exceptions import AccessError, Warning, UserError, ValidationError


class WizardStockCommentary(models.TransientModel):
    _name = 'wizard.stock.commentary'
    _description = 'Stock Commentary'

    location_id = fields.Many2one('stock.location', string='Emplacement')
    product_id = fields.Many2one('product.product', string='Article')
    quantity = fields.Float(string="Quantité Disponible")
    inventory_quantity = fields.Float(string="Quantité Comptée")
    inventory_diff_quantity = fields.Float(string="Différence")
    stock_quant_id = fields.Many2one('stock.quant', string='Stock Quantity')
    commentary = fields.Text(string='Commentaire', required=True)
    

    def confirm(self):
        """ Write Stock location commentary difference on its quantities """
        self.ensure_one()

        stockCommentary = self.env['stock.commentary']
        vals = {
            'stock_location_id': self.location_id.id,
            'product_id': self.product_id.id,
            'commentary': self.commentary,
            'inventory_diff_quantity': self.inventory_diff_quantity,
        }
        stockCommentary.sudo().create(vals)


        products_tracked_without_lot = []
        for quant in self.stock_quant_id:
            rounding = quant.product_uom_id.rounding
            if fields.Float.is_zero(quant.inventory_diff_quantity, precision_rounding=rounding)\
                    and fields.Float.is_zero(quant.inventory_quantity, precision_rounding=rounding)\
                    and fields.Float.is_zero(quant.quantity, precision_rounding=rounding):
                continue
            if quant.product_id.tracking in ['lot', 'serial'] and\
                    not quant.lot_id and quant.inventory_quantity != quant.quantity and not quant.quantity:
                products_tracked_without_lot.append(quant.product_id.id)
        # for some reason if multi-record, env.context doesn't pass to wizards...
        ctx = dict(self.stock_quant_id.env.context or {})
        ctx['default_quant_ids'] = self.stock_quant_id.ids
        quants_outdated = self.stock_quant_id.filtered(lambda quant: quant.is_outdated)
        if quants_outdated:
            ctx['default_quant_to_fix_ids'] = quants_outdated.ids
            return {
                'name': _('Conflict in Inventory Adjustment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'stock.inventory.conflict',
                'target': 'new',
                'context': ctx,
            }
        if products_tracked_without_lot:
            ctx['default_product_ids'] = products_tracked_without_lot
            return {
                'name': _('Tracked Products in Inventory Adjustment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'stock.track.confirmation',
                'target': 'new',
                'context': ctx,
            }
        self.stock_quant_id._apply_inventory()
        self.stock_quant_id.inventory_quantity_set = False