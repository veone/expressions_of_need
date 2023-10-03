from odoo import fields, models, api


class StockPicking(models.Model):
    """ Inherit the 'stock.picking' class to add new fields """
    _inherit = 'stock.picking'

    expression_of_need_id = fields.Many2one('expression.of.need', string="Expressions de besoins")
    expression_of_need_hider = fields.Boolean(string="Hider", default=True)
