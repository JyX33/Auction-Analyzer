const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface ItemBase {
  item_id: number;
  item_name: string;
  item_class_name: string;
  item_subclass_name: string;
}

export interface ItemDetail extends ItemBase {
  item_class_id: number;
  item_subclass_id: number;
  display_subclass_name?: string;
  groups: string[];
}

export interface ItemListResponse {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  items: ItemBase[];
}

export interface ItemClass {
  item_class_id: number;
  item_class_name: string;
}

export interface ItemSubclass {
  item_subclass_id: number;
  item_subclass_name: string;
}

export interface GroupBase {
  group_id: number;
  group_name: string;
}

export interface GroupDetail extends GroupBase {
  items: ItemBase[];
}

export interface RealmData {
  id: number;
  name: string;
  language: string;
  population_type: 'Full' | 'High' | 'Medium' | 'Low';
  item_count: number;
  last_updated: string;
}

export interface ItemPriceDetails {
  item_id: number;
  item_name: string;
  lowest_price: number;
  highest_price: number;
  quantity: number;
  average_lowest_five: number;
  rating: number;
}

export interface PriceMetrics {
  average_price: number;
  price_trend: number;
  item_details: {
    item_id: number;
    current_price: number;
    historical_low: number;
    historical_high: number;
  }[];
}

export interface RealmComparison {
  realm_id: number;
  total_value: number;
  value_per_item: number;
  rating: number;
  items: ItemPriceDetails[];
}

class APIClient {
  private async fetchWithError<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || 'An error occurred while fetching data');
    }

    return response.json();
  }

  // Item endpoints
  async getItemById(itemId: number): Promise<ItemDetail> {
    return this.fetchWithError<ItemDetail>(`/items/${itemId}`);
  }

  async listItems(params: {
    page?: number;
    page_size?: number;
    item_class_name?: string;
    item_subclass_name?: string;
  } = {}): Promise<ItemListResponse> {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.page_size) searchParams.append('page_size', params.page_size.toString());
    if (params.item_class_name) searchParams.append('item_class_name', params.item_class_name);
    if (params.item_subclass_name) searchParams.append('item_subclass_name', params.item_subclass_name);

    return this.fetchWithError<ItemListResponse>(`/items?${searchParams.toString()}`);
  }

  // Item Classes endpoints
  async listItemClasses(): Promise<ItemClass[]> {
    return this.fetchWithError<ItemClass[]>('/item-classes');
  }

  async listSubclassesForClass(classId: number): Promise<ItemSubclass[]> {
    return this.fetchWithError<ItemSubclass[]>(`/item-classes/${classId}/subclasses`);
  }

  // Groups endpoints
  async listGroups(): Promise<GroupBase[]> {
    return this.fetchWithError<GroupBase[]>('/groups');
  }

  async getGroupById(groupId: number): Promise<GroupDetail> {
    return this.fetchWithError<GroupDetail>(`/groups/${groupId}`);
  }

  async listItemsInGroup(groupId: number): Promise<ItemBase[]> {
    return this.fetchWithError<ItemBase[]>(`/groups/${groupId}/items`);
  }

  // Realm endpoints
  async getRealms(realm_category?: string): Promise<RealmData[]> {
    const params = new URLSearchParams();
    if (realm_category) params.append('realm_category', realm_category);
    return this.fetchWithError<RealmData[]>(`/realms${params.toString() ? `?${params.toString()}` : ''}`);
  }

  async getRealmPrices(realmId: number, itemIds: number[], timeRange: string = '7d'): Promise<PriceMetrics> {
    const params = new URLSearchParams({
      items: itemIds.join(','),
      time_range: timeRange,
    });

    return this.fetchWithError<PriceMetrics>(`/prices/${realmId}?${params.toString()}`);
  }

  async compareRealms(realmIds: number[], itemIds: number[]): Promise<RealmComparison[]> {
    return this.fetchWithError<RealmComparison[]>('/comparison', {
      method: 'POST',
      body: JSON.stringify({ realms: realmIds, items: itemIds }),
    });
  }
}

export const apiClient = new APIClient();
