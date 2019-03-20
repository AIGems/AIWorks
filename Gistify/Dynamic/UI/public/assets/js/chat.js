$( document ).ready(function() {
    $(".container-chat-borderStyle").scrollTop($(".container-chat-borderStyle")[0].scrollHeight);
});

var data={'session_id':'9786597778'}
var wholechat;
var dict = { 'Change Plan': '<i class="em em-angry"></i>&nbsp;&nbsp;&nbsp;&nbsp;<img class="em" src="assets/img/smileys/repeat.svg"></img>', 'Handoff To Agent': '<i class="em em-runner" style="transform: scaleX(-1);"></i>'};
var dyn_dict = []

var url='http://127.0.0.1:4000/retrieve_session';
fetch(url).then(function(response) {
  return response.json();
}).then(function(data) {
  chat_widget(data['session_id']);
  get_signals(data['session_id']);
  get_gistify(data['session_id']);
}).catch(function() {
  console.log("Booo");
});

function chat_widget(session_id){
var data={'session_id':session_id}	
$.post('http://127.0.0.1:4000/get_conversation',data,function(response){

    var chat_for_notes=response['conversation'];
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
	//notes_summary(chat_for_notes);
	//keyextract()

},'json');
}

function isEmpty(obj) {
  return Object.keys(obj).length === 0;
}

function notes_summary(chat_notes){
	console.log("Chat_Notes")
	console.log(chat_notes)
	var data={'query':chat_notes,'length':3}
$.post('http://127.0.0.1:4000/summarize_notes',data,function(response){
	console.log("Notes Summary")
	console.log(response)
},'json');
}


function get_gistify(session_id){
	
	var data={'session_id':session_id}
	
$.post('http://127.0.0.1:4000/get_gistify',data,function(response){
	console.log(response);
	console.log(response['intents']);
	str='<table width="90%"><tr><th width="45%">Bot Action</th><th width="45%">Customer Intent</th></tr></table><ul class="timeline">'

	for(i=0;i<=response['intents'].length-1;i++){
		var intent=response['intents'][i][0]['intent'];
		var action=response['intents'][i][0]['action'];
		var outtext=response['intents'][i][0]['text'][0];
		var time=response['intents'][i][0]['time'];
		var parameters=response['intents'][i][0]['parameters'];
		var parameter_str;

		var absence_flag=isEmpty(parameters)
		console.log(intent);
		console.log(action);
		console.log(outtext);
		console.log(parameters);
		console.log(absence_flag);
		console.log(dict[intent]);
		
		if(action=="input.unknown")
		{
			action="Unrecognized Utterance";
			intent="Handoff To Agent";
			document.getElementById("handoff").innerHTML="<i>"+outtext+"</i>";
			summary_notes="Customer intent was "+response['intents'][i-1][0]['intent']+".Bot takes "+response['intents'][i-1][0]['action']+" action and showed '"+response['intents'][i-1][0]['text'][0]+"'.Bot handoff due to unrecognized utterance ('"+outtext+"')."
			document.getElementById("acw").innerHTML=summary_notes;
		}

		if(i==(response['intents'].length-1)){
			intent_icon='<div class="timeline-badge danger"></i></div>';
		}
		else{
			intent_icon='<div class="timeline-badge warning"></i></div>';
		}

		var expandable_id="timeline_expandale_id_"+i;
		var overlay_id="timeline_overlay_cont_id_"+i;
		var timeline_intent_id="timeline_intent_id_"+i;


		str+='<li class="timeline-inverted">'+intent_icon+'<div class="timeline-panel"><div class="timeline-heading">';
		if(absence_flag===false){
			console.log("inside parameters")
			console.log("Intent is")
			console.log(intent)
			console.log("dict of intent is")
			console.log(dict[intent])
			console.log(dyn_dict[intent])
			if(dict.hasOwnProperty(intent)){
				str+='<table><tr><td><label onclick="toggleConv(\'src\',\''+timeline_intent_id+'\');"><h4 class="timeline-title">'+intent+'&nbsp;&nbsp;&nbsp;&nbsp;'+dict[intent]+'</h4></label></td></tr></table><p><small class="text-muted"><i class="glyphicon glyphicon-time"></i>'+time+' (HH:MM:SS)</small></p>';
			}
			else{
			str+='<table><tr><td><label onclick="toggleConv(\'src\',\''+timeline_intent_id+'\');"><h4 class="timeline-title">'+intent+'</h4></label></td></tr></table><p><small class="text-muted"><i class="glyphicon glyphicon-time"></i>'+time+' (HH:MM:SS)</small></p>';
			}
			
			parameter_str='<div id="'+timeline_intent_id+'" class="timeline-body" style="display:none">';
			
			for (var key in parameters) {
				if (parameters.hasOwnProperty(key)) {           
					console.log(key, parameters[key]);
					if(parameters[key] !== null && parameters[key] !== ''){
					parameter_str+='<p><b>'+key+': </b>'+parameters[key]+'</p>';
					}
				}
			}
			
			parameter_str+='</div>';
			console.log("parameter_str");
			console.log(parameter_str);
			str+=parameter_str;
		}
		else{
			if(dict.hasOwnProperty(intent)){
				str+='<h4 class="timeline-title">'+intent+'&nbsp;&nbsp;&nbsp;&nbsp;'+dict[intent]+'</h4><p><small class="text-muted"><i class="glyphicon glyphicon-time"></i>'+time+' (HH:MM:SS)</small></p>';
			}
			else{
				str+='<h4 class="timeline-title">'+intent+'</h4><p><small class="text-muted"><i class="glyphicon glyphicon-time"></i>'+time+' (HH:MM:SS)</small></p>';
			}
		}
		str+='</div></div></li><li><div class="timeline-badge"></div><div class="timeline-panel"><div class="timeline-heading"><table><tr><td><label onclick="toggleConv(\'src\',\''+overlay_id+'\');"><h4 class="timeline-title">'+action+'</h4></label></td></tr></table></div><hr><div id="'+overlay_id+'" class="timeline-body" style="display:none"><p>'+outtext+'</p></div></div></li>';

	}
	str+='</ul></div>'
	console.log("Get_Gistify_Output_Str");
	console.log(str);
	document.getElementById("chat_gistify_timeline_view").innerHTML=str;

	var handoff_intent=response['intents'][response['intents'].length-2][0]['intent'];
	var handoff_action=response['intents'][response['intents'].length-2][0]['action'];
	document.getElementById("handoff_intent").innerHTML=handoff_intent;
	document.getElementById("handoff_action").innerHTML=handoff_action;

	//document.getElementById("text-area").value=response['conversation']

	//addElementsToTable(response['intents'])
},'json');

}


