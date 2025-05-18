from odoo import models, fields

class ComplainStatusReport(models.Model):
    _name = 'complain.status.report'
    _description = 'Complaint Status Report'
    _auto = False 
    _rec_name = "complaint_category"

    complaint_category = fields.Selection([
        ('delay', 'Delay'),
        ('damage', 'Damage'),
        ('wrong_delivery', 'Wrong Delivery'),
        ('payment_issue', 'Payment Issue')
    ], string='Category')

    status = fields.Selection([
        ('open', 'Open'),
        ('in_progress', 'In-progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], string='Status')

    assigned_to = fields.Many2one('res.users', string='Assigned To')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string='Priority')

    resolution_time = fields.Integer(string="Resolution Time (Days)")
    count = fields.Integer(string='Complaint Count') 

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW complain_status_report AS (
                SELECT
                    MIN(id) AS id,
                    complaint_category,
                    status,
                    assigned_to,
                    priority,
                    AVG(resolution_time) AS resolution_time,
                    COUNT(*) AS count
                FROM
                    customer_complaint
                GROUP BY
                    complaint_category, status, assigned_to, priority
            );
        """)
