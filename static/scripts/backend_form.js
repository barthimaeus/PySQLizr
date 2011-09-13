$(document).ready(
	function(){
		$("#sqlinputbutton").button();

		$("#sqlinputbutton").click(
			function(){
				$.post(
					"/customsql",
					$("#sqlinputform").serialize(),
					function(data){
						alert("Request Status:\n"+data["status"]+"\n\n"+data["response"]);
						window.location="/backend";
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
					},
					"json"
				);

				$(".deletelink").live('click',
					function(){
						$("#inputarea").val("DELETE FROM "+$(this).attr("targettable")+" WHERE "+$(this).attr("targetcolumn")+"="+$(this).attr("targetval")+";");
					}
				);
			}
		);





	}
)
