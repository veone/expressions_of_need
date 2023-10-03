from odoo import fields, models, api, _

from odoo import api, fields, models, tools, exceptions, _
from odoo.exceptions import AccessError, Warning, UserError, ValidationError


class WizardStockPickingGeneration(models.TransientModel):
    _name = 'wizard.stock.transfer.generation'
    _description = 'Description'

    partner_id = fields.Many2one('res.partner', string='Demandeur', required=False)
    picking_type_id = fields.Many2one('stock.picking.type', string='Type Opération')
    expression_of_need_id = fields.Many2one('expression.of.need', string='Expression de besoins')
    scheduled_date = fields.Date("Date")
    expression_of_need_line = fields.Many2many('expression.of.need.line', string="Need line")
    location_id = fields.Many2one('stock.location', string='Origine', help="Emplacement Source", required=True, domain=[('usage', '=', 'internal')])
    location_dest_id = fields.Many2one('stock.location', string='Destination', help="Emplacement de Destination", required=True, domain=[('usage', '=', 'internal')])

    def confirm(self):
        """ Generate stock picking from an expression of needs. """
        self.ensure_one()
        StockPicking = self.env['stock.picking']
        stock_line = []

        if len(self.expression_of_need_line):
            for any_expression in self.expression_of_need_line:     
                line_vals = {
                    'name': 'TRANSFER ' + str(any_expression.quantity) + " " + str(any_expression.product_id.name) + ' from ' + str(self.location_id.name) + " to " + str(self.location_dest_id.name),
                    'product_id': any_expression.product_id.id,
                    'product_uom_qty': any_expression.quantity,
                    'product_uom': any_expression.uom_id.id,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id
                }
                stock_line.append(line_vals)

        if self.expression_of_need_line:
            stock_picking = StockPicking.create({
                'partner_id': self.partner_id.id,
                'picking_type_id': self.picking_type_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'expression_of_need_id': self.expression_of_need_id.id,
                'scheduled_date': self.scheduled_date,
                'expression_of_need_hider': False,
                'move_ids_without_package': [(0, 0, line) for line in stock_line],
            })
        else:
            message = "Veuillez faire une Expression de besoins."
            raise ValidationError(_(message))

        try:
            form_view_id = self.env.ref("stock.view_picking_form").id
        except Exception as e:
            form_view_id = False
        return {
            'name': _('Transfert Interne'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': stock_picking.id,
            'context': {},
            'views': [(form_view_id, 'form')],
        }
