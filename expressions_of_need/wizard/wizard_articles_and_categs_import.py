import io
import xlrd
import babel
import logging
import tempfile
import binascii
from io import StringIO
from datetime import date, datetime, time
from email.policy import default
from odoo import api, fields, models, tools, exceptions, _
from odoo.exceptions import AccessError, Warning, UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class WizardArticleCategoryImport(models.TransientModel):
    _name = 'wizard.artcat.import'
    _description = 'Wizard Article and category Import'

    article_category_line_ids = fields.Many2many('wizard.artcat.import.line', string="Liste Articles")

    file_type = fields.Selection([('XLSX', 'Fichier XLSX')], string='Type de Fichier', default='XLSX')
    file = fields.Binary(string="Téléverser le fichier")

    def import_list(self):
        self.ensure_one()
        if len(self.article_category_line_ids):
            product_product = self.env['product.product']
            compte = 0
            for any_prdct in self.article_category_line_ids:
                if not any_prdct.unit_of_measure_id or not any_prdct.monarticle or not any_prdct.category_id or not any_prdct.sub_category_id:
                    message = "Veuillez remplir tous les champs de la ligne où L'UNITÉ DE MESURE = " + str(any_prdct.unit_of_measure_id.name) + ", L'ARTICLE = " + str(any_prdct.monarticle) + ", LA CATÉGORIE = " + str(any_prdct.sub_category_id.name) + " et LA SOUS CATÉGORIE = " + str(any_prdct.category_id.name) +  " avant d'importer."
                    raise ValidationError(_(message))
                les_products = product_product.search([('name', '=', any_prdct.monarticle), ('uom_id', '=', any_prdct.unit_of_measure_id.id), ('uom_po_id', '=', any_prdct.unit_of_measure_id.id), ('categ_id', '=', any_prdct.sub_category_id.id)])
                compte = compte + 1
                vals = {
                    'name': any_prdct.monarticle,
                    'categ_id': any_prdct.sub_category_id.id,
                    'uom_id': any_prdct.unit_of_measure_id.id,
                    'uom_po_id': any_prdct.unit_of_measure_id.id,
                    'detailed_type': 'product',
                    'supplier_taxes_id': False
                }  

                if len(les_products):
                    for le_prdct in les_products:
                        le_prdct.write(vals)
                else:
                    product_product.create(vals)

    @api.onchange('file')
    def import_article_and_category_list(self):
        if self.file:
            try:
                file = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".xlsx")
                file.write(binascii.a2b_base64(self.file))
                file.seek(0)
                values = {}
                workbook = xlrd.open_workbook(file.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise ValidationError(_("Veuillez choisir un format de fichier valide (xlsx) !"))

            for row_no in range(sheet.nrows):
                if row_no <= 0:
                    fields = list(
                        map(lambda row: row.value.encode('utf-8'), sheet.row(row_no)))
                else:
                    line = list(
                        map(lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))

                    values.update({
                        'article': line[0],
                        'category': line[1],
                        'sub_category': line[2],
                        'unit_of_measure': line[3]
                    })

                    res = self._create_imported_articles_and_categories(values)
            

    def _create_imported_articles_and_categories(self, values):
        the_category = self._get_category(values.get('category').strip())
        the_sub_category = self._get_sub_category(values.get('sub_category').strip(), the_category)
        the_unit_of_measure = self._get_unit_of_measure(values.get('unit_of_measure').strip())
        
        vals = {
            'monarticle': str(values.get('article').strip()),
            'category_id': the_category,
            'sub_category_id': the_sub_category,
            'unit_of_measure_id': the_unit_of_measure            
        }

        res = self.article_category_line_ids = [(0, 0, vals)]
        return res

    def _get_category(self, name):
        identifiant = False
        
        if name:
                product_category_env = self.env['product.category']
                product_category = product_category_env.search([('name', '=', name), ], limit=1)
                if product_category:
                    identifiant = product_category.id
                else:
                    vals = {
                        'name': name,
                        'property_cost_method': 'average'  
                    }
                    product_created = product_category_env.create(vals)
                    identifiant = product_created.id
        else:
            message = str(name) + " n'est pas une catégorie d'articles connue." + \
                " Veuillez choisir une catégorie d'articles existante."
            raise ValidationError(_(message))
        return identifiant

    def _get_sub_category(self, name, id):
        identifiant = False
        
        if name:
                product_sub_category_env = self.env['product.category']
                product_sub_category = product_sub_category_env.search([('name', '=', name), ('parent_id', '=', id), ], limit=1)
                if product_sub_category:
                    identifiant = product_sub_category.id
                else:
                    vals = {
                        'name': name,
                        'parent_id': id,
                        'property_cost_method': 'average' 
                    }
                    product_created = product_sub_category_env.create(vals)
                    identifiant = product_created.id
        else:
            message = str(name) + " n'est pas une sous catégorie d'articles connue." + \
                " Veuillez choisir une sous catégorie d'articles existante."
            raise ValidationError(_(message))
        return identifiant

    def _get_unit_of_measure(self, name):
        identifiant = False
        
        if name:
                unit_of_measure_env = self.env['uom.uom']
                unit_of_measure = unit_of_measure_env.search([('name', '=', name), ], limit=1)
                if unit_of_measure:
                    identifiant = unit_of_measure.id
        else:
            message = str(name) + " n'est pas une unité de mesure connue." + \
                " Veuillez choisir une unité de mesure existante."
            raise ValidationError(_(message))
        return identifiant