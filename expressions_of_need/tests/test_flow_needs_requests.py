# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import mock
from odoo.tests import common, HttpCase, tagged
from odoo import tools
from . import models

@tagged('-at_install', 'post_install')
class TestFlowNeedsRequest(common.TransactionCase):
    def setUp(self):
        super(TestFlowNeedsRequest, self).setUp()

        the_user_env = self.env['res.users']
        the_user_id = the_user_env.search([], limit=1)

        the_uom_env = self.env['uom.uom']
        the_uom_id = the_uom_env.search([], limit=1)

        the_product_env = self.env['product.product']
        self.product_vals1 = {
            "name": "Tomate",
        }
        the_product_instance1 = the_product_env.create(self.product_vals1)
        self.product_vals2 = {
            "name": "Chipsy",
        }
        the_product_instance2 = the_product_env.create(self.product_vals2)
        self.product_vals3 = {
            "name": "Patate",
        }
        the_product_instance3 = the_product_env.create(self.product_vals3)
        self.product_vals4 = {
            "name": "Banane",
        }
        the_product_instance4 = the_product_env.create(self.product_vals4)

        values1 = {
            "product_id": the_product_instance1.id,
            "quantity": 1,
            #"uom_id": the_product_instance1.uom_id.id,
            #"quantity_validate": 0,
            #"quantity_remaining": 1
        }
        values2 = {
            "product_id": the_product_instance2.id,
            "quantity": 2,
            #"uom_id": the_product_instance2.uom_id.id,
            #"quantity_validate": 0,
            #"quantity_remaining": 2
        }
        values3 = {
            "product_id": the_product_instance3.id,
            "quantity": 3,
            #"uom_id": the_product_instance3.uom_id.id,
            #"quantity_validate": 0,
            #"quantity_remaining": 3
        }
        values4 = {
            "product_id": the_product_instance4.id,
            "quantity": 4,
            #"uom_id": the_product_instance4.uom_id.id,
            #"quantity_validate": 0,
            #"quantity_remaining": 4
        }

        need_vals = {
            "user_id": the_user_id.id,
            "need_line_ids":  [(0, 0, values1),(0, 0,values2),(0, 0, values3),(0, 0, values4)],
        }
        self.expression_of_need_env = self.env["expression.of.need"]
        self.expression_of_need_instance = self.expression_of_need_env.create(need_vals)

    def test_submission(self):
        self.expression_of_need_instance.put_in_waiting_state()
        self.assertEqual(self.expression_of_need_instance.state, 'waiting')

    def test_validation(self):
        self.test_submission()
        self.expression_of_need_instance.put_in_validated_state()
        self.assertEqual(self.expression_of_need_instance.state, 'validated')

    def test_internal_transfer(self):
        self.test_validation()
        internal_transfer_wizard = self.WizardStockPickingGenerationTest.create({
            'partner_id': self.expression_of_need_instance.partner_id.id,
            'picking_type_id': self.expression_of_need_instance.picking_type_id.id,
            'expression_of_need_id': self.expression_of_need_instance.expression_of_need_id.id,
            'scheduled_date': self.expression_of_need_instance.scheduled_date,
            'expression_of_need_line': [(6, 0, self.expression_of_need_instance.need_line_ids.ids)],
            'location_id': self.expression_of_need_instance.company_id.partner_id.property_stock_supplier.id,
            'location_dest_id': self.expression_of_need_instance.user_id.partner_id.property_stock_customer.id,
        })
        internal_transfer_wizard.confirm()
        self.assertNotEqual(len(self.health_insurance_pricing_instance), 0)
        with self.assertRaises(NotImplementedError):
            internal_transfer_wizard.confirm()   