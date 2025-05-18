from odoo import models, fields, api

class TypeWiseReport(models.Model):
    _name = 'type.wise.report'
    _description = 'Type wise Report'
    _auto = False 
    _rec_name = 'complaint_category'

    status = fields.Selection([
        ('open','Open'),
        ('in_progress','In-progress'),
        ('resolved','Resolved'),
        ('closed','Closed')],string='Status')

    complaint_category = fields.Selection([
        ('delay','Delay'),
        ('damage','Damage'),
        ('wrong_delivery','Wrong Delivery'),
        ('payment_issue','Payment Issue')])
    
    complain_count = fields.Integer()

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW type_wise_report AS (
                SELECT
                    MIN(id) AS id,
                    complaint_category,
                    status,
                    COUNT(*) AS complain_count
                FROM customer_complaint
                GROUP BY status, complaint_category
            )
        """)