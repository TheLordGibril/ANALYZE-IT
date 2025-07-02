import axios from "axios";

const API_URL = "http://127.0.0.1:8000/predict";

export const fetchPrediction = async ({ country, virus, date_start, date_end }) => {
  try {
    const response = await axios.get(API_URL, {
      params: { country, virus, date_start, date_end },
    });
    return response.data;
  } catch (error) {
    console.error("Erreur API:", error);
    throw error;
  }
};
