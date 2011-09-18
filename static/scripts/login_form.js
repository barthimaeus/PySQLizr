$(document).ready(
	function(){
		$("#loginform").draggable();
		$("#loginbutton").button();
		$("#loginbutton").click(
			function() {
				$.post(
					"/login",
					$("#form").serialize(),
					function(data){
						if (data["message"] == "correct") {
							window.location="/backend";
						}
						else {
							window.location="/login";
						}
					},
					dataType="json"
				)
			}
		)
	}
)