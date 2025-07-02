import usePrediction from "../services/usePrediction"

export default function TextCard({ name, value, parameters }) {
    const { prediction, loading, error } = usePrediction({ country: parameters.country, virus: parameters.virus, dateStart: parameters.date_start, dateEnd: parameters.date_end });

    if (loading) return <p>Chargement...</p>;
    if (error) return <p>Erreur: {error.message}</p>;
    return (
        <div className="text-black">
            <p>{name}</p>
            {console.log("Prediction data:", prediction)}
            {console.log(loading)}
            <p>{prediction && prediction.predictions[name]}</p>
        </div>
    )
}