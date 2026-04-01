import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/Card'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'

export function Dashboard() {
  const [events, setEvents] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(false)
  }, [])

  return (
    <div className="min-h-screen bg-[#F4F4F0] p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-8 font-[Archivo]">Dashboard</h1>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card>
              <h3 className="text-lg font-bold mb-2 font-[Archivo]">Today's Events</h3>
              <p className="text-3xl font-bold text-[#FF6B6B]">0</p>
            </Card>
            <Card>
              <h3 className="text-lg font-bold mb-2 font-[Archivo]">This Week</h3>
              <p className="text-3xl font-bold text-[#51CF66]">0</p>
            </Card>
            <Card>
              <h3 className="text-lg font-bold mb-2 font-[Archivo]">Completed</h3>
              <p className="text-3xl font-bold text-[#000000]">0</p>
            </Card>
          </div>

          <Card className="mb-8">
            <h2 className="text-2xl font-bold mb-4 font-[Archivo]">Upcoming Events</h2>
            {loading ? (
              <p className="text-[#666666]">Loading...</p>
            ) : events.length === 0 ? (
              <p className="text-[#666666]">No events scheduled. Create one to get started!</p>
            ) : (
              <div className="space-y-3">
                {events.map((event: any) => (
                  <div key={event.id} className="flex justify-between items-center border-b-2 border-black pb-3">
                    <div>
                      <p className="font-bold font-[Archivo]">{event.title}</p>
                      <p className="text-sm text-[#666666]">{event.time}</p>
                    </div>
                    <Badge variant="accent">{event.category}</Badge>
                  </div>
                ))}
              </div>
            )}
          </Card>

          <div className="flex gap-4">
            <Button variant="primary">Create Event</Button>
            <Button variant="secondary">Sync Calendar</Button>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default Dashboard
