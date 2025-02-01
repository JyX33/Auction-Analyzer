import { useAtom } from 'jotai'
import { useState } from 'react'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { apiClient, type ItemBase } from '@/lib/api'
import { selectedRealmIdsAtom } from '@/lib/store'
import { LoadingSpinner } from '../ui/loading-spinner'

export function ItemSelect() {
  const [selectedRealms] = useAtom(selectedRealmIdsAtom)
  const [searchQuery, setSearchQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [searchResults, setSearchResults] = useState<ItemBase[]>([])
  const [addingItem, setAddingItem] = useState<number | null>(null)

  const handleSearch = async () => {
    setIsLoading(true)
    try {
      const response = await apiClient.listItems({ 
        page: 1,
        page_size: 10,
        item_class_name: searchQuery 
      })
      setSearchResults(response.items)
    } catch (error) {
      alert(`Failed to search items: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsLoading(false)
    }
  }

  const handleAddToRealm = async (itemId: number) => {
    if (selectedRealms.length === 0) return
    setAddingItem(itemId)
    try {
      await Promise.all(selectedRealms.map(realmId => 
        apiClient.getRealmPrices(realmId, [itemId])
      ))
      alert('Item added to selected realms!')
      setSearchResults([])
    } catch (error) {
      alert(`Failed to add item: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setAddingItem(null)
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

      {isLoading ? (
        <div className="flex justify-center"><LoadingSpinner /></div>
      ) : (
        searchResults.length > 0 && (
          <ul className="border rounded-md">
            {searchResults.map((item) => (
              <li key={item.item_id} className="py-2 px-4 border-b last:border-b-0 flex justify-between items-center">
                <span>{item.item_name}</span>
                <Button
                  onClick={() => handleAddToRealm(item.item_id)}
                  disabled={addingItem === item.item_id}
                >
                  {addingItem === item.item_id ? "Adding..." : "Add to Realm"}
                </Button>
              </li>
            ))}
          </ul>
        )
      )}
    </div>
  )
}
