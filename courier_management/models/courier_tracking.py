from odoo import models, fields,_,api
from odoo.exceptions import UserError

class CourierTracking(models.Model):
    _name = "courier.tracking"
    _inherits = {'courier.booking':'booking_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']   
    _description = 'Courier Tracking'
    _rec_name = 'booking_id'

    booking_id = fields.Many2one('courier.booking')
    agent_id = fields.Many2one('delivery.agent')
    timestamp = fields.Datetime(string='Status timestamp',tracking=True)
    notes = fields.Text(string='Additional tracking info')
    complain_id = fields.One2many('customer.complaint','tracking_id')
    count_complain = fields.Integer()
    tracking_id = fields.Char()
    status = fields.Selection([('pick_up','Pick-Up'),
                               ('in_transit','In-transit'),
                               ('out_for_delivery','Out for delivery'),
                               ('delivered','Delivered'),
                               ('returned','Returned')])
   
    

    def action_pick_up(self):
        self.booking_id.state = 'picked'
        self.status = 'pick_up'
        self.booking_id.pickup_time = fields.Datetime.now()

    def action_in_transit(self):
        self.booking_id.state = 'in_transit'
        self.status = 'in_transit'
        self.timestamp = fields.Datetime.now()
        self.booking_id.in_transit_time = fields.Datetime.now()

    def action_out_for_delivery(self):
        self.booking_id.state = 'out_for_delivery'
        self.status = 'out_for_delivery'
        self.timestamp = fields.Datetime.now()
        self.booking_id.out_for_delivery_time = fields.Datetime.now()


    def action_delivered(self):
        self.booking_id.state = 'delivered'
        self.status = 'delivered'
        self.timestamp = fields.Datetime.now()
        # self.booking_id.delivered_time = fields.Datetime.now()

        return {
                'type': 'ir.actions.act_window',
                'name': 'Delivery Details',
                'view_mode': 'form',
                'res_model': 'courier.delivered',
                'target': 'new',
                'context': {
                    'default_booked_id': self.booking_id.id,
                },
            }
    
    def action_complain_customer(self):
        complains = self.env['customer.complaint'].search([('booking_id', '=', self.id)])
        self.count_complain = len(complains)
        # count = len(complains)
        # print("\n\n\n\n",count)
        if not complains:
            raise UserError('No complaints found for this booking.')
        return {   
            "type": "ir.actions.act_window",
            "name": "Complaints",
            "view_mode": "list,form",
            "res_model": "customer.complaint",
            "domain": [("id", "in", complains.ids)],
            "target": "current"
        }
    
class CourierDelivered(models.TransientModel):
    _name = "courier.delivered"
     
    booked_id = fields.Many2one('courier.booking')
    name = fields.Many2one('res.partner', string='Name')
    delivery_time = fields.Datetime(string='Delivery Time', default = fields.Datetime.now())
    delivery_proof = fields.Binary()


    def action_delivered_details(self):
        # print("\n\n\n\n\n\n>>>>>>>>>>>>>",self.env.context)
        self.booked_id.receiver_id = self.name
        self.booked_id.delivered_time = self.delivery_time
        self.booked_id.delivery_proof = self.delivery_proof
        

    def action_return(self):
        self.booked_id.state = 'returned'
        self.booked_id.tracking_id.status = 'returned'