import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/Card'
import { Button } from '@/components/Button'
import { Input } from '@/components/Input'
import { Badge } from '@/components/Badge'

export function Finance() {
  const [expenses, setExpenses] = useState([])
  const [summary, setSummary] = useState({
    total_spent: 0,
    monthly_budget: 500,
    percentage_used: 0,
    burn_rate: 0,
    days_until_budget_exhausted: 0,
    flagged_expenses: [],
  })
  const [newExpense, setNewExpense] = useState({
    amount: '',
    category: 'food',
    description: '',
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(false)
  }, [])

  const handleLogExpense = async () => {
    if (!newExpense.amount || !newExpense.description) return
    setNewExpense({ amount: '', category: 'food', description: '' })
  }

  const daysRemaining = Math.ceil(summary.days_until_budget_exhausted)
  const budgetPercentage = Math.min(summary.percentage_used, 100)

  return (
    <div className="min-h-screen bg-[#F4F4F0] p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl font-bold mb-8 font-[Archivo]">CFO Dashboard</h1>

          {/* Budget Status */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card>
              <h3 className="text-lg font-bold mb-2 font-[Archivo]">Total Spent</h3>
              <p className="text-3xl font-bold text-[#FF6B6B]">£{summary.total_spent.toFixed(2)}</p>
              <p className="text-sm text-[#666666] mt-2">of £{summary.monthly_budget}</p>
            </Card>

            <Card>
              <h3 className="text-lg font-bold mb-2 font-[Archivo]">Budget Status</h3>
              <div className="mb-3">
                <div className="w-full bg-white border-2 border-black h-8">
                  <div
                    className="bg-[#FF6B6B] h-full border-r-2 border-black transition-all"
                    style={{ width: `${budgetPercentage}%` }}
                  />
                </div>
              </div>
              <p className="text-sm font-bold font-[Archivo]">{summary.percentage_used.toFixed(1)}% Used</p>
            </Card>

            <Card>
              <h3 className="text-lg font-bold mb-2 font-[Archivo]">Days Remaining</h3>
              <p className={`text-3xl font-bold ${daysRemaining > 7 ? 'text-[#51CF66]' : 'text-[#FF6B6B]'}`}>
                {daysRemaining}
              </p>
              <p className="text-sm text-[#666666] mt-2">at current burn rate</p>
            </Card>
          </div>

          {/* Burn Rate Warning */}
          {summary.burn_rate > 0 && (
            <Card className="mb-8 bg-[#FFF3CD] border-[#FF6B6B]">
              <h3 className="text-lg font-bold mb-2 font-[Archivo] text-[#FF6B6B]">Savage CFO Alert</h3>
              <p className="font-[Inter] text-black">
                You're burning £{summary.burn_rate.toFixed(2)} per day. At this rate, you'll run out in {daysRemaining} days.
                {summary.percentage_used > 50 && " Time to cut back."}
              </p>
            </Card>
          )}

          {/* Log New Expense */}
          <Card className="mb-8">
            <h2 className="text-2xl font-bold mb-4 font-[Archivo]">Log Expense</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <Input
                label="Amount (£)"
                type="number"
                placeholder="0.00"
                value={newExpense.amount}
                onChange={(e) => setNewExpense({ ...newExpense, amount: e.target.value })}
              />
              <div className="mb-4">
                <label className="block text-sm font-bold mb-2 font-[Archivo]">Category</label>
                <select
                  className="w-full border-2 border-black p-3 font-[Inter] focus:outline-none focus:shadow-[2px_2px_0px_rgba(0,0,0,1)]"
                  value={newExpense.category}
                  onChange={(e) => setNewExpense({ ...newExpense, category: e.target.value })}
                >
                  <option value="food">Food</option>
                  <option value="transport">Transport</option>
                  <option value="materials">Materials</option>
                  <option value="software">Software</option>
                  <option value="entertainment">Entertainment</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <Input
                label="Description"
                placeholder="What did you buy?"
                value={newExpense.description}
                onChange={(e) => setNewExpense({ ...newExpense, description: e.target.value })}
              />
            </div>
            <Button variant="primary" onClick={handleLogExpense}>
              Log Expense
            </Button>
          </Card>

          {/* Flagged Expenses */}
          {summary.flagged_expenses.length > 0 && (
            <Card className="mb-8">
              <h2 className="text-2xl font-bold mb-4 font-[Archivo] text-[#FF6B6B]">Flagged by CFO</h2>
              <div className="space-y-4">
                {summary.flagged_expenses.map((expense: any) => (
                  <div key={expense.id} className="border-l-4 border-[#FF6B6B] pl-4 py-2">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <p className="font-bold font-[Archivo]">£{expense.amount.toFixed(2)} - {expense.description}</p>
                        <Badge variant="error" className="mt-2">{expense.category}</Badge>
                      </div>
                    </div>
                    {expense.ai_warning && (
                      <p className="text-sm text-[#FF6B6B] font-[Inter] italic">{expense.ai_warning}</p>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Recent Expenses */}
          <Card>
            <h2 className="text-2xl font-bold mb-4 font-[Archivo]">Recent Expenses</h2>
            {loading ? (
              <p className="text-[#666666]">Loading...</p>
            ) : expenses.length === 0 ? (
              <p className="text-[#666666]">No expenses logged yet.</p>
            ) : (
              <div className="space-y-2">
                {expenses.map((expense: any) => (
                  <div key={expense.id} className="flex justify-between items-center border-b-2 border-black pb-2">
                    <div>
                      <p className="font-bold font-[Archivo]">{expense.description}</p>
                      <p className="text-sm text-[#666666]">{expense.category}</p>
                    </div>
                    <p className="font-bold font-[Archivo]">£{expense.amount.toFixed(2)}</p>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </motion.div>
    </div>
  )
}

export default Finance
