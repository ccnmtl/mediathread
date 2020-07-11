// TODO: why are we getting an error for `the_records`
// here in the course settings page?
Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Student Project Visibility', () => {
    beforeEach(() => {
        cy.login('student_one', 'test');
        cy.wait(500);
    });

    it('creates a project as an Instructor', () => {
        cy.visit('/course/1/');
        cy.wait(500);
        cy.visit('/course/1/project/create/', {
            method: 'POST',
            body: {
                project_type: 'composition'
            }
        });

        cy.wait(500);

        cy.get('#loaded').should('exist');
        cy.get('.page-title-form input').clear()
            .type('Composition Public: Scenario 3');
        cy.get('.project-savebutton').click();
        cy.contains('Whole Class - all class members can view').click();
        cy.get('.btn-save-project').contains('Save').click();
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.get('.project-visibility-description')
            .should('contain', 'Shared with Class');
    });

    // it('views composition as a Student', () => {
    //     cy.login('student_one', 'test');

    //     cy.visit('/course/1/');
    //     // cy.get('.instructor-list')
    //     //     .should('have.length', 1)
    //     //     .and('contain', 'Composition Public: Scenario 3');
    //     // cy.get('.switcher-top').click();
    //     // cy.get('#choice_all_items > .switcher-choice').click();
    //     // cy.get('.projectlist').should('exist')
    //     //     .and('contain', 'Composition Public: Scenario 3');
    // });

    it('creates a project as Student one', () => {
        cy.visit('/course/1/project/create/', {
            method: 'POST',
            body: {
                project_type: 'composition'
            }
        });

        cy.get('#loaded').should('exist');
        cy.get('.page-title-form input').clear()
            .type('Public');
        cy.get('.project-savebutton').click();
        cy.contains('Whole Class - all class members can view').click();
        cy.get('.btn-save-project').contains('Save').click();
        cy.get('.project-savebutton').should('contain', 'Saved');
        cy.get('.project-visibility-description')
            .should('contain', 'Shared with Class');
    });

    // it('views Student One composition as Student Two', () => {
        // cy.login('student_two', 'test');
        // cy.visit('/course/1/');
        // cy.get('.switcher-top').click();
        // cy.get('.switcher-choice.owner').contains('One, Student').click();
        // cy.get('.metadata-value-author').contains('Student One');
        // cy.get('.projectlist').should('exist')
        //     .and('contain', 'Public');
    // })
});
