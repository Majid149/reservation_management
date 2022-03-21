from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from odoo.exceptions import ValidationError


class Reservation(models.Model):
    _name = 'reservation.reservation'
    _description = 'This is the reservation model'
    _rec_name = 'reference'

    reference = fields.Char(required=True, readonly=True, default='New Reservation')
    client = fields.Many2one('res.partner', required=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=True)
    article = fields.Text(required=True)
    reservation_date = fields.Datetime(default=lambda self: fields.Datetime.now())
    duration = fields.Integer()
    duration_month = fields.Integer(default=0)
    duration_day = fields.Integer(default=0)
    duration_hour = fields.Integer(default=0)
    report = fields.Many2one('reservation.activity.report')
    end_reservation = fields.Datetime(compute='_compute_end_reservation')
    price_unit = fields.Float(compute='_compute_price_unit')
    order_id = fields.Many2one('sale.order', string='Order Reference', store=True)
    total_duration_hours = fields.Float(compute='_compute_duration_hours', string='Duration in hours', store=True)
    state = fields.Selection([
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('validated', 'Validated'),
        ('canceled', 'Canceled'),
        ('closed', 'Closed')
    ], default='new')

    @api.depends('duration_hour', 'duration_day', 'duration_month')
    def _compute_price_unit(self):
        for rec in self:
            if (rec.duration_day == 0 and rec.duration_month == 0) and rec.duration_hour < 10:
                rec.price_unit = 150
            else:
                rec.price_unit = 140

    @api.depends('duration_hour', 'duration_day', 'duration_month')
    def _compute_duration_hours(self):
        for rec in self:
            rec.total_duration_hours = rec.duration_day * 24 + rec.duration_hour + rec.duration_month * 30 * 24

    def action_new(self):
        self.state = 'new'

    def action_confirm(self):
        self.state = 'confirmed'

    def action_validate(self):
        self.state = 'validated'

    def action_close(self):
        self.state = 'closed'

    def action_cancel(self):
        self.state = 'canceled'

    def action_quote_button(self):
        vals = {
            'origin': self.reference,
            'user_id': self.user_id.id,
            'partner_id': self.client.id,
            'order_line': [(0, 0, {
                'product_id': self.env['product.product'].create({'name': self.reference}).id,
                'name': self.article,
                'product_uom_qty': self.total_duration_hours,
                'price_unit': 150 if self.total_duration_hours < 10 else 140,
            })]
        }
        sale_order = self.env['sale.order'].create(vals)
        self.order_id = sale_order
        # product = self.env['product.product'].create({'name': self.reference, })
        # self.env['sale.order.line'].create({
        #     'product_id': product.id,
        #     'order_id': sale_order.id,
        #     'name': self.article,
        #     'product_uom_qty': self.total_duration_hours,
        #     'price_unit': self.price_unit,
        #             })
        return sale_order

    def action_generate_multiple_quotes(self):
        reservations = self.env['reservation.reservation'].browse(self._context.get('active_ids', []))
        # print('/'.join([r.reference for r in reservations]))
        # Reservations grouped by client
        clients = {}
        for reservation in reservations:
            if reservation.client in clients:
                clients[reservation.client] += reservation
            else:
                clients[reservation.client] = reservation
        # print([reservation.state for client in clients for reservation in clients[client]])
        selected_reservation_states = [reservation.state for client in clients for reservation in clients[client]]
        states_without_validated = ['canceled', 'confirmed', 'closed', 'new']

        # print(len([i for i in states_without_validated if i in selected_reservation_states]))

        if len([i for i in states_without_validated if i in selected_reservation_states]) > 0:
            raise ValidationError('There are reservations that are not validated yet !')
        else:
            for client in clients:
                # print('-------')
                # print(client)
                sale_order = self.env['sale.order'].create({
                    'origin': '/'.join([r.reference for r in clients[client]]),
                    'partner_id': client.id,
                    'user_id': self.user_id.id,
                    'date_order': fields.Datetime.now(),
                    'order_line': [(0, 0, {
                        'product_id': self.env['product.product'].create({'name': reservation.reference}).id,
                        'name': reservation.article,
                        'product_uom_qty': reservation.total_duration_hours,
                        'price_unit': 150 if reservation.total_duration_hours < 10 else 140,
                    }) for reservation in clients[client]]
                })
                # print(sale_order.id)
                for reservation in clients[client]:
                    reservation.order_id = sale_order.id

    @api.depends('reservation_date', 'duration_month', 'duration_day', 'duration_hour')
    def _compute_end_reservation(self):
        for rec in self:
            if rec.reservation_date:
                rec.end_reservation = rec.reservation_date + timedelta(days=rec.duration_day) \
                                      + relativedelta(months=rec.duration_month) \
                                      + timedelta(hours=rec.duration_hour)
            else:

                rec.end_reservation = fields.Datetime.today()

    @api.model
    def create(self, vals):
        if vals.get('reference', 'New Reservation') == 'New Reservation':
            vals['reference'] = self.env['ir.sequence'].next_by_code('reservation.reservation') or 'New'
            # vals['reference'] = self.env['ir.sequence'].get('reservation.reservation') or '/'
        res = super(Reservation, self).create(vals)
        return res
