$( document ).ready(function() {
    $(".container-chat-borderStyle").scrollTop($(".container-chat-borderStyle")[0].scrollHeight);
});

var data={'session_id':'9786597778'}
var wholechat;

$.post('http://127.0.0.1:4000/get_conversation',data,function(response){
	console.log(response)
	console.log(response['conversation'])
	wholechat=response['conversation'];
	wholechat=wholechat.toString();
	console.log("Wholechat");
	console.log(wholechat);
	var chats=response['conversation'].split("\n");
	console.log(chats)

	for(i=0;i<chats.length-1;i++){
		if(i%2==0){
			customerChat(chats[i]);
		}
		else{
			botChat(chats[i]);
		}
	}
	keyextract()

},'json');


$.post('http://127.0.0.1:4000/get_gistify',data,function(response){
	console.log(response);
	console.log(response['intents']);
	str='<table width="70%"><tr><th width="35%">Bot Action</th><th width="35%">Customer Intent</th></tr></table><ul class="timeline">'
	var dict = { "Bill Details" : "white.jpg","Change Plan": "angry.png", "Bill Payment No": "white.jpg","Bill Payment Yes": "white.jpg", "Bill Payment": "white.jpg", "Default Fallback Intent"  : "white.jpg"};
	var churn_dict = { "Bill Details" : "white.jpg","Change Plan": "white.jpg", "Bill Payment No": "white.jpg","Bill Payment Yes": "white.jpg", "Bill Payment": "white.jpg", "Default Fallback Intent"  : "white.jpg" };

	for(i=0;i<=response['intents'].length-1;i++){
		//console.log(response['intents'][i][0]);
		var intent=response['intents'][i][0]['intent'];
		var action=response['intents'][i][0]['action'];
		var outtext=response['intents'][i][0]['text'][0];
		var time=response['intents'][i][0]['time'];

		console.log(intent);
		console.log(action);
		console.log(outtext);
		console.log(dict[intent]);

		if(action=="input.unknown")
		{
			action="Unrecognized Utterance";
			document.getElementById("handoff").innerHTML="<i>"+outtext+"</i>";
		}

		if(i==(response['intents'].length-1)){
			intent_icon='<div class="timeline-badge danger"><i class="glyphicon glyphicon-thumbs-down"></i></div>';
		}
		else{
			intent_icon='<div class="timeline-badge warning"><i class="glyphicon glyphicon-credit-card"></i></div>';
		}

		var expandable_id="timeline_expandale_id_"+i;
		var overlay_id="timeline_overlay_cont_id_"+i;


		str+='<li class="timeline-inverted">'+intent_icon+'<div class="timeline-panel"><div class="timeline-heading"><h4 class="timeline-title">'+intent+'</h4><p><small class="text-muted"><i class="glyphicon glyphicon-time"></i>'+time+' (HH:MM:SS)</small></p></div></div></li><li><div class="timeline-badge"><i class="glyphicon glyphicon-check"></i></div><div class="timeline-panel"><div class="timeline-heading"><table><tr><td><label onclick="toggleConv(\'src\',\''+overlay_id+'\');"><h4 class="timeline-title">'+action+'</h4></label></td></tr></table></div><hr><div id="'+overlay_id+'" class="timeline-body" style="display:none"><p>'+outtext+'</p></div></div></li>';

	}
	str+='</ul></div>'
	document.getElementById("chat_gistify_timeline_view").innerHTML=str;

	var handoff_intent=response['intents'][response['intents'].length-2][0]['intent'];
	var handoff_action=response['intents'][response['intents'].length-2][0]['action'];
	document.getElementById("handoff_intent").innerHTML=handoff_intent;
	document.getElementById("handoff_action").innerHTML=handoff_action;

	//document.getElementById("text-area").value=response['conversation']

	//addElementsToTable(response['intents'])
},'json');


function keyextract(){

    console.log(wholechat)
	data={'query':wholechat,'length':'4'}
	console.log(data)
	$.post('http://127.0.0.1:4000/keywords_extract',data,function(response){
		console.log(response)
	},'json');

}

//keyextract()

function customerChat(chat){
	var div_id="chat_conversations_"+i;
	var div = document.createElement("div");
	div.className="chat_conversation_right";
	div.id=div_id;

	var table=document.createElement("table");
	table.className="conversation_table r_float";
	var row = table.insertRow(0);
	var cell1 = row.insertCell(0);
	cell1.className = "conversation_cont_right";
	cell1.innerHTML = chat;

	var cell2 = row.insertCell(1);
	cell2.className = "conv_indicator_cont_right l_float";
	cell2.innerHTML = '<img src="assets/img/triangle.png" alt="" class="conv_indicator_right">';

    var cell3 = row.insertCell(2);
	cell3.className = "chat_img_cont";
	cell3.innerHTML = '<img src="assets/img/wwe-customer-icon.png" alt="bot" class="img_round_64">';

	div.appendChild(table);
    document.getElementById("chat_widget_container_id").appendChild(div);
}


