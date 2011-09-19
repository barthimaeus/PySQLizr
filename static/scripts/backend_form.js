function load_table(table) {
	$.post(
		"/backend",
		{"table": table},
		function(data){
			$("#editor").html(data["editortemplate"]);
			$("#editortitle").html("Editor: "+data["table"]);
			$("#newrow").button();
		},
		"json"
	);
}

$(document).ready(
	function(){
		$("#sqlinputbutton").button();

		$("#sqlinputbutton").click(
			function(){
				$.post(
					"/customsql",
					$("#sqlinputform").serialize(),
					function(data){
						var table = $("#editortable").attr("targettable");
						alert("Request Status:\n"+data["status"]+"\n\n"+data["response"]);
						load_table(table);
					},
					"json"
				);
			}
		);


		$("#logoutbutton").button();

		$("#logoutbutton").click(
			function(){
				$.post(
					"/customsql",
					{"sqlinput": "logout"},
					function(data){
						alert("Request Status:\n"+data["status"]+"\n\n"+data["response"]);
						window.location="/login";
					},
					"json"
				);
			}
		);




		$(".modifylink").click(
			function(){
				$.post(
					"/backend",
					{"table": $(this).attr("target")},
					function(data){
						$("#editor").html(data["editortemplate"]);
						$("#editortitle").html("Editor: "+data["table"]);
						$("#newrow").button();
					},
					"json"
				);

				$(".deletelink").die('click');
				$(".deletelink").live('click',
					function(){
						var table = $("#editortable").attr("targettable");
						var row = $(this).parent().attr("targetrow");
						$("#inputarea").val("DELETE FROM "+table+" WHERE rowid="+row+";");
					}
				);
				$(".editorcell").die('click');
				$(".editorcell").live('click',
					function(){
						var table = $("#editortable").attr("targettable");
						var row = $(this).parent().attr("targetrow");
						var column = $(this).attr("column");
						$("#inputarea").val("UPDATE "+table+" SET "+column+"=??? \nWHERE rowid="+row+";");
					}
				);

				$(".editorrow").die('mouseover');
				$(".editorrow").live('mouseover',
					function(){
						$(this).css("background", "yellow");
					}
				);
				$(".editorrow").die('mouseout');
				$(".editorrow").live('mouseout',
					function(){
						$(this).css("background", "white");
					}
				);


				$("#newrow").die("click");
				$("#newrow").live("click",
					function(){
						var table = $("#editortable").attr("targettable");
						var sql = "insert into "+table+" (rowid) values(NULL);"

						$.post(
							"/customsql",
							{"sqlinput": sql},
							function(data){
								alert("Request Status:\n"+data["status"]+"\n\n"+data["response"]);
								var table = $("#editortable").attr("targettable");
								load_table(table);
							},
							"json"
						);
					}
				);
			}
		);





	}
)
