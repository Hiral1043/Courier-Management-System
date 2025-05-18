from odoo import models,Command,fields,_,api
from odoo.exceptions import UserError

class CourierBooking(models.Model):
    
    _name = 'courier.booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Courier Booking'
    _rec_name = 'tracking_id'

    tracking_id = fields.Char(string="Tracking ID",required=True, copy=False, readonly=False,
                    default= lambda self: _('New'))
    sender_id = fields.Many2one('res.partner', string='Name', required=True)
    receiver_id = fields.Many2one('res.partner', string='Name', readonly=True)
    #Sender address fields
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    sender_phone = fields.Char(string="Phone Number", required=True)
    # receriver address fields
    receiver_phone = fields.Char(string="Phone Number", required=True)

    receiver_street = fields.Char()
    receiver_street2 = fields.Char()
    receiver_zip = fields.Char(change_default=True)
    receiver_city = fields.Char()
    receiver_state_id = fields.Many2one("res.country.state", string='State')
    receiver_country_id = fields.Many2one('res.country', string='Country')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    weight = fields.Float(string='Weight', required=True)
    dimensions = fields.Char(string='Dimensions', required=True)
    delivery_priority = fields.Selection([
                        ('low', 'Cheapest'),
                        ('medium', 'Balanced'),
                        ('high', 'Fastest'),
                        ('all','All')
                        ], string='Delivery Priority', required=True)
    suggested_modes_ids = fields.One2many('shipping.suggestion', 'booking_id', string='Suggested Modes')
    selected_mode_id = fields.Many2one('shipping.mode', string='Shipping Mode')
    route_id = fields.Many2one('shipping.route', string='Route' ,readonly=True)
    cost = fields.Monetary(string='Cost', currency_field='currency_id',readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)
    delivery_estimate = fields.Integer(string='Delivery Estimate (Days)',readonly=True)
    state = fields.Selection([
                            ('draft', 'Draft'),
                            ('confirmed', 'Confirmed'),
                            ('invoiced', 'Invoiced'),
                            ('picked', 'Picked'),
                            ('in_transit', 'In-transit'),
                            ('out_for_delivery', 'Out for Delivery'),
                            ('delivered', 'Delivered'),
                            ('returned', 'Returned')
                        ], string='State', default='draft')
    # line_id = fields.Many2one('route.line')
    agent_id = fields.Many2one('delivery.agent', string='Assigned agent')
    pickup_time = fields.Datetime(string='Scheduled pickup')
    delivery_proof = fields.Binary()
    invoice_id = fields.Many2one("account.move", string="Invoice")
    assigned_id = fields.One2many('assign.delivery.agent','booking_id')
    ticket_id = fields.Char(related='assigned_id.ticket_id' ,string = "Ticket ID")


    @api.model
    def create(self,vals):
        if vals.get('tracking_id',_('New')) == _('New'):
            vals['tracking_id'] = self.env['ir.sequence'].next_by_code('courier.booking') or _('New')
        return super().create(vals)
    
    
    @api.constrains('sender_phone','receiver_phone')
    def validate_phone(self):
        for record in self:
            if not (record.sender_phone.isdigit() and len(record.sender_phone) == 10):
                raise UserError('phone number must be of 10 digit and numeric') 
            if not (record.receiver_phone.isdigit() and len(record.receiver_phone) == 10):
                raise UserError('phone number must be of 10 digit and numeric') 
    

    @api.constrains('weight')
    def validate_weight(self):
        for record in self:
            if record.weight <= 0:
                raise UserError('Weight must be positive') 
    

    def action_show_suggestion(self):
        for rec in self:
            found_routes = self.env['shipping.route'].search([
            ('source_city', '=ilike', rec.city),
            ('destination_city', '=ilike', rec.receiver_city)])
            if found_routes:
                rec.suggested_modes_ids = [5, 0, 0]
            active_routes = found_routes.route_line_ids.filtered(lambda x:x.is_active)
            for route in active_routes:
                route_lines = route.filtered(lambda route_line: route_line.mode_id.speed_rank == rec.delivery_priority)
                for line in route_lines:
                    rec.suggested_modes_ids = [(0, 0, {
                        'booking_id': rec.id,
                        'route_line_id': line.id,
                        'estimated_days': line.estimated_days,
                        'estimated_cost': line.cost_per_kg,
                        'total_cost' : line.cost_per_kg * rec.weight
                    })]
                        
            if self.delivery_priority == 'all':
                rec.suggested_modes_ids = [5, 0, 0]
                for record in found_routes.mapped('route_line_ids'):
                    rec.suggested_modes_ids = [(0, 0, {
                        'booking_id': rec.id,
                        'route_line_id': record.id,
                        'estimated_days': record.estimated_days,
                        'estimated_cost': record.cost_per_kg,
                        'total_cost' : record.cost_per_kg * rec.weight
                    })]


    
    def action_confirm(self):
        self.state = 'confirmed'
    def action_deliver(self):
        pass

    def action_assign_delivery_agent(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assign Delivery Agent',
            'view_mode': 'form',
            'res_model': 'assign.delivery.agent',
            'target': 'new',
            'context': {
                'default_booking_id': self.id,
                # 'default_sender_id': self.sender_id.id,
                # 'default_receiver_id': self.receiver_id.id,
                # 'default_weight': self.weight,
                # 'default_dimensions': self.dimensions,
                # 'default_delivery_priority': self.delivery_priority,
            },
        }
        



    def action_invoice(self):
        journal = self.env["account.journal"].search([('type', '=', 'sale')], limit=1)
        sender_id = self.env['res.partner'].create({
                'name':self.sender_id.name
            })
        invoice_lines = []
        invoice_lines.append(
            Command.create({
                'name': sender_id.name,
                'quantity': self.weight,  
                'price_unit': self.cost,  
            })
        )
        invoice = self.env["account.move"].create({
            'journal_id': journal.id,
            'move_type': 'out_invoice',  
            'partner_id': sender_id.id,
            'invoice_date': fields.Date.today(), 
            'invoice_line_ids': invoice_lines  
        })
        self.invoice_id = invoice.id
      
        self.state = 'invoiced'
        return {   
            "type": "ir.actions.act_window",
            "name": "Customer Invoice",
            "view_mode": "list,form",
            "res_model": "account.move",
            "res_id": invoice.id,
            "domain": [("id", "=", self.invoice_id.id)],
            "target": "current"
        }
        