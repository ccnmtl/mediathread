describe('Student creates annotation', () => {
    before(() => {
        cy.login('student_one', 'test');
        cy.visit('/course/1/react/asset/1/');
    });

    it('should allow a student to create annotation', () => {
        cy.log('should load the asset');
        cy.get('#cu-privacy-notice-button').click();
        cy.get('.asset-detail-title').contains('MAAP Award Reception');
        cy.get('.nav-link').contains('View Selection')
            .should('have.class', 'active').and('not.be.disabled');

        cy.log('should enter Ready state');
        cy.get('.nav-link').contains('Create Selection').click();
        cy.get('.polygon-button').should('be.visible');
        cy.get('.polygon-button').should('not.have.class', 'bg-warning');
        cy.get('.freeformShape-button').should('be.visible');
        cy.get('.freeformShape-button').should('not.have.class', 'bg-warning');
        cy.get('.drawline-button').should('be.visible');
        cy.get('.drawline-button').should('not.have.class', 'bg-warning');
        cy.get('.ol-zoom-in').should('exist');
        cy.get('.ol-zoom-out').should('exist');
        cy.get('.center-btn').should('exist');

        cy.log('should enter ready to draw state');
        cy.get('.polygon-button').click();
        cy.get('.polygon-button').should('have.class', 'bg-warning');
        cy.get('.freeformShape-button').should('not.have.class', 'bg-warning');
        cy.get('.drawline-button').should('not.have.class', 'bg-warning');
        cy.get('.ol-zoom-in').should('not.exist');
        cy.get('.ol-zoom-out').should('not.exist');
        cy.get('.center-btn').should('not.exist');
        cy.get('#cancel-btn').should('be.visible');
        cy.get('#clear-btn').should('not.exist');

        cy.log('should enter draw state');
        cy.get('canvas').click({force: true});
        cy.get('.ol-zoom-in').should('not.exist');
        cy.get('.ol-zoom-out').should('not.exist');
        cy.get('.center-btn').should('not.exist');
        cy.get('.polygon-button').should('have.class', 'bg-warning');
        cy.get('.freeformShape-button').should('not.have.class', 'bg-warning');
        cy.get('.drawline-button').should('not.have.class', 'bg-warning');
        cy.get('#clear-btn').scrollIntoView().should('be.visible');
        cy.get('#cancel-btn').should('not.exist');

        cy.log('should enter view state after release');
        cy.get('canvas').dblclick({force: true});
        cy.get('canvas').dblclick('bottom');
        cy.get('.ol-zoom-in').should('exist');
        cy.get('.ol-zoom-out').should('exist');
        cy.get('.center-btn').should('exist');
        cy.get('.polygon-button').should('not.have.class', 'bg-warning');
        cy.get('.freeformShape-button').should('not.have.class', 'bg-warning');
        cy.get('.drawline-button').should('not.have.class', 'bg-warning');
        cy.get('#clear-btn').scrollIntoView().should('be.visible');
        cy.get('#cancel-btn').should('not.exist');

        cy.log('clear button Functionality');
        cy.get('#clear-btn').click();
        cy.get('.ol-zoom-in').should('exist');
        cy.get('.ol-zoom-out').should('exist');
        cy.get('.center-btn').should('exist');
        cy.get('.polygon-button').should('not.have.class', 'bg-warning');
        cy.get('.freeformShape-button').should('not.have.class', 'bg-warning');
        cy.get('.drawline-button').should('not.have.class', 'bg-warning');
        cy.get('#clear-btn').should('not.exist');
        cy.get('#cancel-btn').should('not.exist');
    });
});
