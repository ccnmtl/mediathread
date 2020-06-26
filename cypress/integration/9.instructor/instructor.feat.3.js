Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Instructor Feat: Test Create Composition', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.wait(500);
    });

    it('should create a composition as an Instructor', () => {
        cy.log('should check composition panel features');

        //TODO: Test create composition from homepage
        cy.visit('/course/1/project/create/', {
            method: 'POST',
            body: {
                project_type: 'composition'
            }
        });

        cy.wait(500);
        cy.get('#loaded').should('exist');
        cy.get('.panhandle-stripe.composition').should('exist');
        cy.get('.panel-subcontainer-title').contains('Untitled')
            .should('exist');
        cy.get('td.panel-container.open.composition').should('exist');
        cy.get('.panel-subcontainer-title > .form-control').clear()
            .type('Instructor Feature 4');
        cy.get('.project-savebutton').click();
        cy.get('.btn-save-project').click();
        cy.title().should('contain', 'Instructor Feature 4');
        cy.get('#course_title_link').click({force: true});
        cy.contains('Instructor Feature 4').should('exist');
    });
});
