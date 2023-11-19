import { define, html } from 'https://esm.sh/hybrids@^8';

define({
    tag: "subject-card",
    subject: '',
    completion: '',
    content: (host) => {return html`
        <sl-card 
        class="w-64 bg-white hover:bg-gray-100 transition duration-250 ease-in-out transform hover:-translate-y-1 hover:scale-105 hover:animate-pulse active:bg-gray-200" 
        href="/learn">
            <img
                slot="image"
                src=""
            />
            
            <strong>${host.subject}</strong><br />
            <small class="text-gray-500">${host.completion}% Complete</small><br />   
            <sl-button variant="success" size="small" class="mt-4 w-1/2" outline>
                <sl-icon slot="suffix" name="box-arrow-up-right"></sl-icon>
                Learn
            </sl-button><br />
            <div slot="footer">
                <sl-progress-bar value="${host.completion}"></sl-progress-bar>
            </div>
        </sl-card>
    `}
});