function botChat(chat){
	var div_id="chat_conversations_"+i;
	var div = document.createElement("div");
	div.className="chat_conversation_left";
	div.id=div_id;

	var table=document.createElement("table");
	table.className="conversation_table l_float";
	var row = table.insertRow(0);
    var cell1 = row.insertCell(0);
	cell1.className = "chat_img_cont";
	cell1.innerHTML = '<img src="assets/img/chatbot.png" alt="bot" class="img_round_64">';

	var cell2 = row.insertCell(1);
	cell2.className = "conv_indicator_cont_left r_float";
	cell2.innerHTML = '<img src="assets/img/triangle.png" alt="" class="conv_indicator_left">';

	var cell3 = row.insertCell(2);
	cell3.className = "conversation_cont_left";
	cell3.innerHTML = chat;

	div.appendChild(table);
    document.getElementById("chat_widget_container_id").appendChild(div);
}

function selectText() {
  const input = document.getElementById('text-area');
  input.focus();
  input.setSelectionRange(21,25);
}

function selectTextareaLine(startLineNum,endLineNum) {
    var tarea=document.getElementById('text-area');
    //startLineNum--; // array starts at 0
	if(startLineNum<0){startLineNum=0;}
	//endLineNum--;
    var lines = tarea.value.split("\n");

    // calculate start/end
    //var startPos = 0, endPos = tarea.value.length;
	var startPos = 0, endPos = 0;
	var startFlag=0, endFlag = 0;
    for(var x = 0; x < lines.length; x++) {
        if(x == startLineNum) {
		    startFlag=1;
            //break;
        }
		if(startFlag!=1){
        startPos += (lines[x].length+1);
		}
		if(startFlag==1 && endFlag!=1){
		endPos += (lines[x].length+1);
		}
		if(x == endLineNum) {
		    endFlag=1;
			endPos += startPos;
			//endPos += lines[endLineNum].length+startPos;
            //break;
        }
    }
	console.log(lines);
	console.log(startPos);
	console.log(lines[endLineNum]);
	console.log(endPos);

    //var endPos = lines[endLineNum].length+startPos;

    // do selection
    // Chrome / Firefox

    if(typeof(tarea.selectionStart) != "undefined") {
        tarea.focus();
        tarea.selectionStart = startPos;
        tarea.selectionEnd = endPos;
        return true;
    }

    // IE
    if (document.selection && document.selection.createRange) {
        tarea.focus();
        tarea.select();
        var range = document.selection.createRange();
        range.collapse(true);
        range.moveEnd("character", endPos);
        range.moveStart("character", startPos);
        range.select();
        return true;
    }

    return false;
}

function addElementsToTable(arrayElements)
{
    var table = document.getElementById("myTable");


	for(i=0;i<=arrayElements.length-1;i++){
	    // Create an empty <tr> element and add it to the 1st position of the table:
		console.log(arrayElements[i])
		var intent=arrayElements[i][0]['intent'];
		var start=arrayElements[i][0]['start'];
		var end=arrayElements[i][0]['end'];
		console.log(intent)
		console.log(start)
		console.log(end)
        var row = table.insertRow(i);

       // Insert new cells (<td> elements) at the 1st and 2nd position of the "new" <tr> element:
        var cell1 = row.insertCell(0);

      // Add some text to the new cells:
      cell1.innerHTML = "<button onclick='selectTextareaLine("+start+","+end+")'>"+intent+"</button>";
  }
}

function addText(id,action) {
    //var targ = event.target || event.srcElement;
    document.getElementById(id).value += action;
}

function copyNotes(id) {
	var notes = document.getElementById('suggested_response_new').innerText;
	console.log(notes);
	document.getElementById(id).value += notes;
}

function copyResponse(id) {
	var notes = document.getElementById('suggested_response_new').innerText;
	console.log(notes);
	document.getElementById(id).value = notes;
}

// function selectConversation(id) {
// 	var customerConversation = document.getElementById(id);
// 	console.log(customerConversation);
// 	customerConversation.className += " selectingConversation";
// }

function changeText(id,txt) {
    //var targ = event.target || event.srcElement;
    document.getElementById(id).innerHTML = txt;
}

function showTableText(id) {
	document.getElementById(id).style.display = "inline-block";
}
function hideTableText(id) {
	document.getElementById(id).style.display = "none";
}

$(function () {
	$('#suggested_action').change(function () {

	})
})

