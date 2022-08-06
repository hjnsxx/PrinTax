# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PosConfig(models.Model):
    _inherit = 'pos.config'

    printax_ip = fields.Char(string='IP del equipo que está ejecutando el PrinTax', default='192.168.1.100', size = 16)
    printax_port = fields.Char(string='Puerto IP del PrinTax', default='5125', size = 6)
    printax_currency = fields.Many2one('res.currency', string = "Moneda de factura fiscal")
