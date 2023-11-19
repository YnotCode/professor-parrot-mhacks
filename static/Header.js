import { define, html } from 'https://esm.sh/hybrids@^8';

define({
    tag: "header-1",
    name: '',
    content: (host) => { return html`<h1> Welcome, ${host.name}</h1>`},
});