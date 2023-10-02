from odoo import api, fields, models, tools, exceptions, _
from odoo.exceptions import UserError, ValidationError

class StockQuant(models.Model):
    """ Inherit the 'stock.quant' class to add new fields """
    _inherit = 'stock.quant'

    def action_apply_inventory(self):
        """ Open wizard window for stock commentary. """
        if self.inventory_diff_quantity != 0:
            res = self.env.ref('expressions_of_need.action_wizard_stock_commentary')
            res = res.sudo().read()[0]

            res.update({
                'context': {
                    'default_location_id': self.location_id.id,
                    'default_product_id': self.product_id.id,
                    'default_quantity': self.quantity,
                    'default_inventory_quantity': self.inventory_quantity,
                    'default_inventory_diff_quantity': self.inventory_diff_quantity,
                    'default_stock_quant_id': self.id,
                }
            })
            return res
        result = super(StockQuant, self).action_apply_inventory()