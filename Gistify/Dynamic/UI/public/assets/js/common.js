var animation_speed_chat_toggle = 1000;

function readChat(){

	var destObj = $("#chat_gistify_timeline_view");
	if (destObj.is(':visible')){
		destObj.hide();
		$("#gistify_read_more_label_id").html("<h3>Show Timeline >></h3>");
	} else{
		destObj.show();
		$("#gistify_read_more_label_id").html("<h3>Hide Timeline</h3>");
	}
}

function toggleConv(src, dest){
	var destObj = $("#"+dest);
	if (destObj.is(':visible')){
		destObj.hide(animation_speed_chat_toggle);
	} else{
		destObj.show(animation_speed_chat_toggle);
	}
}


function ajaxPop()
{
    $(this).speedoPopup(
    {
        width:550,
        height:265,
        useFrame: TRUE,
        href: '#chat_gistify_timeline_view'
    });
}

function myfunction() {
	window.open(
		'http://localhost:8081/gistify.html','popUpWindow','height=300,width=400,left=10,top=10,resizable=yes,scrollbars=yes,toolbar=yes,menubar=no,location=no,directories=no,status=yes')
}