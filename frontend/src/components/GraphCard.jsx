import { Line } from 'react-chartjs-2'
import {
    Chart as ChartJS,
    LineElement,
    PointElement,
    LinearScale,
    CategoryScale,
    Tooltip,
    Legend,
    Filler,
} from 'chart.js'

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend, Filler)

export default function GraphCard({ labels, datasets }) {
    const data = {
        labels,
        datasets: datasets.map(set => ({
            label: set.label,
            data: set.data,
            borderColor: set.color,
            backgroundColor: set.color + '33',
            tension: 0.3,
            fill: true,
            pointRadius: 0,
            pointHoverRadius: 6,
            borderDash: set.dashed ? [8, 4] : [],
        }))
    }

    const options = {
        responsive: true,
        plugins: {
            legend: { display: true },
            tooltip: { mode: 'index', intersect: false },
            filler: { propagate: false },
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: { display: false },
            },
            y: { beginAtZero: true },
        }
    }

    return (
        <div className="w-full">
            <Line data={data} options={options} />
        </div>
    )
}
