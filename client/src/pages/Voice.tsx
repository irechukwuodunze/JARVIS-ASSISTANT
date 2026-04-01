import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/Card'
import { Button } from '@/components/Button'
import { Badge } from '@/components/Badge'

export function Voice() {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [status, setStatus] = useState<'idle' | 'listening' | 'processing' | 'speaking'>('idle')
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])

  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data)
      }

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        setStatus('processing')
        setTranscript('Processing audio...')
      }

      mediaRecorder.start()
      setStatus('listening')
      setIsListening(true)
    } catch (error) {
      console.error('Microphone access denied:', error)
    }
  }

  const stopListening = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
    }
    setIsListening(false)
  }

  return (
    <div className="min-h-screen bg-[#F4F4F0] flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-md"
      >
        <Card>
          <h1 className="text-3xl font-bold mb-6 font-[Archivo] text-center">Voice Command</h1>

          <div className="mb-8 text-center">
            <motion.div
              animate={status === 'listening' ? { scale: [1, 1.1, 1] } : {}}
              transition={{ duration: 0.6, repeat: Infinity }}
              className="inline-block"
            >
              <div className={`w-24 h-24 rounded-full border-4 border-black flex items-center justify-center mb-4 ${
                status === 'listening' ? 'bg-[#FF6B6B]' : 'bg-white'
              }`}>
                <span className="text-2xl font-bold font-[Archivo]">
                  {status === 'listening' ? '●' : '○'}
                </span>
              </div>
            </motion.div>

            <Badge variant={status === 'listening' ? 'accent' : 'default'} className="mb-4">
              {status === 'idle' && 'Ready'}
              {status === 'listening' && 'Listening...'}
              {status === 'processing' && 'Processing...'}
              {status === 'speaking' && 'Speaking...'}
            </Badge>
          </div>

          {transcript && (
            <div className="mb-6 p-4 bg-white border-2 border-black">
              <p className="text-sm text-[#666666] mb-2 font-[Inter]">Transcript:</p>
              <p className="font-[Inter]">{transcript}</p>
            </div>
          )}

          <div className="flex gap-3">
            {!isListening ? (
              <Button variant="primary" onClick={startListening} className="flex-1">
                Start Listening
              </Button>
            ) : (
              <Button variant="error" onClick={stopListening} className="flex-1">
                Stop
              </Button>
            )}
          </div>

          <p className="text-xs text-[#666666] mt-4 text-center font-[Inter]">
            Press spacebar or click the button to start voice command
          </p>
        </Card>
      </motion.div>
    </div>
  )
}

export default Voice
