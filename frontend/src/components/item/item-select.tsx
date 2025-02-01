import { useAtom } from 'jotai'
import { useState } from 'react'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { api } from '@/lib/api'
import { selectedGroupAtom } from '@/lib/store'

export function ItemSelect() {
  const [selectedGroup, setSelectedGroup] = useAtom(selectedGroupAtom)
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = async () => {
    setIsLoading(true)
    try {
      const response = await api.get('/items', {
        params: { search: searchQuery }
      })
      // TODO: Handle search results
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddToGroup = async (itemId: number) => {
    if (!selectedGroup) return
    try {
      await api.post(`/groups/${selectedGroup}/items`, {
        item_ids: [itemId]
      })
      // TODO: Handle success
    } catch (error) {
      // TODO: Handle error
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          placeholder="Search items..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <Button onClick={handleSearch} disabled={isLoading}>
          Search
        </Button>
      </div>

      {/* TODO: Render search results */}
    </div>
  )
}
