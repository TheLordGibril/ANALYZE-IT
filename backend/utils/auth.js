import jwt from "jsonwebtoken";
import { GraphQLError } from "graphql";

export const generateToken = (userId) => {
  return jwt.sign({ userId }, process.env.KEY, {
    expiresIn: process.env.JWT_EXPIRES || "7d",
  });
};

export const requireAuth = (user) => {
  if (!user) {
    throw new GraphQLError("Vous devez être connecté", {
      extensions: {
        code: "UNAUTHENTICATED",
      },
    });
  }
  return user;
};
