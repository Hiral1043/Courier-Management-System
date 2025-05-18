from odoo import models, fields

class CourierModeStatusReport(models.Model):
    _name = 'courier.mode.status.report'
    _description = 'Courier Mode-wise Status Report'
    _auto = False  
    _rec_name = "booking_id"
    booking_id = fields.Many2one('customer.booking')
    selected_mode_id = fields.Many2one('shipping.mode', string='Shipping Mode', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('invoiced', 'Invoiced'),
        ('picked', 'Picked'),
        ('in_transit', 'In-transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned')
    ], string='Status', readonly=True)
    booking_count = fields.Integer(string='Number of Bookings', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW courier_mode_status_report AS (
                SELECT
                    MIN(id) AS id,
                    selected_mode_id,
                    state,
                    COUNT(*) AS booking_count
                FROM courier_booking
                WHERE selected_mode_id IS NOT NULL
                GROUP BY selected_mode_id, state
            )
        """)
