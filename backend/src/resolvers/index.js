import prisma from "../prisma.js";
import axios from "axios";
import bcrypt from "bcryptjs";
import { GraphQLError } from "graphql";
import { generateToken, requireAuth } from "../utils/auth.js";

const resolvers = {
  Query: {
    predictPandemic: async (_, { country, virus, date_start, date_end }, { user }) => {
      requireAuth(user);
      try {
        const apiUrl = process.env.API_IA_URL || 'http://127.0.0.1:8000';
        const response = await axios.get(`${apiUrl}/predict`, {
          params: { country, virus, date_start, date_end },
        });
        return response.data;
      } catch (error) {
        console.error("Erreur lors de l'appel à l'API ML:", error.message);
        throw new Error("Erreur API ML");
      }
    },
    me: async (_, __, { user }) => {
      requireAuth(user);
      return user;
    },
    pays: async (_, { id_pays }, { user }) => {
      requireAuth(user);

      return prisma.pays.findUnique({
        where: {id_pays: parseInt(id_pays)},
      });
    },
    allPays: async () => {
      return prisma.pays.findMany();
    },

    virus: async (_, { id_virus }, { user }) => {
      requireAuth(user);
      return prisma.virus.findUnique({
        where: {id_virus: parseInt(id_virus)},
      });
    },
    allVirus: async () => {
      return prisma.virus.findMany();
    },

    saison: async (_, { id_saison }, { user }) => {
      requireAuth(user);
      return prisma.saisons.findUnique({
        where: {id_saison: parseInt(id_saison)},
      });
    },
    allSaisons: async () => {
      return prisma.saisons.findMany();
    },

    statistique: async (_, { id_stat }, { user }) => {
      requireAuth(user);
      return prisma.statistiquesJournalieres.findUnique({
        where: {id_stat: BigInt(id_stat)},
      });
    },
    statistiquesByPays: async (_, { id_pays }, { user }) => {
      requireAuth(user);
      return prisma.statistiquesJournalieres.findMany({
        where: {id_pays: parseInt(id_pays)},
      });
    },
    statistiquesByVirus: async (_, { id_virus }, { user }) => {
      requireAuth(user);
      return prisma.statistiquesJournalieres.findMany({
        where: {id_virus: parseInt(id_virus)},
      });
    },
    statistiquesByDate: async (_, { date }, { user }) => {
      requireAuth(user);
      return prisma.statistiquesJournalieres.findMany({
        where: {date: new Date(date)},
      });
    },
    allStatistiques: async (_, __, { user }) => {
      requireAuth(user);
      return prisma.statistiquesJournalieres.findMany();
    },
  },

  Mutation: {
    createPays: async (_, { nom_pays }, { user }) => {
      requireAuth(user);
      return prisma.pays.create({
        data: {nom_pays},
      });
    },
    updatePays: async (_, { id_pays, nom_pays }, { user }) => {
      requireAuth(user);
      return prisma.pays.update({
        where: {id_pays: parseInt(id_pays)},
        data: {nom_pays},
      });
    },
    deletePays: async (_, { id_pays }, { user }) => {
      requireAuth(user);
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

    createVirus: async (_, { nom_virus }, { user }) => {
      requireAuth(user);
      return prisma.virus.create({
        data: {nom_virus},
      });
    },
    updateVirus: async (_, { id_virus, nom_virus }, { user }) => {
      requireAuth(user);
      return prisma.virus.update({
        where: {id_virus: parseInt(id_virus)},
        data: {nom_virus},
      });
    },
    deleteVirus: async (_, { id_virus }, { user }) => {
      requireAuth(user);
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

    createStatistique: async (_, {id_pays, id_virus, date, nouveaux_cas = 0, nouveaux_deces = 0, total_cas = 0, total_deces = 0}, { user }) => {
      requireAuth(user);
      return prisma.statistiquesJournalieres.create({
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
    updateStatistique: async (_, { id_stat, nouveaux_cas, nouveaux_deces, total_cas, total_deces }, { user }) => {
      requireAuth(user);
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
    deleteStatistique: async (_, { id_stat }, { user }) => {
      requireAuth(user);
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
    register: async (_, { email, password, nom, prenom }) => {
      const existingUser = await prisma.user.findUnique({
        where: { email }
      });

      if (existingUser) {
        throw new GraphQLError("Un utilisateur avec cet email existe déjà", {
          extensions: { code: "USER_ALREADY_EXISTS" }
        });
      }

      const hashedPassword = await bcrypt.hash(password, 12);

      const user = await prisma.user.create({
        data: {
          email,
          password: hashedPassword,
          nom,
          prenom
        }
      });

      const token = generateToken(user.id_user);

      return {
        token,
        user: {
          id_user: user.id_user,
          email: user.email,
          nom: user.nom,
          prenom: user.prenom,
          role: user.role,
          created_at: user.created_at.toISOString()
        }
      };
    },
    login: async (_, { email, password }) => {
      const user = await prisma.user.findUnique({
        where: { email }
      });

      if (!user) {
        throw new GraphQLError("Email ou mot de passe incorrect", {
          extensions: { code: "INVALID_CREDENTIALS" }
        });
      }

      const isValid = await bcrypt.compare(password, user.password);

      if (!isValid) {
        throw new GraphQLError("Email ou mot de passe incorrect", {
          extensions: { code: "INVALID_CREDENTIALS" }
        });
      }

      const token = generateToken(user.id_user);

      return {
        token,
        user: {
          id_user: user.id_user,
          email: user.email,
          nom: user.nom,
          prenom: user.prenom,
          role: user.role,
          created_at: user.created_at.toISOString()
        }
      };
    },
  },

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
