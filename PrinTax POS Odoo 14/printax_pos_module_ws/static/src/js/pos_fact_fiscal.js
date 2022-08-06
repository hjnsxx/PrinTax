// Modulo de impresión de factura fiscal para punto de venta 
// Versión 1.0.0 - 2020.09.11 - Hernán Navarro
// Versión 1.1.0 - 2022.07.10 - Adaptatación a Odoo 14 / 15

odoo.define('printax_pos_module_ws.ReceiptScreenButton', function(require)
{
	"use strict";

	// const { Gui } = require('point_of_sale.Gui');
	// const PosComponent = require('point_of_sale.PosComponent');
	// const { posbus } = require('point_of_sale.utils');
	// const { useListener } = require('web.custom_hooks');
	const Registries = require('point_of_sale.Registries');
	const ReceiptScreen = require('point_of_sale.ReceiptScreen');
	var rpc = require('web.rpc');

	const CustomButtonReceiptScreen = (ReceiptScreen) =>
		class extends ReceiptScreen
		{
			constructor()
			{
				super(...arguments);
			}

			OnPrintFactFiscal()
			{
				var IdOrder = this.env.pos.get_order().uid;
				rpc.query(
				{
					model: 'pos.order',
					method: 'printax_print_invoice',
					args: [ 0, 1, IdOrder ]
				}).then(function(resp)
					{
						if(resp.tip == "COK")
						{
							var NameOrder = resp.ord;

							var comando = 'http://'
							comando += resp.ip
							comando += ':'
							comando += resp.port
							comando += '/sendcmd/'
							comando += resp.msg

							var xhr = new XMLHttpRequest;
							xhr.open("GET", comando, true);
							xhr.send(null);

							xhr.onload = function()
							{
								if(xhr.status != 200)
								{
									console.log('Error ${xhr.status}: ${xhr.statusText}');
								}
								else
								{
									var resp = JSON.parse(xhr.responseText)

									if(resp.TIP == "COK")
									{
										rpc.query(
										{
											model: 'pos.order',
											method: 'update_invoice',
											args: [ 0,
													NameOrder,
													resp.FAC,
													resp.SER,
													resp.FEC,
													resp.VTA,
													resp.IVA,
													resp.RPZ ]
										}).then(function(resp){});
									}
									else
									{
										alert(resp.ERR);
									}
								}
							};

							xhr.onprogress = function(event)
							{
							};

							xhr.onerror = function()
							{
								console.log("Request failed");
							};
						}
						else
						{
							alert(resp.err);
						}
					});
			}
		};

	Registries.Component.extend(ReceiptScreen, CustomButtonReceiptScreen);
	return CustomButtonReceiptScreen;
});

