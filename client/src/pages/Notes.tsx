import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card } from '@/components/Card'
import { Button } from '@/components/Button'
import { Input } from '@/components/Input'
import { Badge } from '@/components/Badge'

export function Notes() {
  const [notes, setNotes] = useState([])
  const [newNote, setNewNote] = useState({ title: '', content: '' })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(false)
  }, [])

  const handleCreateNote = async () => {
    if (!newNote.title.trim()) return
    setNewNote({ title: '', content: '' })
  }

  return (
    <div className="min-h-screen bg-[#F4F4F0] p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold mb-8 font-[Archivo]">Notes</h1>

          <Card className="mb-8">
            <h2 className="text-2xl font-bold mb-4 font-[Archivo]">New Note</h2>
            <Input
              label="Title"
              placeholder="Note title..."
              value={newNote.title}
              onChange={(e) => setNewNote({ ...newNote, title: e.target.value })}
            />
            <textarea
              className="w-full border-2 border-black p-3 mb-4 font-[Inter] focus:outline-none focus:shadow-[2px_2px_0px_rgba(0,0,0,1)]"
              rows={6}
              placeholder="Write your note here..."
              value={newNote.content}
              onChange={(e) => setNewNote({ ...newNote, content: e.target.value })}
            />
            <Button variant="primary" onClick={handleCreateNote}>
              Create Note
            </Button>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {loading ? (
              <p className="text-[#666666]">Loading notes...</p>
            ) : notes.length === 0 ? (
              <p className="text-[#666666]">No notes yet. Create one to get started!</p>
            ) : (
              notes.map((note: any) => (
                <Card key={note.id}>
                  <h3 className="text-lg font-bold mb-2 font-[Archivo]">{note.title}</h3>
                  <p className="text-sm text-[#666666] mb-3 line-clamp-3 font-[Inter]">{note.content}</p>
                  <div className="flex gap-2 flex-wrap">
                    {note.tags?.map((tag: string) => (
                      <Badge key={tag} variant="accent">{tag}</Badge>
                    ))}
                  </div>
                </Card>
              ))
            )}
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default Notes
