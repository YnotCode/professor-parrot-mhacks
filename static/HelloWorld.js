import { define, html } from 'https://esm.sh/hybrids@^8';
   
function changeIt(host){
    console.log(host.name);
    var val = host.name;
    host.name = (val == "Joe") ? "World" : "Joe";
}

define({
    tag: "hello-world",
    name: '',
    content: (host) => { return html`<sl-button class="bg-blue-100 p-5 rounded-sm" onclick="${()=>changeIt(host)}">Hello ${host.name}!</sl-button>`},
});