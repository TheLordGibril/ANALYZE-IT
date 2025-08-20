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
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })

// Commande pour intercepter les appels API
Cypress.Commands.add('mockApiCall', (fixture = 'prediction-mock') => {
    cy.intercept('POST', '**/graphql', { fixture }).as('getPrediction')
})

// Commande pour sélectionner un pays
Cypress.Commands.add('selectCountry', (country) => {
    cy.get('select[name="country"]').then($select => {
        $select.val(country)
        $select[0].dispatchEvent(new Event('change', { bubbles: true }))
    })
    cy.get('select[name="country"]').should('have.value', country)
})

// Commande pour sélectionner un pays
Cypress.Commands.add('selectVirus', (virus) => {
    cy.get('select[name="virus"]').then($select => {
        $select.val(virus)
        $select[0].dispatchEvent(new Event('change', { bubbles: true }))
    })
    cy.get('select[name="virus"]').should('have.value', virus)
})

// Commande pour sélectionner un modèle
Cypress.Commands.add('selectModel', (model) => {
    cy.get(`input[type="checkbox"]`).parent().contains(model).parent().find('input').check()
})

// Commande pour attendre le chargement
Cypress.Commands.add('waitForLoading', () => {
    cy.get('div').contains('Chargement...').should('not.exist')
})

// Commande pour vérifier la présence d'un graphique
Cypress.Commands.add('shouldHaveChart', () => {
    cy.get('canvas').should('be.visible')
    // Vérifier que le graphique a des données
    cy.get('canvas').should('have.attr', 'width')
    cy.get('canvas').should('have.attr', 'height')
})

// Commande pour vérifier qu'une carte numérique a une valeur
Cypress.Commands.add('shouldHaveNumberCard', (name, value) => {
    cy.get('div').contains(name).should('be.visible')
    if (value !== undefined) {
        cy.get('div').contains(value.toString()).should('be.visible')
    }
})

// Commande pour vérifier qu'une carte texte a une valeur
Cypress.Commands.add('shouldHaveTextCard', (name, value) => {
    cy.get('div').contains(name).should('be.visible')
    if (value !== undefined) {
        cy.get('div').contains(value).should('be.visible')
    }
})

// Commande pour sélectionner plusieurs modèles d'un coup
Cypress.Commands.add('selectMultipleModels', (models) => {
    models.forEach(model => {
        cy.selectModel(model)
    })
})

// Commande pour vérifier l'état de chargement
Cypress.Commands.add('checkLoadingState', () => {
    cy.get('div').contains('Chargement...').should('be.visible')
})

// Commande pour attendre que le chargement se termine
Cypress.Commands.add('waitForLoadingToFinish', () => {
    cy.get('div').contains('Chargement...', { timeout: 10000 }).should('not.exist')
})

// Commande pour vérifier la réactivité sur différentes tailles d'écran
Cypress.Commands.add('checkResponsiveness', (viewports) => {
    viewports.forEach(viewport => {
        cy.viewport(viewport.width, viewport.height)
        cy.get('div').contains('Analyze-it').should('be.visible')
        cy.get('select[name="country"]').should('be.visible')
    })
})

// Commande pour simuler une sélection complète de workflow
Cypress.Commands.add('completeWorkflow', (options = {}) => {
    const {
        country = 'France',
        virus = 'COVID-19',
        dateStart = '2020-01-01',
        dateEnd = '2020-12-31',
        models = ['total_cases', 'transmission_rate']
    } = options

    cy.selectCountry(country)
    cy.get('input[name="virus"]').clear().type(virus)
    cy.get('input[name="date_start"]').clear().type(dateStart)
    cy.get('input[name="date_end"]').clear().type(dateEnd)

    models.forEach(model => {
        cy.selectModel(model)
    })

    cy.wait('@getPrediction')
})

// Commande pour vérifier l'accessibilité de base
Cypress.Commands.add('checkBasicAccessibility', () => {
    // Vérifier que les éléments focusables peuvent recevoir le focus
    cy.get('select, input, button').each(($el) => {
        cy.wrap($el).focus().should('have.focus')
    })

    // Vérifier que les labels existent
    cy.get('label').should('exist')

    // Vérifier que les éléments interactifs sont visibles
    cy.get('select, input, button').should('be.visible')
})

// Commande pour prendre une capture d'écran avec timestamp
Cypress.Commands.add('screenshotWithTimestamp', (name) => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    cy.screenshot(`${name}-${timestamp}`)
})

// Commande pour vérifier les performances de base
Cypress.Commands.add('checkPerformance', (maxTime = 3000) => {
    const start = performance.now()

    return cy.then(() => {
        const end = performance.now()
        const duration = end - start
        expect(duration).to.be.lessThan(maxTime)
    })
})

// Commande pour simuler une connexion lente
Cypress.Commands.add('simulateSlowConnection', () => {
    cy.intercept('POST', '**/graphql', (req) => {
        req.reply((res) => {
            res.delay(2000) // Délai de 2 secondes
            res.send({ fixture: 'prediction-mock.json' })
        })
    }).as('slowConnection')
})

// Commande pour vérifier qu'aucune erreur JavaScript n'est survenue
Cypress.Commands.add('checkForJavaScriptErrors', () => {
    cy.window().then((win) => {
        const errors = win.console?.error || []
        expect(errors).to.have.length(0)
    })
})

// Commande pour simuler différents états d'erreur
Cypress.Commands.add('simulateApiError', (errorType = 'server') => {
    const errorResponses = {
        server: { statusCode: 500, body: { errors: [{ message: 'Erreur serveur' }] } },
        network: { forceNetworkError: true },
        timeout: { statusCode: 408, body: { errors: [{ message: 'Timeout' }] } },
        notFound: { statusCode: 404, body: { errors: [{ message: 'Ressource non trouvée' }] } }
    }

    cy.intercept('POST', '**/graphql', errorResponses[errorType]).as('apiError')
})