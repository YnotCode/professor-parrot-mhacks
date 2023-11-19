
import { define, html } from 'https://esm.sh/hybrids@^8';

function logout(){
    Cookies.set("logged-in", "false")
    Cookies.set("session-key", "asklnjfjndsfk")
    window.location.reload()
}

function togglePopup(){
    var popup = document.getElementById("popupWindow");
    if(popup.classList.contains("hidden")){
        popup.classList.remove("hidden");
    }else{
        popup.classList.add("hidden");
    }
}
document.addEventListener('click', function(event) {
    var popup = document.getElementById('popupWindow');
    var button = document.getElementById('toggleButton');

    if (!popup.contains(event.target) && !button.contains(event.target)) {
        popup.classList.add('hidden');
    }
});

define({
    tag: "nav-bar",
    name: '',
    image: '',
    content: (host) => {return html`
    <div class="text-black p-2 border-b-2">
        <div class="flex items-center">
            <a href="/" class="flex items-center">
                <img src="/static/parrot.png" class="w-10 h-10">
                <div class="align-left">
                    <h1 class="text-md font-medium ml-2">Professor Parrot</h1>
                </div>
            </a>
            <div class="flex flex-grow"></div>

            <div class ="relative flex justify-end w-1/5">
                <div id="loginBtn">
                    <a href="/login" class="text-md font-medium ml-2 no-underline hover:underline mr-4">
                        <sl-button variant="primary">Login</sl-button>
                    </a>
                </div>
                <a id="toggleButton" onclick="${togglePopup}" class="flex items-center hover: cursor-pointer">
                    <p id="userName" class="font-medium mr-4"></p>
                    <div class= " hidden mr-4" id="userProfile">
                        <sl-avatar id="userAvatar"></sl-avatar>
                    </div>  
                </a> 
                <div id="popupWindow" class="hidden absolute bg-white rounded-lg border-gray-300 border p-4 shadow-lg w-full top-[50px] z-50">
                    <div class="flex flex-col  items-left gap-6">
                        <a href="/settings" class= "no-underline hover:underline hover:text-teal-800"> Settings </a>
                        <a href="" class= "no-underline hover:underline hover:text-teal-800"> Learning Profile </a>
                        <sl-button variant="default" onclick="${logout}">Logout</sl-button>
                    </div>
                </div>  
            </div>
            <div hidden id="logoutBtn">
                <sl-button onclick="${logout}" variant="primary">Logout</sl-button>
            </div>
        </div>
    </div>
    `}
});