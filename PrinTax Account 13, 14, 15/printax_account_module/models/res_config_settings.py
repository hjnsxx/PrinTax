# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    printax_ip = fields.Char(string='IP del equipo que está ejecutando el PrinTax', default='192.168.1.100', size = 16, config_parameter='printax.ip')
    printax_port = fields.Char(string='Puerto que atiene el PrinTax', default='5125', size = 6, config_parameter='printax.port')
