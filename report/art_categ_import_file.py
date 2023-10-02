# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ArtCategXlsx(models.AbstractModel):
    _name = "report.expressions_of_need.report_art_categ_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "articles and categ XLSX Report"

    def _retrieve_categories(self):
        my_category_domain = [('parent_id', '=', False)]
        my_categories = self.env['product.category'].search(my_category_domain, order='name desc')
        mes_categories = []
        if len(my_categories):
            for any_category in my_categories:
                mes_categories.append(any_category.name)
        return mes_categories

    def _retrieve_sub_categories(self):
        my_sub_category_domain = []
        my_sub_categories = self.env['product.category'].search(my_sub_category_domain, order='name desc')
        mes_sous_categories = []
        if len(my_sub_categories):
            for any_category in my_sub_categories:
                if any_category.parent_id:
                    mes_sous_categories.append(any_category.name)
        return mes_sous_categories

    def _retrieve_unit_of_measure(self):
        my_uom_domain = []
        my_uoms = self.env['uom.uom'].search(my_uom_domain, order='name desc')
        mes_unites_de_mesure = []
        if len(my_uoms):
            for any_uom in my_uoms:
                mes_unites_de_mesure.append(any_uom.name)
        return mes_unites_de_mesure

    def generate_xlsx_report(self, workbook, data, partners):

        mes_categories = self._retrieve_categories()
        mes_sous_categories = self._retrieve_sub_categories()
        mes_unites = self._retrieve_unit_of_measure()

        sheet = workbook.add_worksheet("Commissions")
        
        header_format = workbook.add_format({'bold': True,
                                     'align': 'center',
                                     'valign': 'vcenter',
                                     'fg_color': '#00477A',
                                     'border': 1,
                                     'color': '#FFFFFF'
                                     })
        dropdown_format = workbook.add_format({'bold': True,
                                                   'align': 'center',
                                                   'valign': 'vcenter',
                                                   'fg_color': '#00477A',
                                                   'border': 1,
                                                   'locked': True,
                                                   'color': '#FFFFFF'
                                                   })

        data_format = workbook.add_format({'bold': False, 'valign': 'vcenter', 'locked': False})
            
        sheet.set_column(1, 0, 25)
        sheet.write('A1', 'Articles', header_format)
        sheet.set_column(1, 1, 25)
        sheet.write('B1', 'Catégories', dropdown_format)
        sheet.set_column(1, 2, 25)
        sheet.write('C1', 'Sous Catégories', dropdown_format)
        sheet.set_column(1, 3, 25)
        sheet.write('D1', 'Unités', dropdown_format)
        
        sheet.freeze_panes(1, 0)    

        los_products = self.env['product.product']
        nos_products = los_products.search([], order='id desc')
        if len(nos_products):
            i = 2
            for any_product in nos_products:
                a_indice = 'A' + str(i)
                a_contenu = any_product.name
                sheet.write(a_indice, a_contenu, data_format)

                b_indice = 'B' + str(i)
                b_contenu = any_product.categ_id.parent_id.name
                sheet.write(b_indice, b_contenu, data_format)

                c_indice = 'C' + str(i)
                c_contenu = any_product.categ_id.name
                sheet.write(c_indice, c_contenu, data_format)

                d_indice = 'D' + str(i)
                d_contenu = any_product.uom_id.name
                sheet.write(d_indice, d_contenu, data_format)

                i = i + 1


        sheet.data_validation('B2:B1000', {
                'validate': 'list',
                'source': mes_categories,
                'input_title': 'Choix catégories:',
                'input_message': 'Veuillez choisir une catégorie',
            }
            )

        sheet.data_validation('C2:C1000', {
                'validate': 'list',
                'source': mes_sous_categories,
                'input_title': 'Choix sous catégories:',
                'input_message': 'Veuillez choisir une sous catégorie',
            }
            )

        sheet.data_validation('D2:D1000', {
                'validate': 'list',
                'source': mes_unites,
                'input_title': 'Choix Unités de mesure:',
                'input_message': 'Veuillez choisir une unité de mesure',
            }
            )