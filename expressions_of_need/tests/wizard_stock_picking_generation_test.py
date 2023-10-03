from odoo import fields, models, _

class WizardStockPickingGenerationTest(models.TransientModel):
    _inherit = 'wizard.stock.transfer.generation'
    _name = 'wizard.stock.transfer.generation.test'
    _description = 'Description'

    partner_id = fields.Many2one('res.partner', string='Demandeur', required=False)
    picking_type_id = fields.Many2one('stock.picking.type', string='Type Opération')
    expression_of_need_id = fields.Many2one('expression.of.need', string='Expression de besoins')
    scheduled_date = fields.Date("Date")
    expression_of_need_line = fields.Many2many('expression.of.need.line', string="Need line")
    location_id = fields.Many2one('stock.location', string='Origine', help="Emplacement Source", required=True, domain=[('usage', '=', 'internal')])
    location_dest_id = fields.Many2one('stock.location', string='Destination', help="Emplacement de Destination", required=True, domain=[('usage', '=', 'internal')])