export default function NumberCard({ name, value }) {
    return (
        <div className="text-black">
            <p>{name}</p>
            <p>{value}</p>
        </div>
    )
}