from odoo import fields, models, api


class StockLocation(models.Model):
    """ Inherit the 'stock.location' class to add new fields """
    _inherit = 'stock.location'

    stock_commentary_ids = fields.One2many(
        'stock.commentary', 'stock_location_id', string='Commentaires du stock')
    number_of_commentaries = fields.Integer(
        "Commentaires", compute='_get_number_of_commentaries')

    @api.depends('stock_commentary_ids')
    def _get_number_of_commentaries(self):
        for line in self:
            line.number_of_commentaries = len(line.stock_commentary_ids)

    def get_open_commentaries(self):
        return {
            'name': 'Commentaries',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'stock.commentary',
            'target': 'current',
            # 'res_id': self.purchase_order_ids[0].id,
            'domain': [('id', 'in', self.stock_commentary_ids.ids)],
        }
