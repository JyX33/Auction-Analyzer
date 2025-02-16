# Run data extraction
Write-Host "Starting data extraction..." -ForegroundColor Green
python -m src.extractor.scripts.run_extraction
if ($LASTEXITCODE -ne 0) {
    Write-Host "Data extraction failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`nWaiting 5 seconds before populating spell IDs..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Populate spell IDs
Write-Host "Populating spell IDs..." -ForegroundColor Green
python -m src.database.scripts.populate_spell_id
if ($LASTEXITCODE -ne 0) {
    Write-Host "Spell ID population failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`nWaiting 5 seconds before calculating raw craft costs..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Calculate raw craft costs
Write-Host "Calculating raw craft costs..." -ForegroundColor Green
python -m src.database.scripts.populate_raw_craft_cost
if ($LASTEXITCODE -ne 0) {
    Write-Host "Raw craft cost calculation failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "`nAll data updates completed successfully!" -ForegroundColor Green