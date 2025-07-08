export default function NumberCard({ name, value }) {
    if (value === undefined || value === null) return <p>—</p>;
    return (
        <div id={name} className="w-40 h-40 mr-5 bg-white rounded-2xl shadow-lg p-6 flex flex-col justify-center items-center transition-transform hover:scale-[1.02] hover:shadow-xl text-center space-y-2">
            <p className="text-gray-700 text-sm">{name}</p>
            <p className="text-3xl font-bold text-blue-600">{value}</p>
        </div>
    );
}
