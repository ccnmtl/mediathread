Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false;
});

describe('Log In Feature: Test Instructor Login', () => {
    it('Logs in as instructor_one', () => {
        cy.visit('/accounts/login/');
        cy.title().should('contain', 'Login');
        cy.get('#cu-privacy-notice-button').click();
        cy.get('#guest-login').click();
        cy.get('#login-local>div.login-local-form').should('be.visible');
        cy.login('instructor_one', 'test');
        cy.visit('/');
        cy.get('#course-title').contains('My Courses');
        cy.get('#sandboxes_link').click();
        cy.get('.choose-course').should('contain', 'Sample Course');
        cy.get('.choose-course').click();
        cy.title().should('contain', 'Sample Course');
        cy.get('.sign-out').click();
        cy.title().should('contain', 'Splash');
    });
});

describe('Log In Feature: Test Invalid login', () => {
    it('should not log in with invalid credentials', () => {
        cy.visit('/accounts/login/');
        cy.title().should('contain', 'Login');
        cy.get('#cu-privacy-notice-button').click();
        cy.get('#guest-login').click();
        cy.get('#login-local>div.login-local-form').should('be.visible');
        cy.login('foo', 'foo');
        cy.title().should('contain', 'Login');
    });
});

describe('Log In Feature: Test Student Login', () => {
    it('should log in as student_one', () => {
        cy.visit('/accounts/login/');
        cy.title().should('contain', 'Login');
        cy.get('#cu-privacy-notice-button').click();
        cy.get('#guest-login').click();
        cy.get('#login-local>div.login-local-form').should('be.visible');
        cy.login('student_one', 'test');
        cy.visit('/');
        cy.title().should('contain', 'Sample Course');
        cy.get('.sign-out').click();
        cy.title().should('contain', 'Splash');
    });
});

describe('Log In Feature: Test Switch Course feature', () => {
    it('should log in as student_one and see courses', () => {
        cy.visit('/accounts/login/');
        cy.title().should('contain', 'Login');
        cy.get('#cu-privacy-notice-button').click();
        cy.get('#guest-login').click();
        cy.get('#login-local>div.login-local-form').should('be.visible');
        cy.login('student_three', 'test');
        cy.visit('/');

        cy.title().should('contain', 'My Courses');
        cy.get('#sandboxes_link').click();
        cy.contains('Alternate Course').should('exist')
            .and('have.attr', 'href');
        cy.contains('Sample Course').should('exist')
            .and('have.attr', 'href');
        cy.contains('Alternate Course').click();
        cy.get('#course-title').should('contain', 'Alternate Course');

        cy.get('#userMenu').click({force: true});
        cy.get('a[href="/course/list/"]').should('exist');
        cy.get('a[href="/course/list/"]').click();
        cy.title().should('contain', 'My Courses');

        cy.get('#sandboxes_link').click();
        cy.contains('Sample Course').click();
        cy.get('#course-title').should('contain', 'Sample Course');
    });
});
