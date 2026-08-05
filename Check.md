I have two Excel files: one is a source file (referred to as "example") containing data to be transferred, and the other is a destination file with a sheet titled "going" that has an existing formatting structure I need preserved. Both files are attached.

Write a Python script (using `openpyxl`) that copies all data from the source Excel file into the "going" sheet of the destination file, following these rules:

- The "going" sheet has columns B, C, and D merged into a single cell per row for the URL field. When inserting URL data from the source file, write it into this merged cell structure, re-creating the merge for each new row so the format matches existing rows.
- The "going" sheet has a footer positioned near the bottom of the used area. Before inserting new rows, detect the footer's current row position, then insert enough new rows above it to fit all incoming data, and move the footer down so it stays below all newly added data — do not leave gaps or overlap the footer with data.
- Preserve all existing formatting in the destination file: fonts, fills, borders, column widths, merged cell styles, and any other text or cells outside the grid area being populated must remain untouched.
- Only populate the grid/data area with the incoming information — do not alter headers, labels, or any other structural elements of the "going" sheet.
- Map the source columns to the corresponding destination columns based on matching header names or logical correspondence (e.g., the merged B:D cell corresponds to the source file's URL column). If mapping is ambiguous, infer the most sensible correspondence based on column headers and content.

Output the complete script along with a brief explanation of how it detects the footer, handles the merged cells, and inserts rows without disrupting existing formatting.
