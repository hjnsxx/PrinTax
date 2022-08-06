// Impresion de factura fiscal desde lista de ordenes

odoo.define("printax_pos.order_print_fisc", function(require) 
{
	"use strict";

	var bPar = false;

	var Widget = require('web.Widget');
	var rpc = require("web.rpc");

	Widget.include(
	{
		events: 
		{
			'click .css_print_fact_button': '_print_fac_fis',
		},

		_print_fac_fis: function(param)
		{
			// esta rutina es porque el evento es llamado 2 veces
			
			if(bPar == true)
			{
				bPar = false;
				return;
			}
			bPar = true;
			
//			console.log(this);
//			console.log(this.state.data.id);

			var IdOrder = this.state.data.name;

			rpc.query(
			{
				model: "pos.order",
				method: "print_invoice",
//				args: [ 0, this.state.data.id ]
				args: [ 0, 2, IdOrder ]
			}).then(function(resp) 
				{
					var bReimpresio = false;
					
					if(resp.tip == "ERR")
					{
						alert(resp.ERR);
						return;
					}
					
					var NameOrder;
					
					if(resp.tip == "COK")
						NameOrder = resp.ord;
					else
						bReimpresio = true;
						
					var comando = "http://"
					comando += resp.ip
					comando += ":"
					comando += resp.port
					comando += "/sendcmd/"
					comando += resp.msg

					var xhr = new XMLHttpRequest;
					xhr.open("GET", comando, true);
					xhr.send(null);
					
					xhr.onload = function() 
					{
						if(xhr.status != 200) 
						{ 
							console.log("Error ${xhr.status}: ${xhr.statusText}");
						} 
						else 
						{ 
							var resp = JSON.parse(xhr.responseText)
							
							if(resp.TIP == "COK")
							{
								if(bReimpresio == false)
								{
									rpc.query(
									{
										model: "pos.order",
										method: "update_invoice",
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
							}
							else
							{
								alert(resp.ERR);
							}
						}
					};	

					xhr.onprogress = function(event) 
					{
	/*							
						if(event.lengthComputable) 
						{
							console.log(`Received ${event.loaded} of ${event.total} bytes`);
						} 
						else 
						{
							console.log(`Received ${event.loaded} bytes`); // no Content-Length
						}
						
						console.log(xhr.responseText);
	*/
					};

					xhr.onerror = function() 
					{
						console.log("Request failed");
					};
				});
		}
	});
	
	return Widget;
});
