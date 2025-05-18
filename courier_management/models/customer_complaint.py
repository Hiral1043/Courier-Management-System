from odoo import models,Command, fields,_,api
from datetime import datetime
class CustomerComplaint(models.Model):
    _name = 'customer.complaint'
    _description = 'Customer Complaint'
    _rec_name = "ticket_number"

    ticket_number = fields.Char(string="Ticket Number",required=True, copy=False, readonly=False,
        default= lambda self: _('New'))
    booking_id = fields.Many2one(
        'courier.booking', 
        string="Booking",domain="[('sender_id','=',partner_id)]" 
    )
    partner_id = fields.Many2one(
        'res.partner', 
        string='Customer', 
        default=lambda self: self.env.user.partner_id, 
        readonly=True
    )
    complaint_category = fields.Selection([
        ('delay','Delay'),
        ('damage','Damage'),
        ('wrong_delivery','Wrong Delivery'),
        ('payment_issue','Payment Issue')])
    description = fields.Text(string='Complaint detail')
    attachment = fields.Binary()
    assigned_to = fields.Many2one('res.users',required=True)
    # related='booking_id.assigned_id.name.user_id'
    status = fields.Selection([
        ('open','Open'),
        ('in_progress','In-progress'),
        ('resolved','Resolved'),
        ('closed','Closed')],string='Status' ,default='open',required=True)
    priority = fields.Selection([
        ('low','Low'),
        ('medium','Medium'),
        ('high','High')],string='Priority')
    create_date = fields.Datetime(string="Created On", readonly=True)
    resolution_deadline = fields.Datetime(string='Target resolution date',required=True)
    resolution_time = fields.Integer(string="Resolution Time (Days)", compute='_compute_resolution_time', store=True)
    description = fields.Text()
    internal_notes = fields.Text(string='Admin notes')
    tracking_id = fields.Many2one('courier.tracking')

    @api.model
    def create(self,vals):
        if vals.get('ticket_number',_('New')) == _('New'):
            vals['ticket_number'] = self.env['ir.sequence'].next_by_code('customer.complaint') or _('New')
        return super().create(vals)
    
    def action_resolved(self):
        self.status = 'resolved'
        self.resolution_deadline = fields.Datetime.now()
    

    def action_close(self):
        self.status = 'closed'

    @api.onchange('assigned_to')
    def _onchange_assigned_to(self):
        self.status = 'in_progress'


    @api.depends('create_date', 'resolution_deadline')
    def _compute_resolution_time(self):
        for i in self:
            if i.create_date and i.resolution_deadline:
                i.resolution_time = (i.resolution_deadline.date() - i.create_date.date()).days
            else:
                i.resolution_time = 0.0