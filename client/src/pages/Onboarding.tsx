import { useState } from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/Card'
import { Button } from '@/components/Button'
import { Input } from '@/components/Input'

export function Onboarding() {
  const [step, setStep] = useState(0)
  const [persona, setPersona] = useState({
    wake_up_time: '',
    daily_goals: [],
    procrastination_task: '',
    energy_pattern: '',
    preferred_workout_time: '',
  })

  const steps = [
    {
      title: 'What time do you wake up?',
      key: 'wake_up_time',
      type: 'time',
    },
    {
      title: 'What are your top 3 daily goals?',
      key: 'daily_goals',
      type: 'text',
    },
    {
      title: 'What task do you procrastinate on most?',
      key: 'procrastination_task',
      type: 'text',
    },
    {
      title: 'Describe your energy pattern throughout the day',
      key: 'energy_pattern',
      type: 'textarea',
    },
  ]

  const currentStep = steps[step]

  const handleNext = () => {
    if (step < steps.length - 1) {
      setStep(step + 1)
    } else {
      console.log('Onboarding complete:', persona)
    }
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
          <h1 className="text-3xl font-bold mb-2 font-[Archivo]">JARVIS Onboarding</h1>
          <p className="text-[#666666] mb-6 font-[Inter]">
            Let me learn about you. Step {step + 1} of {steps.length}
          </p>

          <div className="mb-6">
            <h2 className="text-xl font-bold mb-4 font-[Archivo]">{currentStep.title}</h2>
            
            {currentStep.type === 'time' && (
              <Input
                type="time"
                value={persona[currentStep.key as keyof typeof persona] as string}
                onChange={(e) =>
                  setPersona({ ...persona, [currentStep.key]: e.target.value })
                }
              />
            )}
            
            {currentStep.type === 'text' && (
              <Input
                type="text"
                placeholder="Enter your answer..."
                value={persona[currentStep.key as keyof typeof persona] as string}
                onChange={(e) =>
                  setPersona({ ...persona, [currentStep.key]: e.target.value })
                }
              />
            )}
            
            {currentStep.type === 'textarea' && (
              <textarea
                className="w-full border-2 border-black p-3 font-[Inter] focus:outline-none focus:shadow-[2px_2px_0px_rgba(0,0,0,1)]"
                rows={4}
                placeholder="Describe your energy pattern..."
                value={persona[currentStep.key as keyof typeof persona] as string}
                onChange={(e) =>
                  setPersona({ ...persona, [currentStep.key]: e.target.value })
                }
              />
            )}
          </div>

          <div className="flex gap-3">
            {step > 0 && (
              <Button variant="secondary" onClick={() => setStep(step - 1)}>
                Back
              </Button>
            )}
            <Button variant="primary" onClick={handleNext} className="flex-1">
              {step === steps.length - 1 ? 'Complete' : 'Next'}
            </Button>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}

export default Onboarding
