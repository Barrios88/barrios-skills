## Requirements for creating and editing financial models or investment banking

Rule: Follow these additional guidelines unless they conflict with user's specifications, request or skill.

### Additional requirements for financial models
- Make all zeros formatted as "-"
- Negative numbers should be red and in parentheses; (500), not -500. In Excel this might be "$#,##0.00_);[Red] ($#,##0.00)"
- For multiples, format as 5.2x
- Always specify units in headers; "Gross Income ($mm)"
- All added raw inputs should have their sources cited in the appropriate cell comment
- Assumptions / data inputs (growth rates, multiples, margins, etc.) should be in separate cells or sheets.
- Financial return formulas must be guarded until the cash-flow sign pattern and minimum data requirements are valid. If IRR/XIRR cannot be valid for an illustrative template, use a documented estimate metric such as cash-on-cash return, NPV at the stated discount rate, or a guarded RATE approximation instead of surfacing `#NUM!`.

#### Finance-specific color conventions:
When building new financial models where no user-provided spreadsheet or formatting instructions override these conventions, use:
- **Blue text (RGB: 0,0,255)**: Hardcoded inputs, and numbers users will change for scenarios
- **Black text (RGB: 0,0,0)**: ALL formulas and calculations
- **Green text (RGB: 0,128,0)**: Links pulling from other worksheets within same workbook
- **Red text (RGB: 255,0,0)**: External links to other files
- **Yellow background (RGB: 255,255,0)**: Key assumptions needing attention or cells that need to be updated

### Additional requirements for investment banking
If the spreadsheet is related to investment banking (LBO, DCF, 3-statement, valuation model, or similar):
- Total calculations should sum a range of cells directly above them.
- Hide gridlines. Add horizontal borders above total calculations, spanning the full range of relevant columns including any label column(s).
- Section headers applying to multiple columns and rows should be left-justified, filled black or dark blue with white text, and should be a merged cell spanning the horizontal range of cells to which the header applies.
- Column labels (such as dates) for numeric data should be right-aligned, as should be the data.
- Row labels associated with numeric data or calculations (for example, "Fintech and Business Cost of Sales") should be left-justified. Labels for submetrics immediately below (for example, "% growth") should be left-aligned but indented.
