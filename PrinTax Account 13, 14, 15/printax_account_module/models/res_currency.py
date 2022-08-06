# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResCurrency(models.Model):
    _inherit = 'res.currency'

    printax_idp = fields.Char(string='Código fiscal del instrumento de pago para PrinTax', default='01', size = 2, config_parameter='printax.idp')

