// JavaScript Document



var home_page_price = 0;
var sub_page_price = 0;





var link_price = 0;

if(location.pathname == '/'){
	link_price = home_page_price;
}

if(location.pathname != '/'){
	link_price = sub_page_price;
}


var promoted_url_at = window.location.href;
promoted_url_at = promoted_url_at.split("?")[0];


const link_form_element = document.createElement('div');
	
link_form_element.setAttribute("id", "link_form_div");





link_form_html_code = ``;

link_form_html_code += `<form id="link_form" class="link_form" action="https://www.paypal.com/cgi-bin/webscr" method="post" enctype="multipart/form-data" target="_top">
<input type="hidden" name="cmd" value="_xclick-subscriptions">
<input type="hidden" name="business" value="KELDMGG5QUQKC">
<input type="hidden" name="lc" value="GB">
<input type="hidden" name="item_name" value="link at ">
<input type="hidden" name="no_note" value="1">
<input type="hidden" name="no_shipping" value="1">
<input type="hidden" name="rm" value="2">
<input type="hidden" name="return" value="https://www./ads/thanks">
<input type="hidden" name="cancel_return" value="https://www./ads">
<input type="hidden" name="src" value="1"> <input type="hidden" name="sra" value="1">  
<input type="hidden" name="a3" value="`+link_price+`">
<input type="hidden" name="p3" value="1">
<input type="hidden" name="t3" value="M">
<input type="hidden" name="currency_code" value="USD">
<input type="hidden" name="bn" value="PP-SubscriptionsBF:btn_buynowCC_LG.gif:NonHosted">
<input type="hidden" name="on0" value="promoted_url">
<input name="os0" type="url" placeholder="enter your URL (https://)" required value="">

<br>
<input type="hidden" name="on1" value="promoted_url_title">
<input name="os1" type="text" style="margin-top:1em;" placeholder="url text/title" required value="">

<input type="hidden" name="on2" value="promoted_url_at">
<input type="hidden" name="os2" value="`+promoted_url_at+`">`;


if(location.pathname == '/'){
    link_form_html_code += `<br>
    <img src="/images/home-page-note.png?3" width="343" height="13" alt="" style="display:inline-block; margin-top:1em;"/>`;
}

link_form_html_code += `<br>
<input type="submit" class="liquid_button" style="margin-top:1em; cursor:pointer;" value="add your link here ($`+link_price+`)">

</form>`;



// html cod eneeds to be set by element, not by ID, by ID is only available after element is written in document
link_form_element.innerHTML = link_form_html_code;

// document.body.insertAdjacentElement('beforeend', link_form_element);



// get the currently running .js script element
current_script = document.currentScript;

// Add the newly-created div to the page
current_script.parentElement.insertBefore(link_form_element, current_script); 









if(typeof document.referrer !== 'undefined' && document.referrer !== null && document.referrer != ''){
	var referrer_is_valid = true;
}

if(referrer_is_valid){
	
	
	if(document.referrer.startsWith(window.location.host)){
		referrer_is_valid = false;
	}
    if(document.referrer.startsWith('http://'+window.location.host)){
		referrer_is_valid = false;
	} 
	if(document.referrer.startsWith('https://'+window.location.host)){
		referrer_is_valid = false;
	} 

}

if(referrer_is_valid){

    const url = 'https://www.tntcode.com/ads/user_source_save.php?referrer='+document.referrer+'&landing_url='+document.URL+'&using_beacon'+Math.random();
	navigator.sendBeacon(url);
    
}