function get_competitor(session_id, callback){
var data={'session_id':session_id}
var str;
$.post('http://127.0.0.1:4000/competitor',data,function(response){
	console.log(response)
	console.log(response['competitors'])
	if(response['competitors'].length !== 0){
	var competitor_line=response['competitors'][0]['competitor']['index']
	competitor_str='<button id="competitor" class="actionable_signals" onclick="clickAnyWhere(\'chat_conversations_'+competitor_line+'_conversation\')">Competitor Mention</button>'
	callback(competitor_str);
	}
	else{
		console.log("no competitor mentioned")
		return null
	}
},'json');
}


function get_negative_indicator(session_id, callback){
var data={'session_id':session_id}
var max_negative=0
var max_negative_line=0
var max_negative_str;

$.post('http://127.0.0.1:4000/scoresentiment',data,function(response){
	console.log(response)
	for (var key in response) {
		if (response.hasOwnProperty(key)) {           
			if(response[key].length !== 0){
				if(response[key][0][2]>max_negative){
				max_negative=response[key][0][2]
				max_negative_line=response[key][0][3]
				max_negative_intent=key
				}
			}
		}
	}
	if(max_negative !== 0){
	dyn_dict.push({
    key:   max_negative_intent,
    value: "<i class=\"em em-angry\"></i>"
   });
   console.log("dyn_dict")
   console.log(dyn_dict)
	max_negative_str='<button id="sentiment" class="actionable_signals" onclick="clickAnyWhere(\'chat_conversations_'+max_negative_line+'_conversation\')">Negative Sentiment</button>'
	callback(max_negative_str);
	}
	else{
		console.log("no negative sentiment")
		return null
	}
},'json');
}


function get_signals(session_id){
var data={'session_id':session_id}

	get_competitor(session_id,function(competitor_str){
	console.log("competitor api invoked")
	console.log(competitor_str)
	
	get_negative_indicator(session_id,function(max_negative_str){
	console.log("max_negative api invoked")
	console.log(max_negative_str)
	
	$.post('http://127.0.0.1:4000/get_signals',data,function(response){
		console.log(response)
		console.log(response['actions'])
		var competitior_line=response['actions'][0]['competitor']['index']
		var previous_interaction_line=response['actions'][0]['previous_interaction']['index']
		var sentiment=response['actions'][0]['sentiment']['index']

		str=competitor_str+'<button id="previous" class="actionable_signals" onclick="clickAnyWhere(\'chat_conversations_'+previous_interaction_line+'_conversation\')">Previous Interaction Referred</button>'+max_negative_str;
		document.getElementById("actionable_signals").innerHTML = str;
	},'json');
		});
	});
}


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
	var cell_id="chat_conversations_"+i+"_conversation";
	cell1.className = "conversation_cont_right";
	cell1.id=cell_id;
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
	var cell_id="chat_conversations_"+i+"_conversation";
	cell3.id=cell_id;
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
