import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/Card'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'

export function FocusMode() {
  const [isActive, setIsActive] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [checkInsCompleted, setCheckInsCompleted] = useState(0)
  const [totalCheckIns, setTotalCheckIns] = useState(0)
  const [nextCheckInTime, setNextCheckInTime] = useState<Date | null>(null)
  const [proofOfWorkUrl, setProofOfWorkUrl] = useState('')
  const [history, setHistory] = useState([])

  useEffect(() => {
    let interval: NodeJS.Timeout
    if (isActive && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining((prev) => prev - 1)
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [isActive, timeRemaining])

  const handleStartFocusMode = async () => {
    setIsActive(true)
    setSessionId('session-123')
    setTimeRemaining(90 * 60) // 90 minutes in seconds
    setCheckInsCompleted(0)
    setTotalCheckIns(4)
    setNextCheckInTime(new Date(Date.now() + 25 * 60 * 1000))
  }

  const handleCheckIn = async () => {
    setCheckInsCompleted((prev) => prev + 1)
    setNextCheckInTime(new Date(Date.now() + 25 * 60 * 1000))
  }

  const handleEndFocusMode = async () => {
    setIsActive(false)
    setSessionId(null)
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const checkInProgress = (checkInsCompleted / totalCheckIns) * 100

  return (
    <div className="min-h-screen bg-[#F4F4F0] p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold mb-8 font-[Archivo]">Focus Mode</h1>

          {!isActive ? (
            <Card className="mb-8 text-center">
              <h2 className="text-2xl font-bold mb-4 font-[Archivo]">Ready to Focus?</h2>
              <p className="text-[#666666] mb-6 font-[Inter]">
                Start a deep work session. You'll need to check in every 25 minutes to prove you're working.
              </p>
              <Button variant="primary" onClick={handleStartFocusMode} className="text-lg">
                Start Focus Mode (90 min)
              </Button>
            </Card>
          ) : (
            <>
              {/* Active Session */}
              <Card className="mb-8">
                <div className="text-center mb-6">
                  <motion.div
                    animate={{ scale: [1, 1.05, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="inline-block"
                  >
                    <div className="w-32 h-32 rounded-full border-4 border-black flex items-center justify-center bg-[#51CF66] mb-4">
                      <span className="text-5xl font-bold font-[Archivo]">
                        {formatTime(timeRemaining)}
                      </span>
                    </div>
                  </motion.div>

                  <p className="text-2xl font-bold font-[Archivo] mb-2">Focus Mode Active</p>
                  <p className="text-[#666666] font-[Inter]">
                    {checkInsCompleted} of {totalCheckIns} check-ins completed
                  </p>
                </div>

                {/* Check-in Progress */}
                <div className="mb-6">
                  <div className="w-full bg-white border-2 border-black h-8">
                    <div
                      className="bg-[#51CF66] h-full border-r-2 border-black transition-all"
                      style={{ width: `${checkInProgress}%` }}
                    />
                  </div>
                </div>

                {/* Next Check-in */}
                {nextCheckInTime && (
                  <div className="mb-6 p-4 bg-white border-2 border-black">
                    <p className="text-sm font-bold font-[Archivo] mb-2">Next Check-in:</p>
                    <p className="text-lg font-[Archivo]">
                      {nextCheckInTime.toLocaleTimeString()}
                    </p>
                  </div>
                )}

                {/* Proof of Work */}
                <div className="mb-6">
                  <label className="block text-sm font-bold mb-2 font-[Archivo]">
                    Proof of Work (Optional Photo)
                  </label>
                  <input
                    type="file"
                    accept="image/*"
                    className="w-full border-2 border-black p-3"
                    onChange={(e) => {
                      const file = e.target.files?.[0]
                      if (file) {
                        const reader = new FileReader()
                        reader.onload = (event) => {
                          setProofOfWorkUrl(event.target?.result as string)
                        }
                        reader.readAsDataURL(file)
                      }
                    }}
                  />
                  {proofOfWorkUrl && (
                    <img src={proofOfWorkUrl} alt="Proof of work" className="mt-3 max-w-xs border-2 border-black" />
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-4">
                  <Button variant="primary" onClick={handleCheckIn} className="flex-1">
                    Check In Now
                  </Button>
                  <Button variant="secondary" onClick={handleEndFocusMode}>
                    End Session
                  </Button>
                </div>
              </Card>

              {/* Savage PA Message */}
              <Card className="bg-[#FFE5E5] border-[#FF6B6B]">
                <h3 className="text-lg font-bold mb-2 font-[Archivo] text-[#FF6B6B]">Savage PA</h3>
                <p className="font-[Inter]">
                  You've been focused for {Math.floor(timeRemaining / 60)} minutes. Don't break the chain. Check in when the timer hits 25 minutes.
                </p>
              </Card>
            </>
          )}

          {/* History */}
          {history.length > 0 && (
            <Card className="mt-8">
              <h2 className="text-2xl font-bold mb-4 font-[Archivo]">Focus History</h2>
              <div className="space-y-3">
                {history.map((session: any) => (
                  <div key={session.id} className="flex justify-between items-center border-b-2 border-black pb-3">
                    <div>
                      <p className="font-bold font-[Archivo]">{session.date}</p>
                      <p className="text-sm text-[#666666]">{session.duration} minutes</p>
                    </div>
                    <Badge variant={session.completed ? 'success' : 'error'}>
                      {session.completed ? 'Completed' : 'Failed'}
                    </Badge>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      </motion.div>
    </div>
  )
}

export default FocusMode
