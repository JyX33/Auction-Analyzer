# Frontend Architecture Documentation

## Overview

The frontend application for realm ranking analysis is built using modern web technologies with a focus on performance, type safety, and maintainable code structure.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/             # Layout components
│   │   ├── realm/             # Realm-specific components
│   │   ├── price/             # Price analysis components
│   │   └── ui/                # Reusable UI components
│   ├── lib/
│   │   ├── api/               # API client and types
│   │   ├── store/             # Jotai atoms and derived state
│   │   └── utils/             # Helper functions
│   ├── types/                 # TypeScript type definitions
│   └── pages/                 # Route components
└── tests/                     # Test files
```

## Key Components

### Realm Selection
- RealmSelector: Filterable dropdown for realm selection
- RealmList: Display list of available realms with key metrics
- RealmDetails: Show detailed realm information

### Price Analysis
- PriceChart: Recharts-based visualization
- PriceMetrics: Key price statistics display
- TrendIndicator: Visual indicator of price trends

### Data Management
- API Integration using Fetch API
- Jotai atoms for state management
- Type-safe API response handling

## State Management

### Jotai Store Structure
```typescript
// Base atoms
const selectedRealmAtom = atom<number | null>(null);
const itemFiltersAtom = atom<ItemFilter[]>([]);

// Derived atoms
const realmPricesAtom = atom(
  (get) => {
    const realmId = get(selectedRealmAtom);
    // ... fetch and compute price data
  }
);
```

## Data Flow

1. User Selection
```
User Input -> Jotai State -> API Request -> Update UI
```

2. Price Updates
```
API Polling -> Update Store -> Refresh Charts
```

## Component Communication

- Props for parent-child communication
- Jotai for global state
- Custom hooks for shared logic

## Performance Considerations

- Debounced API calls
- Memoized expensive computations
- Lazy loading of chart components
- Optimistic UI updates

## Testing Strategy

### Unit Tests (Vitest)
- Component rendering
- State management
- Utility functions

### Integration Tests
- API interaction
- User flows
- State updates

## Error Handling

- API error boundaries
- Loading states
- Fallback UI components
- Error reporting

## Accessibility

- ARIA attributes
- Keyboard navigation
- Color contrast compliance
- Screen reader support

## Future Enhancements

- Offline support
- Real-time updates
- Advanced filtering
- Custom dashboards
- Saved preferences

## Development Guidelines

1. Component Creation
   - Use TypeScript for all components
   - Follow shadcn/ui patterns
   - Implement proper error boundaries

2. State Management
   - Keep atoms focused and minimal
   - Use selectors for derived data
   - Document state dependencies

3. Testing
   - Write tests alongside components
   - Focus on user interactions
   - Mock API calls appropriately

4. Performance
   - Monitor bundle size
   - Implement code splitting
   - Profile rendering performance