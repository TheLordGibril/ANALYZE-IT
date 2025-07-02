import prisma from "../prisma.js";
import axios from "axios";

import bcrypt from "bcryptjs";
import { GraphQLError } from "graphql";
import { generateToken, requireAuth } from "../utils/auth.js";

const resolvers = {
  Query: {
    // Résolveur pour prédiction de pandémie
    predictPandemic: async (_, { country, virus, date_start, date_end }) => {
      try {
        const response = await axios.get(
          `http://127.0.0.1:8000/predict`,
          {
            params: { country, virus, date_start, date_end }
          }
        );
        return response.data;
      } catch (error) {
        console.error("Erreur lors de l'appel à l'API ML:", error.message);
        throw new Error("Erreur API ML");
      }
    },
    // Résolveurs pour Pays
    pays: async (_, { id_pays }, { user }) => {
      requireAuth(user);

      return await prisma.pays.findUnique({
        where: { id_pays: parseInt(id_pays) },
      });
    },
    allPays: async () => {
      return await prisma.pays.findMany();
    },

    // Résolveurs pour Virus
    virus: async (_, { id_virus }) => {
      return await prisma.virus.findUnique({
        where: { id_virus: parseInt(id_virus) },
      });
    },
    allVirus: async () => {
      return await prisma.virus.findMany();
    },

    // Résolveurs pour Saisons
    saison: async (_, { id_saison }) => {
      return await prisma.saisons.findUnique({
        where: { id_saison: parseInt(id_saison) },
      });
    },
    allSaisons: async () => {
      return await prisma.saisons.findMany();
    },

    // Résolveurs pour Statistiques
    statistique: async (_, { id_stat }) => {
      return await prisma.statistiquesJournalieres.findUnique({
        where: { id_stat: BigInt(id_stat) },
      });
    },
    statistiquesByPays: async (_, { id_pays }) => {
      return await prisma.statistiquesJournalieres.findMany({
        where: { id_pays: parseInt(id_pays) },
      });
    },
    statistiquesByVirus: async (_, { id_virus }) => {
      return await prisma.statistiquesJournalieres.findMany({
        where: { id_virus: parseInt(id_virus) },
      });
    },
    statistiquesByDate: async (_, { date }) => {
      return await prisma.statistiquesJournalieres.findMany({
        where: { date: new Date(date) },
      });
    },
    allStatistiques: async () => {
      return await prisma.statistiquesJournalieres.findMany();
    },
  },

  Mutation: {
    login: async (_, { email, password }) => {
      const user = await prisma.user.findUnique({ where: { email } });
      if (!user) {
        throw new GraphQLError("Utilisateur non trouvé", {
          extensions: { code: "UNAUTHENTICATED" },
        });
      }

      const valid = await bcrypt.compare(password, user.password);
      if (!valid) {
        throw new GraphQLError("Mot de passe incorrect", {
          extensions: { code: "UNAUTHENTICATED" },
        });
      }

      const token = generateToken(user.id_user);

      return { token };
    },

    // Mutations pour Pays
    createPays: async (_, { nom_pays }) => {
      return await prisma.pays.create({
        data: { nom_pays },
      });
    },
    updatePays: async (_, { id_pays, nom_pays }) => {
      return await prisma.pays.update({
        where: { id_pays: parseInt(id_pays) },
        data: { nom_pays },
      });
    },
    deletePays: async (_, { id_pays }) => {
      try {
        await prisma.pays.delete({
          where: { id_pays: parseInt(id_pays) },
        });
        return true;
      } catch (error) {
        console.error("Error deleting pays:", error);
        return false;
      }
    },

    // Mutations pour Virus
    createVirus: async (_, { nom_virus }) => {
      return await prisma.virus.create({
        data: { nom_virus },
      });
    },
    updateVirus: async (_, { id_virus, nom_virus }) => {
      return await prisma.virus.update({
        where: { id_virus: parseInt(id_virus) },
        data: { nom_virus },
      });
    },
    deleteVirus: async (_, { id_virus }) => {
      try {
        await prisma.virus.delete({
          where: { id_virus: parseInt(id_virus) },
        });
        return true;
      } catch (error) {
        console.error("Error deleting virus:", error);
        return false;
      }
    },

    // Mutations pour Statistiques
    createStatistique: async (
      _,
      {
        id_pays,
        id_virus,
        date,
        nouveaux_cas = 0,
        nouveaux_deces = 0,
        total_cas = 0,
        total_deces = 0,
      }
    ) => {
      return await prisma.statistiquesJournalieres.create({
        data: {
          id_pays: parseInt(id_pays),
          id_virus: parseInt(id_virus),
          date: new Date(date),
          nouveaux_cas,
          nouveaux_deces,
          total_cas,
          total_deces,
        },
      });
    },
    updateStatistique: async (
      _,
      { id_stat, nouveaux_cas, nouveaux_deces, total_cas, total_deces }
    ) => {
      const updateData = {};
      if (nouveaux_cas !== undefined) updateData.nouveaux_cas = nouveaux_cas;
      if (nouveaux_deces !== undefined)
        updateData.nouveaux_deces = nouveaux_deces;
      if (total_cas !== undefined) updateData.total_cas = total_cas;
      if (total_deces !== undefined) updateData.total_deces = total_deces;

      return await prisma.statistiquesJournalieres.update({
        where: { id_stat: BigInt(id_stat) },
        data: updateData,
      });
    },
    deleteStatistique: async (_, { id_stat }) => {
      try {
        await prisma.statistiquesJournalieres.delete({
          where: { id_stat: BigInt(id_stat) },
        });
        return true;
      } catch (error) {
        console.error("Error deleting statistique:", error);
        return false;
      }
    },
  },

  // Résolveurs de types
  Pays: {
    statistiques_journalieres: async (parent) => {
      return await prisma.statistiquesJournalieres.findMany({
        where: { id_pays: parent.id_pays },
      });
    },
  },

  Virus: {
    statistiques_journalieres: async (parent) => {
      return await prisma.statistiquesJournalieres.findMany({
        where: { id_virus: parent.id_virus },
      });
    },
  },

  StatistiquesJournalieres: {
    pays: async (parent) => {
      return await prisma.pays.findUnique({
        where: { id_pays: parent.id_pays },
      });
    },
    virus: async (parent) => {
      return await prisma.virus.findUnique({
        where: { id_virus: parent.id_virus },
      });
    },
  },
};

export default resolvers;
