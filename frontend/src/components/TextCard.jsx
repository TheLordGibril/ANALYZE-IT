export default function TextCard({ name, text }) {
    return (
        <div className="text-black">
            <p>{name}</p>
            <p>{text}</p>
        </div>
    )
}