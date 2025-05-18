from odoo import models,api,fields

class ShippingRoute(models.Model):
    _name = 'shipping.route'
    _description = 'Shipping Route'

    name = fields.Char(string='Name', compute='combine_rec_name', store=True)

    source_city = fields.Char(string='Source City', required=True)
    destination_city = fields.Char(string='Destination City', required=True)
    distance_km = fields.Float(string='Distance (KM)', required=True)
    route_line_ids = fields.One2many('route.line', 'route_id', string='Route Lines')
    
    @api.depends('source_city', 'destination_city')
    def combine_rec_name(self):
        for record in self:
            record.name = f"{record.source_city} to {record.destination_city}"