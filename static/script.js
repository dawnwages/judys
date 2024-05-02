icon = document.getElementById("mobile-menu-button");
menu = document.getElementById("mobile-menu-2");

function checker(){
	if(menu.classList.contains('hidden') == true){
  	    menu.classList.remove('hidden');
    }else{
  	    menu.classList.add('hidden');
    }
}

icon.onclick = function(){
	checker();
}