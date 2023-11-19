import { define, html } from 'https://esm.sh/hybrids@^8';

define({
    tag: "topic-row",
    topic: '',
    mastery: '',
    content: (host) => {return html`
    <tr class="bg-white w-full min-w-full">
        <td class="border px-4 py-2">${host.topic}</td>
        <td class="border px-4 py-2 justify-items-center">
            Mastery: <sl-rating label="Rating" readonly value="${parseInt(host.mastery)/100*5}"></sl-rating>
        </td>
    </tr>
    `}
});