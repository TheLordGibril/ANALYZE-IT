// LineChart.jsx
import { Line } from 'react-chartjs-2'
import {
    Chart as ChartJS,
    LineElement,
    PointElement,
    LinearScale,
    CategoryScale,
    Tooltip,
    Legend,
} from 'chart.js'

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend)

export default function GraphCard({ labels, dataPoints, label = "Dataset" }) {
    const data = {
        labels: labels,
        datasets: [
            {
                label: label,
                data: dataPoints,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                tension: 0.3,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6,
            }
        ]
    }

    const options = {
        responsive: true,
        plugins: {
            legend: { display: true },
            tooltip: { mode: 'index', intersect: false },
        },
        scales: {
            x: { grid: { display: false } },
            y: { beginAtZero: true },
        }
    }

    return <Line data={data} options={options} />
}
