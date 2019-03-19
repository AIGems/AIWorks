var animation_speed_chat_toggle = 1000;

function readChat(){

	var destObj = $("#chat_gistify_timeline_view");
	if (destObj.is(':visible')){
		destObj.hide();
		$("#gistify_read_more_label_id").html("Show Timeline >>");
	} else{
		destObj.show();
		$("#gistify_read_more_label_id").html("Hide Timeline");
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
