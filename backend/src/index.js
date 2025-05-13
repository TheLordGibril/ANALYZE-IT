import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import dotenv from 'dotenv';
import typeDefs from './schema/typeDefs.js';
import resolvers from './resolvers/index.js';
import prisma from './prisma.js';

// Charger les variables d'environnement
dotenv.config();

// Créer le serveur Apollo
const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: ({ req }) => {
    return {
      prisma,
      req
    };
  },
  formatError: (error) => {
    console.error('GraphQL Error:', error);
    return error;
  },
  csrfPrevention: false,
});

// Démarrer le serveur
const PORT = process.env.PORT || 4000;
async function startServer() {
  const { url } = await startStandaloneServer(server, {
    listen: { port: PORT },
    context: async ({ req }) => {
      return {
        prisma,
        req
      };
    },
  });
  console.log(`🚀 Serveur Apollo prêt à l'adresse ${url}`);
}

startServer();

// Fermeture propre du client Prisma lors de l'arrêt de l'application
process.on('SIGINT', () => {
  prisma.$disconnect();
  process.exit(0);
});