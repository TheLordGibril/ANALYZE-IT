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

const verticalLineWithPointPlugin = {
    id: 'verticalLineWithPointOnHover',
    afterDraw: (chart) => {
        if (chart.tooltip?._active && chart.tooltip._active.length) {
            const ctx = chart.ctx;
            const activePoint = chart.tooltip._active[0].element;
            const x = activePoint.x;
            const y = activePoint.y;

            ctx.save();
            ctx.beginPath();
            ctx.setLineDash([8, 4]);
            ctx.moveTo(x, chart.chartArea.top);
            ctx.lineTo(x, chart.chartArea.bottom);
            ctx.lineWidth = 2;
            ctx.strokeStyle = '#888';
            ctx.stroke();
            ctx.restore();

            ctx.save();
            ctx.beginPath();
            ctx.arc(x, y, 6, 0, 2 * Math.PI);
            ctx.fillStyle = '#4285F4';
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.fill();
            ctx.stroke();
            ctx.restore();
        }
    }
}

export default function GraphCard({ labels, datasets, title }) {
    const calculateLabelCount = () => {
        let count = 0;
        let lastMonth = null;
        let lastYear = null;

        for (let i = 0; i < labels.length; i++) {
            const label = labels[i];
            if (!label || label.length !== 10) continue;

            const year = label.slice(0, 4);
            const month = label.slice(5, 7);

            if (month !== lastMonth || year !== lastYear) {
                count++;
                lastMonth = month;
                lastYear = year;
            }
        }

        return count;
    };

    const labelCount = calculateLabelCount();
    const showOnlyYears = labelCount > 20;

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
                ticks: {
                    display: true,
                    autoSkip: false,
                    maxRotation: 0,
                    callback: function (value, index, ticks) {
                        const label = this.getLabelForValue(value);

                        if (!label || label.length !== 10) return '';

                        const anneeActuelle = label.slice(0, 4);
                        const moisActuel = label.slice(5, 7);

                        if (showOnlyYears) {
                            const labelPrecedent = index > 0 ? labels[index - 1] : null;
                            const anneePrecedente = labelPrecedent ? labelPrecedent.slice(0, 4) : null;

                            if (!anneePrecedente || anneeActuelle !== anneePrecedente) {
                                return anneeActuelle;
                            }
                            return '';
                        }

                        const labelPrecedent = index > 0 ? labels[index - 1] : null;
                        const anneePrecedente = labelPrecedent ? labelPrecedent.slice(0, 4) : null;
                        const moisPrecedent = labelPrecedent ? labelPrecedent.slice(5, 7) : null;

                        if (!labelPrecedent || moisActuel !== moisPrecedent) {
                            if (!anneePrecedente || anneeActuelle !== anneePrecedente) {
                                return anneeActuelle;
                            } else {
                                const moisNoms = [
                                    "Janv", "Févr", "Mars", "Avr", "Mai", "Juin",
                                    "Juil", "Août", "Sept", "Oct", "Nov", "Déc"
                                ];
                                return moisNoms[parseInt(moisActuel, 10) - 1];
                            }
                        }

                        return '';
                    }
                }
            },
            y: { beginAtZero: true },
        }
    }

    return (
        <div className="w-full">
            <div className="text-lg font-semibold text-gray-700 mb-2">{title}</div>
            <Line data={data} options={options} plugins={[verticalLineWithPointPlugin]} />
        </div>
    )
}