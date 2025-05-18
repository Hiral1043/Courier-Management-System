from odoo import models,Command, fields
import random 

class DeliveryAgent(models.Model):
    _name = 'delivery.agent'
    _description = 'Delivery Agent'

    name = fields.Many2one('res.partner',string='Agent name' ,related='user_id.partner_id')
    user_id = fields.Many2one('res.users')
    is_available = fields.Boolean(string='Availability status')


class AssignDeliveryAgent(models.TransientModel):
    _name = "assign.delivery.agent"

    name = fields.Many2one('delivery.agent')
    booking_id = fields.Many2one('courier.booking')
    courier_tracking_id = fields.Char()
    def action_assign(self):
        print(">>>>>>>>>>>>",self.env.context)
        context = dict(self.env.context)
        context.update({
            'partner_id' : self.name.id
        })
        self.env.context = context
        self.booking_id.agent_id = self.env.context.get('partner_id')
        self.courier_tracking_id = random.randrange(11111, 99999, 5)
        print("\n\n\n\n\n\n>>>>>>>>>>>>courier_tracking_id",self.courier_tracking_id)
        
        # existing_tracking = self.env['courier.tracking'].search([('booking_id', '=', self.booking_id.id)], limit=1)
        # if not existing_tracking:
        tracking_vals = {
        'agent_id': self.name.id,
        'booking_id': self.booking_id.id,
        'timestamp': fields.Datetime.now(),
        'tracking_id' : self.courier_tracking_id
        }
        print("\n\n\n\n>>>>>>>>>>>>tracking_vals",tracking_vals)
        self.env['courier.tracking'].create(tracking_vals)

