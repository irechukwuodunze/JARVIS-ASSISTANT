import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/Card'
import { Badge } from '@/components/Badge'

export function Analytics() {
  const [metrics, setMetrics] = useState({
    average_efficiency_score: 0,
    peak_efficiency_time: null,
    peak_efficiency_mood: null,
    low_efficiency_time: null,
    low_efficiency_mood: null,
    mood_time_correlation: {},
  })
  const [heatmap, setHeatmap] = useState({})
  const [phaseEfficiency, setPhaseEfficiency] = useState({})
  const [timeRange, setTimeRange] = useState(7)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(false)
  }, [timeRange])

  const moodColors = {
    drained: '#FF6B6B',
    unfocused: '#FFD93D',
    focused: '#51CF66',
    energized: '#4ECDC4',
  }

  const hours = Array.from({ length: 24 }, (_, i) => i)
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

  return (
    <div className="min-h-screen bg-[#F4F4F0] p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl font-bold mb-8 font-[Archivo]">Time-Audit Dashboard</h1>

          {/* Time Range Selector */}
          <div className="flex gap-2 mb-8">
            {[1, 7, 30].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                className={`px-4 py-2 font-bold font-[Archivo] border-2 border-black ${
                  timeRange === range
                    ? 'bg-black text-white'
                    : 'bg-white text-black'
                }`}
              >
                Last {range === 1 ? '24h' : range === 7 ? '7d' : '30d'}
              </button>
            ))}
          </div>

          {/* Efficiency Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <Card>
              <h3 className="text-lg font-bold mb-4 font-[Archivo]">Average Efficiency</h3>
              <p className="text-4xl font-bold text-[#51CF66]">
                {metrics.average_efficiency_score.toFixed(1)}%
              </p>
              <p className="text-sm text-[#666666] mt-2 font-[Inter]">
                Peak at {metrics.peak_efficiency_time} when {metrics.peak_efficiency_mood}
              </p>
            </Card>

            <Card>
              <h3 className="text-lg font-bold mb-4 font-[Archivo]">Mood-Time Correlation</h3>
              <div className="space-y-2">
                {Object.entries(metrics.mood_time_correlation).map(([mood, score]: [string, any]) => (
                  <div key={mood} className="flex items-center justify-between">
                    <Badge variant={mood as any}>{mood}</Badge>
                    <div className="w-32 bg-white border-2 border-black h-6">
                      <div
                        className="h-full transition-all"
                        style={{
                          width: `${(score / 100) * 100}%`,
                          backgroundColor: moodColors[mood as keyof typeof moodColors] || '#000000',
                        }}
                      />
                    </div>
                    <p className="text-sm font-bold font-[Archivo]">{score.toFixed(0)}%</p>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Productivity Heatmap */}
          <Card className="mb-8">
            <h2 className="text-2xl font-bold mb-6 font-[Archivo]">Productivity Heatmap</h2>
            <div className="overflow-x-auto">
              <div className="inline-block">
                {/* Day labels */}
                <div className="flex">
                  <div className="w-12" /> {/* Spacer for hour labels */}
                  {days.map((day) => (
                    <div key={day} className="w-16 text-center font-bold font-[Archivo] text-sm mb-2">
                      {day}
                    </div>
                  ))}
                </div>

                {/* Heatmap grid */}
                {hours.map((hour) => (
                  <div key={hour} className="flex items-center">
                    <div className="w-12 text-xs font-bold font-[Archivo] text-right pr-2">
                      {hour.toString().padStart(2, '0')}:00
                    </div>
                    {days.map((day) => (
                      <div
                        key={`${day}-${hour}`}
                        className="w-16 h-12 border border-black m-0.5"
                        style={{
                          backgroundColor: heatmap[`${day}_${hour}`]
                            ? `rgba(81, 207, 102, ${heatmap[`${day}_${hour}`] / 100})`
                            : '#FFFFFF',
                        }}
                        title={`${day} ${hour}:00 - ${heatmap[`${day}_${hour}`]?.toFixed(0) || 0}%`}
                      />
                    ))}
                  </div>
                ))}
              </div>
            </div>
            <p className="text-xs text-[#666666] mt-4 font-[Inter]">
              Darker green = higher productivity. Hover to see exact efficiency score.
            </p>
          </Card>

          {/* Phase Efficiency */}
          <Card>
            <h2 className="text-2xl font-bold mb-6 font-[Archivo]">Project Phase Efficiency</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(phaseEfficiency).map(([phase, data]: [string, any]) => (
                <div key={phase} className="border-2 border-black p-4">
                  <h3 className="font-bold font-[Archivo] mb-3">{phase}</h3>
                  <div className="space-y-2">
                    <p className="text-sm font-[Inter]">
                      Time: <span className="font-bold">{(data.total_time_minutes / 60).toFixed(1)}h</span>
                    </p>
                    <p className="text-sm font-[Inter]">
                      Efficiency: <span className="font-bold">{data.average_efficiency.toFixed(0)}%</span>
                    </p>
                    <div className="w-full bg-white border-2 border-black h-4">
                      <div
                        className="bg-[#51CF66] h-full transition-all"
                        style={{ width: `${data.average_efficiency}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </motion.div>
    </div>
  )
}

export default Analytics
