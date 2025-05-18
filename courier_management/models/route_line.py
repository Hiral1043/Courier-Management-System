from odoo import models, fields, api

class RouteLine(models.Model):
    _name = 'route.line'
    _description = 'Route Line'
    _rec_name = 'route_id'
       
    route_id = fields.Many2one('shipping.route', string='Route', required=True)
    mode_id = fields.Many2one('shipping.mode', string='Shipping Mode', required=True)
    cost_per_kg = fields.Float(string='Cost per KG', required=True)
    estimated_days = fields.Integer(string='Estimated Days', required=True)
    is_active = fields.Boolean(string='Is Active', default=True,store=True)    