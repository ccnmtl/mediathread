Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Instructor Feat: Test Create Composition', () => {
    beforeEach(() => {
        cy.login('instructor_one', 'test');
        cy.visit('/course/1/');
        cy.get('.card-group h5 a').contains('MAAP Award Reception');
    });

    it('should create a composition as an Instructor', () => {
        cy.log('creates a project');
        cy.visit('/course/1/projects');
        cy.get('.page-title').contains('Projects');
        cy.get('#cu-privacy-notice-icon').click();
        cy.get('button').contains('Add a project').should('be.visible');
        cy.get('button').contains('Add a project').click()
        cy.get('button#add-composition-button').should('be.visible')
        cy.get('button#add-composition-button').click();

        cy.log('should check composition panel features');
        cy.get('#loaded').should('exist');
        cy.get('.page-title').should('be.visible');
        cy.get('.page-title').contains('Untitled')
        cy.get('.page-title').click().clear()
            .type('Instructor Feature 3');
        cy.get('.project-savebutton').click();
        cy.get('.btn-save-project').click();
        cy.title().should('contain', 'Instructor Feature 3');
        cy.visit('/course/1/projects/');
        cy.contains('Instructor Feature 3').should('exist');
    });
});
