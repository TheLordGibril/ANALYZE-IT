// ***********************************************************
// This example support/e2e.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'
import '@cypress/code-coverage/support'

// Configuration globale
Cypress.on('window:before:load', (win) => {

    if (win.__coverage__) {
        console.log('Coverage object found!');
    } else {
        console.log('No coverage object found');
    }
});

afterEach(() => {
    cy.window().then((win) => {
        if (win.__coverage__) {
            console.log('Collecting coverage data...');
        }
    });
});

Cypress.on('uncaught:exception', (err, runnable) => {
    // returning false here prevents Cypress from
    // failing the test
    return false
})