function agentReply(id) {
	var message = document.getElementById(id).value;

	if (message) {
		var originalDiv = document.getElementById("chat_widget_container_id")
		var div = document.createElement("div")
		div.classList.add("chat_conversation_left")
		// create elements <table>
		var tbl = document.createElement("table");
		var tblBody = document.createElement("tbody");
		tbl.classList.add("conversation_table")
		tbl.classList.add("l_float")
		// table row creation
		var row = document.createElement("tr");
		// create element <td> and text node
		//Make text node the contents of <td> element
		// put <td> at end of the table row
		var cell_1 = document.createElement("td");
		cell_1.classList.add("chat_img_cont");
		var img_1 = document.createElement("img");
		img_1.setAttribute("src", "assets/img/wwe-agent-icon.png");
		img_1.setAttribute("alt", "Agent");
		img_1.classList.add("img_round_64");
		cell_1.appendChild(img_1);
		row.appendChild(cell_1);

		var cell_2 = document.createElement("td");
		cell_2.classList.add("conv_indicator_cont_left");
		cell_2.classList.add("r_float");
		var img_2 = document.createElement("img");
		img_2.setAttribute("src", "assets/img/triangle.png");
		img_2.setAttribute("alt", "");
		img_2.classList.add("conv_indicator_left")
		cell_2.appendChild(img_2);
		row.appendChild(cell_1);

		var cell_3 = document.createElement("td");
		cell_3.classList.add("conversation_cont_left")
		var cellText_3 = document.createTextNode(message);
		cell_3.appendChild(cellText_3)
		row.appendChild(cell_3)

		tblBody.appendChild(row);
		tbl.appendChild(tblBody);
		div.appendChild(tbl)
		originalDiv.appendChild(div)
		document.getElementById(id).value=""
	}
}
function addTextAgent(class_name,text) {
	// var hello = "hello"
	// var agentText = document.getElementsByClassName('wwe-message-box');
	// document.getElementsByClassName(class_name).innerHTML=text;
	document.getElementById(class_name).innerHTML=text;
	// console.log(document.getElementsByClassName(class_name).innerHTML);
	console.log(class_name);
	console.log(text);
	// parent.document.querySelector('.wwe-chat-view .wwe-message-box .wwe-textarea').innerText="hi from js";
}
function changeButtonColor(event) {
	var count = 0;
	let parentElement = event.currentTarget.parentElement.children;
	for (var i = 0; i < parentElement.length; i++) {
		parentElement[i].style.color = '#000'; //black
		parentElement[i].style.backgroundColor = '#fff'; //white
		parentElement[i].style.borderColor = '#FF4F1F' //black
	}
	event.currentTarget.style.color = '#fff'; //white
	event.currentTarget.style.backgroundColor = '#FF4F1F'; //black
	event.currentTarget.style.borderColor = '#FF4F1F' //black

}

function scrollDown() {
	$(".container-chat-borderStyle").scrollTop($(".container-chat-borderStyle")[0].scrollHeight);
}


(function(){
	document.getElementById('chat_widget_container_id_1').scrollTop = 9999999;
	alert('hello');
}());


// remove all .active classes when clicked anywhere
// function selectConversation(id) {
// 	var customerConversation = document.getElementById(id);
// 	console.log(customerConversation);
// 	customerConversation.className += " selectingConversation";
// }

function clickAnyWhere(conv_id){
var conversation=document.getElementById(conv_id);
conversation.className += " selectingConversation";
document.getElementById(conv_id).scrollIntoView();

console.log("inside click anywhere")
console.log(conversation)

hide = true;
$('.chat-main-div').on("click", function () {
     if (hide) $('.conversation_cont_right').removeClass('selectingConversation');
     hide = true;
	 });

	 // $('.gistify_conversation_cont').on("click", function () {
 	 //     if (hide) $('.conversation_cont_right').removeClass('selectingConversation');
 	 //     hide = false;
 		//  });

// $('.actionable_signals').on("click", function () {
//  	      if (hide and $('.conversation_cont_right').hasClass('selectingConversation'))
// 				{
// 					$('.conversation_cont_right').removeClass('selectingConversation');
// 					hide=false;
// 				}
// 				// else{
// 				// 	$('.conversation_cont_right').addClass('selectingConversation');
// 				// 	hide=true;
// 				// }
//  	 	 });

// add and remove .active
// $(conv_id).on('click', '.conversation_cont_right', function () {
//
//     var self = $(this);
//
//     if (self.hasClass('selectingConversation')) {
//         $('.conversation_cont_right').removeClass('selectingConversation');
//         return false;
//     }
//
//     $('.conversation_cont_right').removeClass('selectingConversation');
//
//     self.toggleClass('selectingConversation');
//     hide = false;
// });
}
