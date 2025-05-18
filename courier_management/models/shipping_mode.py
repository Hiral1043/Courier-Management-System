from odoo import models,api,fields

class ShippingMode(models.Model):
    _name = 'shipping.mode'
    _description = 'Shipping Mode'

    name = fields.Char(string='Shipping Mode Name', required=True)
    speed_rank = fields.Selection([
        ('low', 'Cheapest'),
        ('medium', 'Balanced'),
        ('high', 'Fastest'),
    ], string='Speed Rank')