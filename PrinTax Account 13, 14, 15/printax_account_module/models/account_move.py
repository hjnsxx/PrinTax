# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.http import request
from odoo.exceptions import UserError

import json
import base64
import requests

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    # definición de los campos que reciben la información que retorna el PrinTax
    ptx_fiscal_invoice = fields.Char("Número de factura fiscal impresa", size = 10)
    ptx_serial_printer = fields.Char("Serial del impresor fiscal", size = 12)
    ptx_printing_date = fields.Datetime('fecha y hora de impresión de la factura fiscal')
    ptx_base_imponible = fields.Float('Total de la base imponible')
    ptx_impuesto_printer = fields.Float('IVA calculado por el impresor')
    ptx_reporte_z = fields.Char("Número de reporte Z asociado a la factura", size = 6)

    @api.model
    def imprimir_factura_fiscal(self, id_move):
#       _logger.info("En imprimir_factura_fiscal")

        mdlMove = self.env['account.move'].sudo().browse(id_move[0])
        mdlPartner = self.env['res.partner'].sudo().browse(mdlMove.partner_id.id)
        
        if mdlPartner.vat == False:
            raise UserError("El cliente debe tener el número de registro fiscal")
            return
        
        strType = mdlMove.type

#       _logger.info("strType " + strType)

        bReimpresion = False
        strCmd = ""

        # si ya existe envía hace reimpresión
        
        if mdlMove.ptx_fiscal_invoice != False:
#       if False:
            bReimpresion = True
        
            if strType == "out_invoice":
                strCmd += "TIP=RFA\n"
                strCmd += "FNO=" + str(mdlMove.ptx_fiscal_invoice).lstrip("0") + "\n"
            else:
                strCmd += "TIP=RCR\n"
                strCmd += "NNC=" + str(mdlMove.ptx_fiscal_invoice).lstrip("0") + "\n"
        else:
            if strType == "out_invoice":
                strCmd += "TIP=FAC\n"

            if strType == "out_refund":
                strCmd += "TIP=NCR\n"

                if mdlMove.ref == False:
                    raise UserError("Se debe colocar el número de factura original en 'Referencia'")
                    return
                    
                IdOrigen = self.env['account.move'].sudo().search([('name', '=', mdlMove.ref)])
                mdlFactOrig = self.env['account.move'].sudo().browse(IdOrigen.id)

                if mdlFactOrig == False:
                    raise UserError("Factura original en 'Referencia' no encontrada")
                    return

                strCmd += "FNO=" + str(mdlFactOrig.ptx_fiscal_invoice) + "\n"
                strCmd += "SRP=" + mdlFactOrig.ptx_serial_printer + "\n"
                strCmd += "FFO=" + mdlFactOrig.ptx_printing_date.strftime("%Y%m%d%H%M%S") + "\n"

            strCmd += "NRF=" + str(mdlPartner.vat) + "\n"
            strCmd += "CNM=" + str(mdlPartner.name) + "\n"
            
            if mdlPartner.street != False:
                strCmd += "TXT=" + mdlPartner.street + "\n"
                
            if mdlMove.name != False:
                strCmd += "TXT=Doc: " + mdlMove.name + "\n"
                
    #       strCmd += "TXT=Telefono " + str(mdlPartner.phone) + "\n"

            # Cada línea debe tener el porcentaje de IVA, este porcentaje debe estar registrado en el impresor fiscal
            # se coloca 0 cuandidso es exento de impuesto

            for lstProducto in mdlMove.invoice_line_ids:
                mdlProducto = self.env['account.move.line'].sudo().browse(lstProducto.id)
                mdlProd = self.env['product.product'].sudo().browse(mdlProducto.product_id.id)

                strCmd += "PRD="

                if mdlProducto.tax_ids:
                    mdlTax = self.env['account.tax'].sudo().browse(mdlProducto.tax_ids.id)
                    strCmd += str(mdlTax.amount) + ","
                else:
                    strCmd += "0,"

                strCmd += str(mdlProducto.price_unit) + ","
                strCmd += str(mdlProducto.quantity) + ","
                strCmd += mdlProd.display_name + "\n"
                
            lstPagos = json.loads(mdlMove.invoice_payments_widget)
            
            if lstPagos != False:
                for Pagos in lstPagos['content']:
                    mdlPayment = self.env['account.payment'].sudo().browse(Pagos['account_payment_id'])
                    mdlCurrency = self.env['res.currency'].sudo().browse(mdlPayment.currency_id.id)
                    
                    fMonto = mdlPayment.amount * mdlCurrency.rate;
                    
                    strCmd += "IDP=" + mdlCurrency.printax_idp + "," + str(fMonto) + "\n"

            strCmd += "SUT=1\n"
        
#        _logger.info(strCmd)

        strCmd = base64.b64encode(strCmd.encode('utf-8'))

        printax_ip = self.env['ir.config_parameter'].sudo().get_param('printax.ip')
        printax_port = self.env['ir.config_parameter'].sudo().get_param('printax.port')

        try:
            respuesta = requests.get('http://' + str(printax_ip) + ':' + str(printax_port) + '/sendcmd/' + strCmd.decode("utf-8"), timeout=20)
        except requests.exceptions.RequestException as e:
             raise UserError("Problemas de comunicación con PrinTax")
             return
        
        respuesta = respuesta.json()

        if 'ERR' in respuesta:
            raise UserError(respuesta['ERR'])
            return

        if bReimpresion == False:
            if strType == "out_invoice":
                mdlMove.update({
                        'ptx_fiscal_invoice': respuesta['FAC'],
                        'ptx_serial_printer': respuesta['SER'],
                        'ptx_printing_date': respuesta['FEC'],
                        'ptx_base_imponible': respuesta['VTA'],
                        'ptx_impuesto_printer': respuesta['IVA'],
                        'ptx_reporte_z': respuesta['RPZ']
                    })
                    
            if strType == "out_refund":
                mdlMove.update({
                        'ptx_fiscal_invoice': respuesta['NCR'],
                        'ptx_serial_printer': respuesta['SER'],
                        'ptx_printing_date': respuesta['FEC'],
                        'ptx_base_imponible': respuesta['VTA'],
                        'ptx_impuesto_printer': respuesta['IVA'],
                        'ptx_reporte_z': respuesta['RPZ']
                    })
