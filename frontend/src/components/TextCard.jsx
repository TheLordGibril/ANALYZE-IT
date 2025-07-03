import usePrediction from "../services/usePrediction"

export default function TextCard({ name, value, parameters }) {
    const { prediction, loading, error } = usePrediction({ country: parameters.country, virus: parameters.virus, dateStart: parameters.date_start, dateEnd: parameters.date_end });

    if (loading) return <p>Chargement...</p>;
    if (error) return <p>Erreur: {error.message}</p>;
    return (
        <div className="w-40 h-40 bg-white rounded-2xl shadow-lg p-6 flex flex-col justify-center items-center transition-transform hover:scale-[1.02] hover:shadow-xl text-center space-y-2">
            <p className="text-gray-700 text-sm">{name}</p>
            <p className="text-3xl font-bold text-blue-600">
                {prediction?.predictions?.[name].map((elt, index) => (
                    <span key={index}>
                        {elt}
                        {index < prediction.predictions[name].length - 1 ? ', ' : ''}
                    </span>
                ))}
            </p>
        </div>
    )
}