Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Discussion View: Create Discussion', () => {

    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.wait(500);
    });

    it('Instructor Creates Discussion', () => {
        cy.request({
            method: 'POST',
            url: '/discussion/create/',
            form: true,
            body: {
                comment_html: 'Discussion Title',
                app_label: 'courseaffils',
                model: 'course',
                obj_pk: '1'
            }
        }).then((resp) => {
            cy.visit(resp.redirects[0].substring(5));
        });

        cy.log('create assignment');
        cy.get('#cu-privacy-notice-icon').click();
        //TODO: test discussion creation from homepage
        cy.title().should('contain', 'Discussion');
        cy.get('#comment-form-submit').click();
        cy.contains('Respond').should('exist');
        cy.contains('Edit').should('exist');
        cy.visit('/course/1/oldhome/');
        cy.get('#loaded').should('exist');
        cy.contains('Discussion Title').should('have.attr', 'href');
        cy.contains('Discussion Title').click();
        cy.title().should('contain', 'Discussion');
    });
});
