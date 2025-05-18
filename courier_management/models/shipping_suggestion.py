from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ShippingSuggestion(models.Model):
    _name = 'shipping.suggestion'
    _description = 'Shipping Suggestion'

    booking_id = fields.Many2one('courier.booking', string='Booking Reference')
    route_line_id =fields.Many2one('route.line')
    estimated_days = fields.Integer(string='Estimated Days')
    estimated_cost = fields.Float(string='Estimated Cost(per kgs)')
    total_cost = fields.Float(string='Total Cost')
 
    def action_selected_route(self):
        for rec in self:
            self.booking_id.state = 'confirmed'
            self.booking_id.cost = rec.estimated_cost
            self.booking_id.delivery_estimate = rec.estimated_days
            self.booking_id.route_id = rec.route_line_id.route_id.id
            self.booking_id.selected_mode_id = rec.route_line_id.mode_id.id