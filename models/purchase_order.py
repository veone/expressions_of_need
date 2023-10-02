from odoo import fields, models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'Purchase Order'

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------
    
    summary_sheet_id = fields.Many2one('summary.sheet', string='Summary Sheet')
    summary_field_hider = fields.Boolean(string="Summary Field Hider", default=True)

    # def _get_destination_location(self):
    #     #result = super(PurchaseOrder, self)._get_destination_location()
    #     self.ensure_one()
    #     if self.partner_id:
    #         return self.partner_id.property_stock_customer.id
    #     #return self.picking_type_id.default_location_dest_id.id


    # def _prepare_picking(self):
    #     result = super(PurchaseOrder, self)._prepare_picking()

    #     result['location_dest_id'] = self.partner_id.property_stock_customer.id

    #     return result
