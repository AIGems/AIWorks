var data={'session_id':'9786597778'}

$.post('http://127.0.0.1:4000/get_gistify',data,function(response){
	console.log(response)
	var txt=response['intents'][response['intents'].length-1][0]['text'][0]
	var action=response['intents'][response['intents'].length-2][0]['action']
	var intent=response['intents'][response['intents'].length-2][0]['intent']
	$(".intentsum").html(intent);
	$(".actionsum").html(action);
	$(".textsum").html(txt);
	var txt_1=response['intents'][response['intents'].length-2][0]['text'][0]
	var action_1=response['intents'][response['intents'].length-2][0]['action']
	var intent_1=response['intents'][response['intents'].length-2][0]['intent']
	$(".textsum_1").html(txt_1);
	$(".intentsum_1").html(intent_1);
	$(".actionsum_1").html(action_1);
	var txt_3=response['intents'][response['intents'].length-4][0]['text'][0]
	var action_3=response['intents'][response['intents'].length-4][0]['action']
	// print action_3
	var intent_3=response['intents'][response['intents'].length-4][0]['intent']
	$(".textsum_3").html(txt_3);
	$(".actionsum_3").html(action_3);
	$(".intentsum_3").html(intent_3);

	// for (var i=2; i<5; i+=2)
	// {
	// 	var txt_arr[i] = response['intents'][response['intents'].length-i][0]['text'][0]
	// 	var action_arr[i]=response['intents'][response['intents'].length-i][0]['action']
	// 	var intent_arr[i]=response['intents'][response['intents'].length-i][0]['intent']
	// 	$(".text_sum[i]").html(txt_arr[i]);
	// 	$(".intent_sum[i]").html(intent_arr[i]);
	// 	$(".action_sum[i]").html(action_arr[i]);
	// }

},'json');
