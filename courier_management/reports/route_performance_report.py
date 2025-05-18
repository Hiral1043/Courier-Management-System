from odoo import models, fields, api

class RoutePerformanceReport(models.Model):
    _name = 'route.performance.report'
    _description = 'Route Performance Report'
    _auto = False  
    _rec_name = 'route_id'

    route_id = fields.Many2one('shipping.route', string='Route')
    total_bookings = fields.Integer(string='Total Bookings')


    def init(self):
        self.env.cr.execute("""
            DROP VIEW IF EXISTS route_performance_report;
            CREATE OR REPLACE VIEW route_performance_report AS (
                SELECT
                    MIN(id) AS id,
                    route_id,
                    state,
                    COUNT(*) AS total_bookings
                FROM courier_booking
                WHERE route_id IS NOT NULL
                GROUP BY route_id, state
            )
        """)
        
