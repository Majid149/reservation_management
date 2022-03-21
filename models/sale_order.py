from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    reservation_ids = fields.One2many('reservation.reservation', 'order_id')
    reservation_count = fields.Integer(compute='_compute_reservation_count', store=True)

    @api.depends('reservation_ids')
    def _compute_reservation_count(self):
        for record in self:
            record.reservation_count = len(record.reservation_ids)

    def action_view_reservations(self):
        action = self.env['ir.actions.act_window']._for_xml_id('reservation.reservation_action')
        if len(self.reservation_ids) == 1:
            print('action_view_reservation')
            action['view_mode'] = 'form'
            action['res_id'] = self.reservation_ids.id
            action['views'] = []
        else:
            action['domain'] = [('id', 'in', self.reservation_ids.ids)]
            action['context'] = []
        return action
        # action = self.env.ref('reservation.sales_action')
        # if self.reservation_count > 1:
        #     action['domain'] = [('id', 'in', self.reservation_ids.ids)]
        # elif self.reservation_ids:
        #     form_view = [(self.env.ref('reservation.reservation_view_id').id, 'form')]
        #     action['views'] = form_view
        #     action['res_id'] = self.reservation_ids.ids
