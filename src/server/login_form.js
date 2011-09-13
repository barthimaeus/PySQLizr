$(function() {
		$("#draggable").draggable();
        $("#login").button();
        $("#login").click(
            function(){
                $.post(
                    "/login",
                    $("#form").serialize(),
                    function(data){
                        alert(data["message"]);
                        window.location.replace("/backend");
                    },
                    "json"
                );
            }
        );
});