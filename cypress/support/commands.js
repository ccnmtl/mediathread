// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject,
//   options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'},
//   (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

Cypress.Commands.add('login', (username, password) => {
    return cy.request({
        url: '/accounts/login/',
        method: 'GET'
    }).then(() => {
        cy.getCookie('csrftoken').its('value').then((token) => {
            cy.request({
                url: '/accounts/login/',
                method: 'POST',
                form: true,
                followRedirect: true,
                body: {
                    username: username,
                    password: password,
                    csrfmiddlewaretoken: token
                }
            }).then(() => {
                return cy.getCookie('csrftoken').its('value');
            });
        });
    });
});

Cypress.Commands.add('getIframeBody', () => {
    // get the iframe > document > body
    // and retry until the body element is not empty
    return cy
        .get('iframe')
        .its('0.contentDocument.body').should('not.be.empty')
    // wraps "body" DOM element to allow
    // chaining more Cypress commands, like ".find(...)"
    // https://on.cypress.io/wrap
        .then(cy.wrap);
});

// Lifted this pattern from https://github.com/jonoliver/cypress-axe-demo

const severityIndicators = {
    minor: '⚪️',
    moderate: '🟡',
    serious: '🟠',
    critical: '🔴',
};

function callback(violations) {
    violations.forEach(violation => {
        const nodes =
            Cypress.$(violation.nodes.map(node => node.target).join(','));

        Cypress.log({
            name: `${severityIndicators[violation.impact]} A11Y`,
            consoleProps: () => violation,
            $el: nodes,
            message: `[${violation.help}](${violation.helpUrl})`
        });

        violation.nodes.forEach(({ target }) => {
            Cypress.log({
                name: '🔧',
                consoleProps: () => violation,
                $el: Cypress.$(target.join(',')),
                message: target
            });
        });
    });
}

Cypress.Commands.add('checkPageA11y', () => {
    cy.injectAxe();

    const ctx = {runOnly: {type: 'tag', values: ['wcag2a']}};
    cy.checkA11y('html', ctx, callback, true);
});
