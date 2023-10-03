import logging
from odoo import fields, models, api, _
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class WizardActivity(models.TransientModel):
    _name = 'wizard.summary.sheet'
    _description = 'Summary sheet'

    need_line_ids = fields.Many2many('expression.of.need', string="Expression of need")
    sheet_line_ids = fields.One2many('wizard.sheet.line', 'sheet_id', string="Expression of need line")

    @api.onchange('need_line_ids')
    def get_product_line(self):
        if len(self.need_line_ids):
            for any_need in self.need_line_ids:
                if any_need.state != 'validated' or any_need.status_validation != 'not_delivered':

                    raise UserError(
                        _("Please choose some validated and undelivered Expressions of needs to generate a summary of need !"))

        WizardSheetLine = self.env['wizard.sheet.line']
        for exp_line in self.need_line_ids:
            for product_line in exp_line.need_line_ids:
                product = WizardSheetLine.search([('product_id', '=', product_line.product_id.id),
                                                  ('uom_id', '=', product_line.uom_id.id),
                                                  ('sheet_id', '=', self.id)
                                                  ])
                if product:
                    product.write({
                        'quantity': product.quantity + product_line.quantity
                    })
                else:
                    WizardSheetLine.create({'product_id': product_line.product_id.id,
                                            'uom_id': product_line.uom_id.id,
                                            'quantity': product_line.quantity,
                                            'sheet_id': self.id
                                            })


    def _get_last_parent(self, category):
        if not category.parent_id:
            return category
        else:
            return self._get_last_parent(category.parent_id)

        
    def generate_summary_sheet(self):

        filtered_categs = []        

        if len(self.sheet_line_ids):
            categ_list = []
            for any_sheet_line in self.sheet_line_ids:
                the_last_parent_category = self._get_last_parent(any_sheet_line.product_id.categ_id)

                if the_last_parent_category:
                    categ_list.append(the_last_parent_category.id)
                
            filtered_categs = list(set(categ_list))

            for any_filter in filtered_categs:
                # for any_need_line in self.need_line_ids:
                #     if any_need_line
                sheet = self.env['summary.sheet'].create({
                    'date': datetime.now().date(),
                    'user_id': self.env.user.id,
                    'categ_id': any_filter
                })

                if sheet:
                    for any_line in self.sheet_line_ids:
                        summary_sheet_env = self.env['summary.sheet.line']
                        summary_sheet_line = summary_sheet_env.search(
                            [('sheet_id', '=', sheet.id), ('product_id', '=', any_line.product_id.id)], limit=1)
                        
                        any_line_last_parent_category = self._get_last_parent(any_line.product_id.categ_id)

                        if any_line_last_parent_category.id == any_filter:
                            if not summary_sheet_line:
                                vals = {
                                    'sheet_id': sheet.id,
                                    'product_id': any_line.product_id.id,
                                    'uom_id': any_line.uom_id.id,
                                    'quantity': any_line.quantity
                                }
                                summary_sheet_env.create(vals)
                            else:
                                vals = {
                                    'sheet_id': sheet.id,
                                    'product_id': any_line.product_id.id,
                                    'uom_id': any_line.uom_id.id,
                                    'quantity': any_line.quantity + summary_sheet_line.quantity
                                }
                                summary_sheet_line.write(vals)

                    id_needs = []
                    for any_need in sheet.need_line_ids:
                        for any_line_need in any_need.need_line_ids:
                            for any_sum_line in sheet.sheet_line_ids:
                                if any_sum_line.product_id.id == any_line_need.product_id.id:
                                    id_needs.append(any_need.id)
                    filt_id_needs = list(set(id_needs))

                    sheet.update({
                        'need_line_ids': [(6, 0, filt_id_needs)]
                    })

                    
        res = self.env.ref('expressions_of_need.summary_sheet_act_window')
        res = res.sudo().read()[0]
        res.update({'domain': str([('categ_id', 'in', filtered_categs), ('user_id', '=', self.env.user.id)])})

        return res


class WizardSummarySheetLine(models.TransientModel):
    _name = 'wizard.sheet.line'
    _rec_name = 'product_id'
    _description = 'wizard sheet line'

    quantity = fields.Float("Desired quantity")
    product_id = fields.Many2one('product.product', string="Product")
    uom_id = fields.Many2one('uom.uom', string="Unit of measure")
    sheet_id = fields.Many2one('wizard.summary.sheet', string="Sheet")

    @api.constrains('quantity', 'quantity_validate', 'quantity_remaining')
    def _check_quantity(self):
        for record in self:
            if record.quantity < 0:
                raise ValidationError("La quantité doit être positive")
