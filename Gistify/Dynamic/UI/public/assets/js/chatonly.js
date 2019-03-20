$( document ).ready(function() {
    $(".container-chat-borderStyle").scrollTop($(".container-chat-borderStyle")[0].scrollHeight);
});

var data={'session_id':'9786597778'}
var wholechat;

var url='http://127.0.0.1:4000/retrieve_session';
fetch(url).then(function(response) {
  return response.json();
}).then(function(data) {
  console.log(data);
  console.log(data['session_id']);
  chat_widget(data['session_id']);
}).catch(function() {
  console.log("Booo");
});


function chat_widget(session_id){
var data={'session_id':session_id}	
$.post('http://127.0.0.1:4000/get_conversation',data,function(response){
	console.log(response)
	//session_id=get_session();
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

},'json');
}


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
