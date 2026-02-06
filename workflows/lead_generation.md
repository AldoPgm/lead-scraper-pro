# Lead Generation Workflow

**Objective**: Extract lead information (Name, Title, Company) from public LinkedIn profiles and generate email patterns.

## Inputs
- **Target**: List of LinkedIn public profile URLs.
- **Output File**: `.tmp/leads.csv`

## Steps
1. **Prepare URLs**: ensure you have the target URLs ready.
2. **Run Scraper**:
   - Execute the extraction tool:
     ```bash
     python tools/scrape_leads.py --urls "https://www.linkedin.com/in/example-user"
     ```
   - *Note*: You can provide multiple URLs separated by space or input a file path if the tool supports it.
3. **Verify Output**:
   - Check `.tmp/leads.csv` for the extracted data.
   - Verify pattern generation (e.g., `firstname.lastname@company.com`).
4. **Error Handling**:
   - If the scraper returns 403/999 (LinkedIn anti-bot), the tool may switch to "Demo Mode" using mock data to demonstrate the parsing logic.
   - Check console logs for validation errors.

## Maintenance
- Update `tools/scrape_leads.py` if HTML structure changes.
- Rotate IPs or add delays if rate limits are encountered.
