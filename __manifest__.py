{
    'name': 'Expression of need',
    'version': '15.0.0.1',
    'summary': 'Management system expressions of need',
    'description': """
    """,
    'category': 'Expression of need',
    'author': 'Veone',
    'website': 'https://www.veone.net',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'product',
        'purchase',
        'purchase_stock',
        'stock',
        'report_xlsx'
    ],
    'data': [
        'data/expression_of_need_data.xml',
        'data/res_config_data.xml',
        'data/sequence.xml',
        'report/report.xml',
        'wizard/wizard_summary_sheet.xml',
        'wizard/wizard_stock_transfer_generation_view.xml',
        'wizard/wizard_articles_and_categs_import_line_view.xml',
        'wizard/wizard_articles_and_categs_import_view.xml',
        'wizard/wizard_stock_commentary_view.xml',
        'wizard/wizard_generate_commentaries_multi.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/expressions_of_need_views.xml',
        'views/summary_sheet_views.xml',
        'views/stock_picking_view.xml',
        'views/purchase_order_view.xml',
        'views/stock_commentary_view.xml',
        'views/stock_location_view.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/form.png',
        'static/description/generate.png',
    ],
    'installable': True,
    'auto_install': False
}
