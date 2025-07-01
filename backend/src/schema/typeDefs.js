import { gql } from "graphql-tag";

const typeDefs = gql`
  type Pays {
    id_pays: ID!
    nom_pays: String!
    statistiques_journalieres: [StatistiquesJournalieres]
  }

  type Virus {
    id_virus: ID!
    nom_virus: String!
    statistiques_journalieres: [StatistiquesJournalieres]
  }

  type Saisons {
    id_saison: ID!
    nom_saison: String!
    statistiques: [StatistiquesJournalieres]
  }

  type StatistiquesJournalieres {
    id_stat: ID!
    id_pays: ID!
    id_virus: ID!
    id_saison: ID!
    date: String!
    nouveaux_cas: Int
    nouveaux_deces: Int
    total_cas: Int
    total_deces: Int
    pays: Pays
    virus: Virus
    croissance_cas: Float
    taux_mortalite: Float
    taux_infection: Float
    taux_mortalite_population: Float
    taux_infection_vs_global: Float
    taux_mortalite_pop_vs_global: Float
  }

  type Query {
    # Requêtes pour les prédictions de pandémie
    predictPandemic(country: String!, virus: String!, date: String!): JSON
    
    # Requêtes pour Pays
    pays(id_pays: ID): Pays
    allPays: [Pays]

    # Requêtes pour Virus
    virus(id_virus: ID): Virus
    allVirus: [Virus]

    saison(id_saison: ID): Saisons
    allSaisons: [Saisons]

    # Requêtes pour Statistiques
    statistique(id_stat: ID!): StatistiquesJournalieres
    statistiquesByPays(id_pays: ID!): [StatistiquesJournalieres]
    statistiquesByVirus(id_virus: ID!): [StatistiquesJournalieres]
    statistiquesByDate(date: String!): [StatistiquesJournalieres]
    allStatistiques: [StatistiquesJournalieres]
  }
  scalar JSON

  type Mutation {
    # Mutations pour Pays
    createPays(nom_pays: String!): Pays
    updatePays(id_pays: ID!, nom_pays: String!): Pays
    deletePays(id_pays: ID!): Boolean

    # Mutations pour Virus
    createVirus(nom_virus: String!): Virus
    updateVirus(id_virus: ID!, nom_virus: String!): Virus
    deleteVirus(id_virus: ID!): Boolean

    # Mutations pour Statistiques
    createStatistique(
      id_pays: ID!
      id_virus: ID!
      date: String!
      nouveaux_cas: Int
      nouveaux_deces: Int
      total_cas: Int
      total_deces: Int
    ): StatistiquesJournalieres

    updateStatistique(
      id_stat: ID!
      nouveaux_cas: Int
      nouveaux_deces: Int
      total_cas: Int
      total_deces: Int
    ): StatistiquesJournalieres

    deleteStatistique(id_stat: ID!): Boolean
  }
`;

export default typeDefs;
