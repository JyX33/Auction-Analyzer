# Project Roadmap - Blizzard Item Data Extractor

## Project Goals

- [x] Implement robust data extraction from Blizzard API
- [x] Create efficient local data storage system
- [ ] Develop REST API for data access
- [ ] Enable user-defined item grouping functionality

## Features

### Phase 1: Data Extraction (Current)

- [x] Set up project structure and documentation
- [x] Implement concurrent Blizzard API requests
- [x] Handle rate limiting and error scenarios
- [x] Generate detailed extraction reports
- [x] Store item data in SQLite database

### Phase 2: Database & Data Management

- [x] Implement database schema
- [x] Create database migration system
- [x] Set up data validation
- [x] Implement data update mechanisms
- [ ] Create backup and restore functionality

### Phase 3: REST API Development

- [ ] Design and implement API endpoints
- [ ] Add filtering and pagination
- [ ] Implement error handling
- [ ] Add API documentation (Swagger UI)
- [ ] Set up API testing

### Phase 4: Item Groups Feature

- [ ] Implement group creation/management
- [ ] Add items to groups functionality
- [ ] Create group query endpoints
- [ ] Add group data validation

## Completion Criteria

### Data Extraction

- Successfully extract data for large item lists
- Handle rate limits gracefully
- Generate comprehensive extraction reports
- Store data accurately in SQLite
- Efficient batch processing with existing item filtering
- Automatic skipping of duplicate realms/items
- Inter-batch delays for API rate management

### Database Management

- Efficient data storage and retrieval
- Data integrity maintenance
- Successful backup/restore operations
- Optimized batch operations for item updates
- Duplicate prevention mechanisms

### API Functionality

- All endpoints working as documented
- Proper error handling
- Comprehensive API documentation
- Successful API tests

### Item Groups

- Create and manage groups
- Add/remove items from groups
- Query items by group
- Validate group operations

## Completed Tasks

*(This section will be updated as tasks are completed)*

- Phase 1: Data Extraction completed
- Phase 2: Data validation and update mechanisms implemented
  - Set-based item filtering
  - Connected realm duplicate prevention
  - Batch processing optimization
  - Rate limit management with delays

## Future Considerations

- Potential migration to PostgreSQL for scaling
- Authentication system for API
- Enhanced group management features
- Performance optimization for large datasets
- API usage analytics
- Periodic extraction scheduling
- Database index optimization for ID queries
