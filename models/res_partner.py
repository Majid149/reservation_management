from odoo import fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'
    reservation_ids = fields.One2many('reservation.reservation', 'client')
