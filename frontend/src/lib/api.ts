const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1';

export interface RealmData {
  id: number;
  name: string;
  region: string;
  item_count: number;
  last_updated: string;
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
}

class APIClient {
  private async fetchWithError(endpoint: string, options: RequestInit = {}) {
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

  async getRealms(region?: string): Promise<RealmData[]> {
    const params = new URLSearchParams();
    if (region) params.append('region', region);
    
    return this.fetchWithError(`/realms${params.toString() ? `?${params.toString()}` : ''}`);
  }

  async getRealmPrices(realmId: number, itemIds: number[], timeRange: string = '7d'): Promise<PriceMetrics> {
    const params = new URLSearchParams({
      items: itemIds.join(','),
      time_range: timeRange,
    });

    return this.fetchWithError(`/prices/${realmId}?${params.toString()}`);
  }

  async compareRealms(realmIds: number[], itemIds: number[]): Promise<RealmComparison[]> {
    return this.fetchWithError('/comparison', {
      method: 'POST',
      body: JSON.stringify({ realms: realmIds, items: itemIds }),
    });
  }
}

export const apiClient = new APIClient();