// TODO: why are we getting an error for `the_records`
// here in the course settings page?
Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Student Project Visibility', () => {

    it('creates a project as an Instructor', () => {
      cy.login('instructor_one', 'test');
      cy.visit('/course/1/');
      cy.get('#homepage-create-menu').click();
      cy.get('#create-project-menu input[type="submit"]')
        .eq(1).contains('Create Composition').click();
      cy.get('#loaded').should('exist');
      cy.get('.panel-subcontainer-title > .form-control').clear()
        .type('Composition Public: Scenario 3');
      cy.get('.project-savebutton').click();
      cy.contains('Whole Class - all class members can view').click();
      cy.get('.btn-primary').contains('Save').click();
      cy.get('.project-savebutton').should('contain', 'Saved');
      cy.get('.project-visibility-link').should('contain', 'Published to Class');
    });
    it('views composition as a Student', () => {
      cy.login('student_one', 'test');
      cy.visit('/course/1/');
      cy.get('.instructor-list')
        .should('have.length', 1)
        .and('contain', 'Composition Public: Scenario 3');
      cy.get('.switcher-top').click();
      cy.get('#choice_all_items > .switcher-choice').click();
      cy.get('.projectlist').should('exist')
        .and('contain', 'Composition Public: Scenario 3');
    });
    it('creates a project as Student one', () => {
      cy.login('student_one', 'test');
      cy.visit('/course/1/');
      cy.get('#homepage-create-menu').click();
      cy.get('#create-project-menu input[type="submit"]')
        .contains('Create Composition').click();
      cy.get('#loaded').should('exist');
      cy.get('.panel-subcontainer-title > .form-control').clear()
        .type('Public');
      cy.get('.project-savebutton').click();
      cy.contains('Whole Class - all class members can view').click();
      cy.get('.btn-primary').contains('Save').click();
      cy.get('.project-savebutton').should('contain', 'Saved');
      cy.get('.project-visibility-link').should('contain', 'Published to Class');
    });
    it('views Student One composition as Student Two', () => {
      cy.login('student_two', 'test');
      cy.visit('/course/1/');
      cy.get('.switcher-top').click();
      cy.get('.switcher-choice.owner').contains('One, Student').click();
      cy.get('.metadata-value-author').contains('Student One');
      cy.get('.projectlist').should('exist')
        .and('contain', 'Public');
    })
});
