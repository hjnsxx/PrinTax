# -*- coding: utf-8 -*-
# Módulo que define el método print_invoice, que envía la factura al impresor fiscal a traves de PrinTax
#
# Esta versión maneja dos operaciones, la primera se encarga de armar el mensaje y la segunda guarda los datos
# se hace de esta manera porque no se puede enviar un mensaje desde el servidor al PrinTax cuando el equipo está
# en la nube
#
# Versión 1.0.0 - 2020.09.11 - Hernán Navarro
# Versión 1.0.1 - 2020.09.27

import logging

from datetime import datetime, timedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.http import request

import base64
import requests

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    # definición de los campos que reciben la información que retorna el PrinTax
    ptx_fiscal_invoice = fields.Char("Número de factura fiscal impresa", size = 10)
    ptx_serial_printer = fields.Char("Serial del impresor fiscal", size = 12)
    ptx_printing_date = fields.Datetime('Fecha y hora de impresión de la factura fiscal')
    ptx_base_imponible = fields.Float('Total de la base imponible')
    ptx_impuesto_printer = fields.Float('IVA calculado por el impresor')
    ptx_reporte_z = fields.Char("Número de reporte Z asociado a la factura", size = 6)

    def printax_print_invoice(self, origen, nro_orden):
        # _logger.info("printax_print_invoice - Entrando a la función")

        if origen == 1:
            # _logger.info("Origen = 1")
            id_order = self.env['pos.order'].search([('pos_reference', 'like', '%' + nro_orden)])
        else:
            # _logger.info("Origen != 1")
            id_order = self.env['pos.order'].search([('name', '=', nro_orden)])

        # _logger.info("id_order: ")
        # _logger.info(id_order);
        # _logger.info("Get mlOrder")
        mdlOrder = self.env['pos.order'].sudo().browse(id_order.id)

        # _logger.info("Get mlPrinter")
        mdlPrinter = self.env['pos.config'].sudo().browse(mdlOrder.config_id.id)

        # Si el campo ptx_fiscal_invoice no es nulo es que ya se imprimió esta factura
        if mdlOrder.ptx_fiscal_invoice != False:
            cmd = "TIP=RFA\n"
            cmd += "FNO=" + mdlOrder.ptx_fiscal_invoice;
            cmd = base64.b64encode(cmd.encode('utf-8'))

            # _logger.info("Factura ya fué impresa")

            return {
                'tip': "ERR",
                'err': "Factura ya fué impresa",
            }

        # _logger.info("Get mdlPartner")
        mdlPartner = self.env['res.partner'].sudo().browse(mdlOrder.partner_id.id)

        dTasa = 1.0
        if mdlOrder.currency_id.id != mdlPrinter.printax_currency.id:
            mdlMoney = self.env['res.currency'].sudo().browse(mdlPrinter.printax_currency.id)
            dTasa = mdlMoney.rate

        cmd = "TIP=FAC\n"
        if mdlPartner.vat == False:

            # _logger.info("Falta la identificación fiscal")

            return {
                'tip': "ERR",
                'err': "Falta la identificación fiscal",
            }
        else:
            cmd += "NRF=" + mdlPartner.vat + "\n"

        if mdlPartner.name == False:

            # _logger.info("Falta el nombre del cliente")

            return {
                'tip': "ERR",
                'err': "Falta el nombre del cliente",
            }
        else:
            cmd += "CNM=" + mdlPartner.name + "\n"

        cmd += "TXT=Orden " + nro_orden + "\n"

        strAddress = ""
        if mdlPartner.street != False:
            strAddress = mdlPartner.street
        if mdlPartner.street2 != False:
            if strAddress != "":
                strAddress += ", "
            strAddress += ", " + mdlPartner.street2
        if mdlPartner.city != False:
            if strAddress != "":
                strAddress += ", "
            strAddress += mdlPartner.city

        if strAddress != "":
            cmd += "TXT=" + strAddress + "\n"

        if mdlPartner.phone != False:
            cmd += "TXT=Telefono " + mdlPartner.phone + "\n"

        # Cada línea debe tener el porcentaje de IVA, este porcentaje debe estar registrado en el impresor fiscal
        # se coloca 0 cuando es exento de impuesto

        for lines in mdlOrder.lines:
            cmd += "PRD="

            mdlTax = self.env['account.tax'].sudo().browse(lines.tax_ids.id)
            if mdlTax.amount == False:
                taxRate = "0"
            else:
                taxRate = mdlTax.amount

            dPrecio = lines.price_unit * dTasa

            cmd += str(taxRate) + ","
            cmd += str(dPrecio) + ","
            cmd += str(lines.qty) + ","
            cmd += lines.display_name + "\n"

        cmd += "SUT=1\n"
        cmd = base64.b64encode(cmd.encode('utf-8'))

        # _logger.info("Factura armada")

        return {
            'tip': "COK",
            'ip': mdlPrinter.printax_ip,
            'port': mdlPrinter.printax_port,
            'msg': cmd,  # .decode("utf-8")
            'ord': id_order.id
        }

    def update_invoice(self, nro_orden, strFac, strSer, strFec, strVta, strIva, strRpz):
        mdlOrder = self.env['pos.order'].sudo().browse(nro_orden)
        mdlOrder.update(
        {
            'ptx_fiscal_invoice': strFac,
            'ptx_serial_printer': strSer,
            'ptx_printing_date': strFec,
            'ptx_base_imponible': strVta,
            'ptx_impuesto_printer': strIva,
            'ptx_reporte_z': strRpz
        })
