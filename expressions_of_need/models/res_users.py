from odoo import fields, models, api

class ResUsers(models.Model):
    _inherit = 'res.users'
    _description = 'Res Users'

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------
    
    # def write(self, values):
    #     stock_location_env = self.env['stock.location']
    #     stock_location = stock_location_env.search([('usage', '=', 'internal'), ('name', '=', self.name)], limit=1)

    #     if stock_location:
    #         # the_stock_location_env = self.env['stock.location']
    #         # the_stock_location = the_stock_location_env.search([('usage', '=', 'internal'), ('name', '=', 'WH')], limit=1)
    #         stock_location.write({
    #             'name': self.name,
    #             'location_id': self.company_id.partner_id.property_stock_customer.id,
    #         })
    #     else:
    #         # the_stock_location_env = self.env['stock.location']
    #         # the_stock_location = the_stock_location_env.search([('usage', '=', 'internal'), ('name', '=', 'WH')], limit=1)
    #         vals = {
    #             'name': self.name,
    #             'location_id': self.company_id.partner_id.property_stock_supplier.id,
    #             'usage': 'internal',
    #             'company_id': self.company_id.id
    #         }
    #         user_location_id = stock_location_env.create(vals)
    #         self.partner_id.write({
    #             'property_stock_customer': user_location_id.id,
    #             'property_stock_supplier':  user_location_id.id
    #         })

    #     res = super().write(values)

    #     return res

    # @api.model
    # def create(self, values):
    #     result = super().create(values)

    #     stock_location_env = self.env['stock.location']
    #     stock_location = stock_location_env.search([('usage', '=', 'internal'), ('company_id', '=', result.company_id.id)], limit=1)

    #     if stock_location:
    #         vals = {
    #             'name': result.name,
    #             'location_id': result.company_id.partner_id.property_stock_customer.id,
    #             'usage': 'internal',
    #             'company_id': result.company_id.id
    #         }
    #         user_location_id = stock_location_env.create(vals)

    #         result.partner_id.write({
    #             'property_stock_customer': user_location_id.id,
    #             'property_stock_supplier':  user_location_id.id
    #         })

    #     return result