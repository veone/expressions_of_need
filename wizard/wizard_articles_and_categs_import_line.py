from odoo import fields, models, api


class WizardArtcatImportLine(models.TransientModel):
    _name = 'wizard.artcat.import.line'
    _description = 'Wizard Articles and Categories import line'

    monarticle = fields.Char("Mon article")
    category_id = fields.Many2one('product.category', string="Catégorie")
    sub_category_id = fields.Many2one('product.category', string='Sous Catégorie')
    unit_of_measure_id = fields.Many2one('uom.uom', string="Unité de mesure")

    def import_list(self):
        pass