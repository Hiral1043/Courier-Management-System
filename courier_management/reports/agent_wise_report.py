from odoo import models, fields

class AgentWiseReport(models.Model):
    _name = 'agent.wise.report'
    _description = 'Agent-wise Resolution Performance Report'
    _auto = False
    _rec_name = "assigned_to"

    assigned_to = fields.Many2one('res.users', string='Agent')
    complaint_category = fields.Selection([
        ('delay', 'Delay'),
        ('damage', 'Damage'),
        ('wrong_delivery', 'Wrong Delivery'),
        ('payment_issue', 'Payment Issue'),
    ], string='Category')
    complaints_count = fields.Integer(string='Total Complaints')

    def init(self):
        self.env.cr.execute("""
            DROP VIEW IF EXISTS agent_wise_report;
            CREATE VIEW agent_wise_report AS (
                SELECT
                    MIN(id) AS id,
                    assigned_to,
                    complaint_category,
                    COUNT(*) AS complaints_count
                FROM customer_complaint
                WHERE assigned_to IS NOT NULL
                GROUP BY assigned_to, complaint_category
            );
        """)