# Coding packet: pairs of pages from one brief where at least three of four raters moved two or more points on one item, in the same direction.
# The two pages of a pair are called P and Q. Which builder made which is not shown and is not to be guessed.
# For each cell: the item, each rater's two ratings (P, Q) and the two evidence clauses; then, once per pair, every other item's clauses on both pages for context.

## Cell compare·A · item b4
- astra-medium: b4 P=2 Q=0
    P: Halloway has a checked radio, SELECTED label and matching Selected supplier summary.
    Q: The award bar says No supplier selected and shows no recorded pick.
- astra-high: b4 P=2 Q=0
    P: Halloway has a checked radio, a SELECTED label and a matching Selected supplier award summary.
    Q: The action bar explicitly says No supplier selected and shows no recorded award.
- claude-opus: b4 P=2 Q=1
    P: award panel names the selected supplier with modelled cost and mandatory-requirement status, the column head shows 'SELECTED', and the footer states the award is held on the tender file
    Q: the bar only reports 'No supplier selected'; the button is greyed and nothing shows an award having been recorded
- claude-sonnet: b4 P=2 Q=0
    P: the Award panel shows 'SELECTED SUPPLIER: Halloway Tyre Group' with a modelled cost, evaluation note and checked radio marked 'SELECTED'
    Q: the footer bar still reads 'No supplier selected. Choose a column in the comparison to record an award.' on the full page
  Context for compare·A: every other clause on both pages, per rater (rating in parentheses):
    astra-medium b1: P(2) Three aligned supplier columns share tender requirements and quantitative scales.  ||  Q(2) A single criterion-by-criterion table aligns all three suppliers.
    astra-medium b2: P(2) Price per axle, lead time, casing warranty and on-site fitting each have three entries.  ||  Q(2) The first four table rows explicitly cover every requested criterion for each supplier.
    astra-medium b3: P(2) Supplier radio buttons and a named award button make selection explicit.  ||  Q(2) Supplier header selectors feed a Record an award control.
    astra-medium b4: P(2) Halloway has a checked radio, SELECTED label and matching Selected supplier summary.  ||  Q(0) The award bar says No supplier selected and shows no recorded pick.
    astra-medium c1: P(0) Cell text and warning labels wrap within their boundaries.  ||  Q(1) The fixed award bar obscures the middle supplier chart in the full-page capture.
    astra-medium c2: P(0) Main values and supporting labels are legible at native size.  ||  Q(0) Table text and chart labels are readable at native resolution.
    astra-medium c3: P(0) The matrix, model and supplier references are fully populated.  ||  Q(0) The missing rolling-resistance value is explicitly identified as supplier data not supplied.
    astra-medium c4: P(0) Repeated cells and quantitative rules follow consistent alignment.  ||  Q(0) Supplier rows and table columns use consistent spacing.
    astra-medium c5: P(0) The sheet and award sidebar fit within the viewport.  ||  Q(0) Panels and table fit the viewport width.
    astra-medium d1: P(6) Only minor density and typography refinement is needed around the narrow supplier columns.  ||  Q(5) Fix the award bar covering chart content and clarify the recorded-selection state.
    astra-high b1: P(2) Halloway, Pentlow and Marrick occupy shared columns across the comparison matrix.  ||  Q(2) One ruled matrix aligns Penmark, Draymoor and Halgarth against identical rows.
    astra-high b2: P(2) Each column includes fitted axle price, planned lead time, casing warranty and on-site fitting terms.  ||  Q(2) The first four matrix criteria show axle prices, lead times, warranties and fitting for all three.
    astra-high b3: P(2) Supplier radio controls and the Award to Halloway Tyre Group button make the choice explicit.  ||  Q(2) Each supplier heading has a selection control, with a separate Record an award button.
    astra-high b4: P(2) Halloway has a checked radio, a SELECTED label and a matching Selected supplier award summary.  ||  Q(0) The action bar explicitly says No supplier selected and shows no recorded award.
    astra-high c1: P(0) The comparison cells, warnings and sidebar contents remain inside their containers.  ||  Q(0) No content is visibly cut off by its own container.
    astra-high c2: P(0) Table text and numerical labels are readable at native capture size.  ||  Q(0) The native-size table values and supporting labels remain readable.
    astra-high c3: P(0) The comparison, model and supplier references all contain finished information.  ||  Q(0) The chart, comparison and trade-off sections contain finished content.
    astra-high c4: P(0) Supplier cells, quantitative scales and reference columns follow consistent alignment.  ||  Q(0) Like table cells and supplier summaries use consistent spacing and alignment.
    astra-high c5: P(0) The comparison matrix and award sidebar fit side by side within the viewport.  ||  Q(0) The sheet and its three supplier columns fit within the viewport.
    astra-high d1: P(6) Only minor copy tightening is needed; the comparison, visible selection and award action already form a coherent decision flow.  ||  Q(4) Move the four required criteria and selection ahead of the lengthy cost explanation and secondary criteria.
    claude-opus b1: P(2) one matrix of Halloway, Pentlow and Marrick against the tender requirement, each row on a shared scale rule  ||  Q(2) fourteen-criterion table with Penmark, Draymoor and Halgarth as columns, plus a one-basis bar comparison above it
    claude-opus b2: P(2) 'Price per axle, fitted', 'Lead time, planned replacement', 'Casing warranty' and 'Fitting included in the price' rows all filled per supplier  ||  Q(2) 'Price per axle', 'Lead time', 'Warranty' and 'On-site fitting' are the first four rows, filled for all three suppliers
    claude-opus b3: P(2) radio in each column head plus an 'Award to Halloway Tyre Group' button in the award panel  ||  Q(2) a checkbox in each supplier column head feeding a 'Record an award' button in the action bar
    claude-opus b4: P(2) award panel names the selected supplier with modelled cost and mandatory-requirement status, the column head shows 'SELECTED', and the footer states the award is held on the tender file  ||  Q(1) the bar only reports 'No supplier selected'; the button is greyed and nothing shows an award having been recorded
    claude-opus c1: P(0) cells wrap; scale rules sit clear of their rows  ||  Q(1) the fixed action bar paints over the Draymoor bar row in the full-page capture, hiding that row's chart
    claude-opus c2: P(0) smallest mono captions on the scale rules remain readable at native size  ||  Q(0) mono values and grey criterion sub-labels read clearly at native size
    claude-opus c3: P(0) all cells quoted; the model-basis panel carries real inputs  ||  Q(0) every cell quoted; 'NOT SUPPLIED' is a stated finding, not a placeholder
    claude-opus c4: P(0) criterion column, three supplier columns and the scale rules repeat identically down the sheet  ||  Q(0) row heights, column widths and the 'Show terms' links repeat consistently
    claude-opus c5: P(0) sheet is centred inside the viewport width  ||  Q(0) content stays inside the 1440 frame
    claude-opus d1: P(6) delivers as a rigorous evaluation record; only the long blank right column beside the lower matrix would want tidying  ||  Q(5) structure is sound but the action bar overlaps content and a checkbox is the wrong control for one exclusive pick
    claude-sonnet b1: P(2) Halloway, Pentlow and Marrick sit as three columns in one comparison table with a shared rank toggle above it  ||  Q(2) one criterion-by-criterion table lists Penmark, Draymoor and Halgarth as three columns against the same fourteen rows
    claude-sonnet b2: P(2) price per axle, lead time, casing warranty and on-site fitting each appear as labelled rows with values for all three suppliers  ||  Q(2) price per axle, lead time, warranty and on-site fitting are each a labelled row with a value in all three columns
    claude-sonnet b3: P(2) a radio selector sits under each supplier card and an 'Award to Halloway Tyre Group' button sits in the Award panel  ||  Q(2) a checkbox sits in each supplier's column header and a 'Record an award' button sits in the footer bar
    claude-sonnet b4: P(2) the Award panel shows 'SELECTED SUPPLIER: Halloway Tyre Group' with a modelled cost, evaluation note and checked radio marked 'SELECTED'  ||  Q(0) the footer bar still reads 'No supplier selected. Choose a column in the comparison to record an award.' on the full page
    claude-sonnet c1: P(0) no capture shows clipped content  ||  Q(0) no capture shows content cut by its container
    claude-sonnet c2: P(0) dense table and dot-plot scale labels remain readable at this size  ||  Q(0) body and label text hold a legible size throughout
    claude-sonnet c3: P(0) no placeholder or broken region appears  ||  Q(0) no empty image slot or placeholder copy appears
    claude-sonnet c4: P(0) row and column spacing stay consistent across the long table  ||  Q(0) row height and column alignment are consistent across the whole table
    claude-sonnet c5: P(0) full page stays within the 1440 frame  ||  Q(0) the full-page capture matches the 1440 viewport with no sideways scroll
    claude-sonnet d1: P(7) the page carries the brief through to its stated endpoint with a supplier actually selected and recorded, and the surrounding sections are clean and consistent  ||  Q(5) structure and copy are sound but the page never shows an award actually made, and the palette is nearly all grayscale with a single accent

## Cell fleet·A · item d1
- astra-medium: d1 P=3 Q=5
    P: Widen or reorganize the schedule and repair table overflow
    Q: Repair panel clipping and polish the muddy neutral palette
- astra-high: d1 P=3 Q=5
    P: Re-form the schedule and overflowing defect table and rebalance the long parts column.
    Q: Adjust schedule and list sizing to remove clipped edges; the information hierarchy is deliverable.
- claude-opus: d1 P=3 Q=5
    P: The defect table has to be re-formed to fit and the empty bottom-left half re-composed, beyond cosmetic work
    Q: Cohesive and complete; the schedule region has to be re-fitted so its right end stops clipping
- claude-sonnet: d1 P=5 Q=6
    P: Content is complete and well organized, but the mismatched column heights leave a large stray gap that needs a structural fix (fill, cap, or reflow).
    Q: All captures show complete, aligned content with no clipping or overflow; deliverable as is.
  Context for fleet·A: every other clause on both pages, per rater (rating in parentheses):
    astra-medium b1: P(2) Fleet number and registration accompany each defect in the table  ||  Q(2) Open-defect table identifies fleet numbers and registrations
    astra-medium b2: P(2) Decision queue labels overdue inspections and gives days over  ||  Q(2) Recall alert and inspection rows explicitly distinguish overdue and expired items
    astra-medium b3: P(2) Each part has a status and delivery date or explicit missing-date statement  ||  Q(2) Parts list provides due dates or explicit authorization and feed status
    astra-medium b4: P(1) Five-bay timeline exists but many job labels are reduced to fragments  ||  Q(2) Ten labeled lanes show jobs against hours with a current-time line
    astra-medium c1: P(1) Inspection column and bottom defect row are visibly cut off  ||  Q(1) Open-defect panel cuts through its last visible row and schedule clips its right edge
    astra-medium c2: P(1) Tiny timeline labels make several jobs difficult to read  ||  Q(0) Main table and schedule text remain readable at native size
    astra-medium c3: P(0) Large lower-left whitespace is unoccupied layout rather than a placeholder  ||  Q(0) Panels contain real operational entries rather than placeholders
    astra-medium c4: P(0) Like rows and parts entries align consistently  ||  Q(0) Repeated rows and status labels align consistently
    astra-medium c5: P(1) Full capture is wider than the 1440-pixel viewport  ||  Q(0) Main panels and sidebar fit within the viewport
    astra-medium d1: P(3) Widen or reorganize the schedule and repair table overflow  ||  Q(5) Repair panel clipping and polish the muddy neutral palette
    astra-high b1: P(2) The defect table identifies each bus by fleet number and registration beside its reported fault.  ||  Q(2) Open-defect rows name fleet number, registration, fault, category and next step.
    astra-high b2: P(2) Overdue inspection rows lead the decision queue with days-over labels and deadline markers.  ||  Q(2) The red recall panel and explicit Overdue or Expired inspection text separate late records.
    astra-high b3: P(2) Each parts entry has a delivery date or a clear Late, No Date or On Order state.  ||  Q(2) Parts rows include due dates or explicit Awaiting Authority and Delivery Date Unavailable states.
    astra-high b4: P(1) Bays and hours are present but many narrow job blocks hide the vehicle or task behind ellipses.  ||  Q(2) Ten bay lanes place vehicle jobs against hours with status fills and printed time ranges.
    astra-high c1: P(1) The defect table cuts off the inspection column and ends in a partial row.  ||  Q(1) The schedule cuts off its late-day right edge and the defect list ends in a partial row.
    astra-high c2: P(1) Compressed schedule labels are too small to read comfortably at native size.  ||  Q(0) Main records and secondary copy remain readable at native resolution.
    astra-high c3: P(0) The large lower-left gap is unused layout space rather than an empty placeholder component.  ||  Q(0) The board is populated throughout with specific operational records.
    astra-high c4: P(0) Like rows and parts entries have consistent internal spacing.  ||  Q(0) Table columns, badges and section headers maintain consistent alignment.
    astra-high c5: P(1) The full-page capture extends beyond the 1440-pixel viewport width.  ||  Q(0) The page itself fits the viewport despite internal schedule clipping.
    astra-high d1: P(3) Re-form the schedule and overflowing defect table and rebalance the long parts column.  ||  Q(5) Adjust schedule and list sizing to remove clipped edges; the information hierarchy is deliverable.
    claude-opus b1: P(2) 'Open defects by vehicle' table sorted by fleet number with type, depot, defect as reported, system, reporter and condition  ||  Q(2) 'Open defects' table lists fleet number, registration, defect, category, age, next step and vehicle state
    claude-opus b2: P(2) 'Needs a decision this shift' queue puts OVERDUE / DUE TODAY chips and a deadline bar with '3 d over' at the top of the page  ||  Q(2) Inspections panel opens with 'Overdue 5 days', 'Overdue 1 day', 'Expired 3 days' plus RECALL NOW chips and a recall banner at the top
    claude-opus b3: P(2) Parts panel gives each line a state chip (DUE TODAY, LATE, NO DATE, AT GOODS-IN, ON ORDER) plus 'Expected 5 Sep' or 'Promised 31 Aug, 3 days late'  ||  Q(2) Every parts line gives supplier, ordered date and 'Due Today 11:00' / 'Due 09 Sep' or an explicit 'Not ordered - awaiting authority'
    claude-opus b4: P(1) Bays 1-5 across 06:00-20:00 with a now-line, but most blocks are squeezed to 'BOOK...', 'DONE ...', 'Free 0...' so the day is hard to read off  ||  Q(2) 'The workshop's day': ten named bays, 05:00-19:00 axis, now-line at 09:42, job bars with times and a state legend
    claude-opus c1: P(1) The defects table's last column is cut by the page edge - only 'INSPECTI' and '2 Sep (' show  ||  Q(1) The gantt's right end is cut by its container - the 'Round / Evening wash' block and the Bay 6 and Bodyshop bars run past the edge; the defects table also cuts the '2242' row in half
    claude-opus c2: P(1) Gantt block labels are reduced to a few tiny characters ('DO...', 'BOOK...', 'IN PROGRESS' overprinted by the now-line)  ||  Q(0) Body copy and mono labels stay comfortably readable
    claude-opus c3: P(0) All panels hold real records  ||  Q(0) No placeholder or unfilled region
    claude-opus c4: P(1) The half-width schedule leaves the whole bottom-left of the page empty beside the parts column, and the gantt's blocks vary in inset between bays  ||  Q(0) Panels, table rows and badge sizes are consistent throughout
    claude-opus c5: P(1) The rendered page is wider than the 1440 viewport, carrying the inspection column off-screen  ||  Q(0) The page itself fits the viewport; the overflow is inside the schedule container
    claude-opus d1: P(3) The defect table has to be re-formed to fit and the empty bottom-left half re-composed, beyond cosmetic work  ||  Q(5) Cohesive and complete; the schedule region has to be re-fitted so its right end stops clipping
    claude-sonnet b1: P(2) Open defects by vehicle table lists type, depot, defect, system, reported, condition and next inspection per vehicle.  ||  Q(2) Open defects table lists fleet, registration, defect, category, age, next step and vehicle status per row.
    claude-sonnet b2: P(2) The decision queue tags each item OVERDUE/DUE TODAY/OFF ROAD/FALLS DUE with a deadline-bar visualization, separate from open defects.  ||  Q(2) Inspections table marks overdue rows in red text with RECALL NOW/OFF ROAD tags versus due-soon rows with green IN WORKSHOP/AWAITING SUPPLIER tags.
    claude-sonnet b3: P(2) Parts on order list shows a due/expected date and a status tag (Due today, Late, No date, At goods-in, On order) per part.  ||  Q(2) Parts on order list shows a due date and status per line (Due today, Delivery date unavailable + Retry, plus an OFF ROAD tag naming the vehicle it holds).
    claude-sonnet b4: P(2) The workshop's day grid shows 5 bays 06:00–20:00 with in-progress/done/held/booked blocks and a now-marker.  ||  Q(2) The workshop's day grid shows 10 bays 05:00–21:00 with named jobs, times and a five-state legend.
    claude-sonnet c1: P(0) none seen  ||  Q(0) none seen
    claude-sonnet c2: P(0) none seen  ||  Q(0) none seen
    claude-sonnet c3: P(0) none seen  ||  Q(0) none seen
    claude-sonnet c4: P(1) The left column (workshop's day, 5 bays) ends roughly 500px above where the right column (parts on order) ends, leaving a large unbalanced empty gap between the two panels.  ||  Q(0) none seen
    claude-sonnet c5: P(0) none seen  ||  Q(0) none seen
    claude-sonnet d1: P(5) Content is complete and well organized, but the mismatched column heights leave a large stray gap that needs a structural fix (fill, cap, or reflow).  ||  Q(6) All captures show complete, aligned content with no clipping or overflow; deliverable as is.

## Cell pharmacy·A · item d1
- astra-medium: d1 P=3 Q=7
    P: Add a dedicated expiring-lot set and repair table clipping
    Q: Complete readable task-oriented console needs no visible repair
- astra-high: d1 P=3 Q=7
    P: Add a dedicated expiring-lot region and repair stock and count-table clipping.
    Q: The complete, readable ledgers and prioritized shift actions are ready to deliver.
- claude-opus: d1 P=4 Q=6
    P: expiring lots need forming into their own region, and the two clipped tables and blank ledger rows fixed alongside
    Q: all four asks are covered and honest; the ragged row heights and cramped drug column are spacing work
- claude-sonnet: d1 P=4 Q=7
    P: A clipped status badge needs a technical fix, and expiring lots would need to become its own itemized region.
    Q: All four brief regions are present as full itemized sets with no visible defects across the captures.
  Context for pharmacy·A: every other clause on both pages, per rater (rating in parentheses):
    astra-medium b1: P(2) Stock by item provides on-hand and par columns  ||  Q(2) Stock ledger shows on-hand quantities against par
    astra-medium b2: P(1) Two quarantine lots appear in a mixed handover queue rather than their own set  ||  Q(2) Expiring-lots-and-holds table lists lot IDs, dates and quantities
    astra-medium b3: P(2) Controlled-substance ledger shows expected and counted balances  ||  Q(2) Shift-count sidebar presents system, counted and variance values
    astra-medium b4: P(2) Arriving-this-shift entries each have status badges  ||  Q(2) Each of the five shown orders has a status badge
    astra-medium c1: P(1) Stock row and variance-open badge are cut by their containers  ||  Q(0) No container cutoff is visible across the captures
    astra-medium c2: P(0) Table and queue text are readable at native size  ||  Q(0) Labels and values remain readable at native size
    astra-medium c3: P(0) Blank ledger lines are purposeful entry space, not broken content  ||  Q(0) Every section is populated with purposeful content
    astra-medium c4: P(0) Repeated queue rows and table columns align  ||  Q(0) Repeated ledger rows and sidebar entries align consistently
    astra-medium c5: P(0) Outer layout fits the viewport  ||  Q(0) Main ledger and sidebar fit within the viewport
    astra-medium d1: P(3) Add a dedicated expiring-lot set and repair table clipping  ||  Q(7) Complete readable task-oriented console needs no visible repair
    astra-high b1: P(2) Stock by item includes ON HAND, PAR and cover-days columns.  ||  Q(2) The stock ledger pairs on-hand quantities with par values for every listed drug.
    astra-high b2: P(1) Two expiring-lot alerts are mixed into handover tasks rather than presented as their own set.  ||  Q(2) Expiring lots and holds is a separate table with lot, expiry, quantity and status.
    astra-high b3: P(2) The controlled-substance ledger shows expected, counted and variance values for shift counts.  ||  Q(2) The shift-count region gives system, counted and variance values for controlled drugs.
    astra-high b4: P(2) Arriving this shift assigns each order a status including in transit and awaiting signature.  ||  Q(2) Each displayed pending order has a state such as confirmed, awaiting signature or in transit.
    astra-high c1: P(1) The stock panel cuts through the Insulin glargine row and the count ledger clips Variance open.  ||  Q(0) Complete captures show ledger rows and labels without container clipping.
    astra-high c2: P(0) Native-size body text, numeric values and metadata remain readable.  ||  Q(0) Primary values and supporting annotations are readable at native resolution.
    astra-high c3: P(0) Blank ledger lines are numbered entry space alongside a working-form layout, not placeholder content.  ||  Q(0) Every region is populated with task-specific data and actions.
    astra-high c4: P(0) The repeated handover actions and table columns align consistently.  ||  Q(0) Repeated table rows, count summaries and order entries maintain consistent alignment.
    astra-high c5: P(0) The page stays within the viewport; clipping is local to panels.  ||  Q(0) The sidebar and two content columns fit within the viewport.
    astra-high d1: P(3) Add a dedicated expiring-lot region and repair stock and count-table clipping.  ||  Q(7) The complete, readable ledgers and prioritized shift actions are ready to deliver.
    claude-opus b1: P(2) "Stock by item" table with ON HAND, PAR, a cover-days bar, lots, next expiry and on-order for 26 of 912 items  ||  Q(2) "Stock ledger" with ON HAND / PAR (31 / 120), a fill bar, days of cover and a status chip per line
    claude-opus b2: P(1) no expiry set of its own: only a NEXT EXPIRY column, an "Expiring ≤ 90 days" filter chip and two quarantine cards in the handover queue  ||  Q(2) "Expiring lots and holds" table: seven flagged lots with lot number, expiry, quantity, location, value and EXPIRED / EXPIRES chips
    claude-opus b3: P(2) "Controlled substances" ledger with expected, counted, variance, signer and witness per numbered line, plus a file-a-line form  ||  Q(2) "Controlled substances, shift count" rail with system, counted and variance for each vault position, 8 of 9 counted
    claude-opus b4: P(2) "Arriving this shift" cards each carry In transit, Awaiting signature, ETA unavailable, Booked or Received  ||  Q(2) "Pending orders" cards with CONFIRMED, AWAITING SIGNATURE, NO CONFIRMATION and IN TRANSIT
    claude-opus c1: P(1) the "Variance ope…" chip on ledger line 004 is sliced by the table's right edge and the Insulin glargine row is cut mid-glyph by the stock table container  ||  Q(0) both tables and the right rail close on their own content in the full-page capture
    claude-opus c2: P(0) mono numerals and labels are dark and legible at 1440  ||  Q(0) dark text on white throughout, including the mono NDC and location columns
    claude-opus c3: P(1) ledger rows 011, 012 and 013 are wholly blank ruled rows  ||  Q(0) no placeholder or empty region anywhere on the page
    claude-opus c4: P(0) handover cards, table rows and the arriving rail each hold a steady rhythm  ||  Q(1) stock-ledger rows swing between two and four lines and the drug cell is top-aligned while NDC, location and cover are vertically centred, so like rows do not share a baseline
    claude-opus c5: P(0) the page stays within 1440  ||  Q(0) content stays inside 1440
    claude-opus d1: P(4) expiring lots need forming into their own region, and the two clipped tables and blank ledger rows fixed alongside  ||  Q(6) all four asks are covered and honest; the ragged row heights and cramped drug column are spacing work
    claude-sonnet b1: P(2) 'Stock by item' table lists on hand, par, cover-days and next-expiry per row.  ||  Q(2) Stock ledger table shows on hand/par and days of cover for 13 line items.
    claude-sonnet b2: P(1) Expiring lots surface only as status badges ('Lot expiring') and one quarantine card, not as a dedicated itemized set.  ||  Q(2) 'Expiring lots and holds' is a dedicated table (7 of 63 lots) with expiry, qty, value and status.
    claude-sonnet b3: P(2) 'Controlled substances' section gives a reconciliation summary and a numbered shift ledger with expected/counted/variance.  ||  Q(2) Right column 'Controlled substances, shift count' lists each drug with system/counted/variance and verified time.
    claude-sonnet b4: P(2) 'Arriving this shift' lists each PO with a status pill (In transit, Awaiting signature, ETA unavailable, Booked, Received).  ||  Q(2) 'Pending orders' panel shows each PO with a status pill (Confirmed, Awaiting signature, No confirmation, In transit).
    claude-sonnet c1: P(1) Row 004's status badge reads 'Variance ope', its text cut off by the table cell/panel boundary.  ||  Q(0) No clipped or cut-off content is visible across the four captures.
    claude-sonnet c2: P(0) Text elsewhere is legible.  ||  Q(0) All table and card text reads clearly at native resolution.
    claude-sonnet c3: P(0) No placeholder or broken regions are visible.  ||  Q(0) No placeholder or broken regions are visible.
    claude-sonnet c4: P(0) Spacing between rows and cards is otherwise consistent.  ||  Q(0) Card and table rows keep consistent padding and alignment throughout.
    claude-sonnet c5: P(0) Content stays within the viewport width.  ||  Q(0) Layout fits the 1440 px width with no sideways scroll.
    claude-sonnet d1: P(4) A clipped status badge needs a technical fix, and expiring lots would need to become its own itemized region.  ||  Q(7) All four brief regions are present as full itemized sets with no visible defects across the captures.

## Cell rail·B · item d1
- astra-medium: d1 P=3 Q=6
    P: The constrained roster and clipped operational panels need structural resizing.
    Q: The hierarchy and operational coverage are ready apart from minor label refinement.
- astra-high: d1 P=3 Q=5
    P: Reform the fixed-height panels so the full train roster and supporting information are visible.
    Q: Only minor header truncation and annotation refinements are needed.
- claude-opus: d1 P=4 Q=6
    P: the roster must be re-formed so 11 trains fit the fixed board, and the crews table needs its truncated column back
    Q: only the truncated header string and small chart-label collisions stand between this and delivery
- claude-sonnet: d1 P=3 Q=6
    P: The train roster and crew-relief column are both truncated with no scroll available on this single-viewport page; the panel needs resizing or scrolling added.
    Q: Well-organized and complete; would ship after cosmetic polish (accent color, spacing) rather than structural change.
  Context for rail·B: every other clause on both pages, per rater (rating in parentheses):
    astra-medium b1: P(1) The roster says eleven trains but only four rows and one subdivision graph are visible.  ||  Q(2) The now line identifies all eleven on-subdivision trains with position and state encoding.
    astra-medium b2: P(2) The critical-first exceptions column starts above the routine roster.  ||  Q(2) Three actionable exceptions sit above the corridor graph and routine table.
    astra-medium b3: P(2) Crew rows display on-duty times, remaining durations and outlaw times.  ||  Q(2) The train table pairs on-duty and on-the-law times with remaining hours.
    astra-medium b4: P(2) Track-and-time entries show mileage limits and explicit time ranges.  ||  Q(2) Maintenance rows show geographic limits and explicit in-effect time ranges.
    astra-medium c1: P(1) The crew relief column and lower exception content are cut off by their panels.  ||  Q(0) No accidental container clipping is visible.
    astra-medium c2: P(1) Secondary labels and graph annotations are small and low contrast.  ||  Q(0) Operational text and graph labels remain readable at native size.
    astra-medium c3: P(0) The visible panels are populated rather than placeholders.  ||  Q(0) All regions contain finished operational content.
    astra-medium c4: P(0) Repeated table rows and exception actions align consistently.  ||  Q(0) Train and maintenance rows follow consistent alignment.
    astra-medium c5: P(0) The outer layout fits the viewport.  ||  Q(0) The complete layout fits the viewport width.
    astra-medium d1: P(3) The constrained roster and clipped operational panels need structural resizing.  ||  Q(6) The hierarchy and operational coverage are ready apart from minor label refinement.
    astra-high b1: P(1) The roster claims eleven trains but exposes four rows, and the chart shows only the selected subdivision.  ||  Q(2) The now line locates all eleven on-subdivision trains, with labeled trajectories and a state legend.
    astra-high b2: P(1) The separate exception column runs beside the main traffic chart.  ||  Q(2) Three actionable exceptions sit above the traffic graph and roster.
    astra-high b3: P(2) Crew rows show on-duty times, remaining hours and outlaw times.  ||  Q(2) The roster lists on-duty, on-the-law and hours-left columns.
    astra-high b4: P(2) Track authorities include milepost limits and explicit start–end times.  ||  Q(2) The maintenance table gives limits, effective intervals and authority states.
    astra-high c1: P(1) The crew relief column and lowest exception card are visibly cut off.  ||  Q(1) The subdivision description in the top bar ends in a visible ellipsis.
    astra-high c2: P(1) Condensed, faint chart labels and ancillary text are difficult to read at native size.  ||  Q(0) The main tables and annotations have readable contrast against the light background.
    astra-high c3: P(0) The panels contain real train, crew and authority information.  ||  Q(0) The chart, detail panel and lower tables are populated.
    astra-high c4: P(0) Repeated cards and table rows maintain their spacing.  ||  Q(0) The exception rows and tabular columns follow consistent alignment.
    astra-high c5: P(0) The page frame stays inside the viewport.  ||  Q(0) Tables and chart fit the page width.
    astra-high d1: P(3) Reform the fixed-height panels so the full train roster and supporting information are visible.  ||  Q(5) Only minor header truncation and annotation refinements are needed.
    claude-opus b1: P(1) the header claims 11 of 11 but the roster window shows only four rows; positions otherwise have to be read off the stringline at the 16:42 line  ||  Q(1) the first screen holds only the stringline and one selected train; the TRAINS table with location, speed and STATUS for all 13 sits a full screen down
    claude-opus b2: P(2) an EXCEPTIONS rail runs the full right edge, ordered CRITICAL then WARNING, separate from the trains table lower left  ||  Q(2) three exception rows with their decisions sit at the very top, under a stated rule that everything else is merely late and lives in the table below
    claude-opus b3: P(2) CREWS ON DUTY table gives ON DUTY 06:26, REMAINING 1:43 and OUTLAWS 18:26 per crew under a 12-hour limit  ||  Q(2) TRAINS columns ON DUTY 03:40, ON THE LAW 15:40, LEFT 1:14, echoed in the detail panel's on-duty and law times
    claude-opus b4: P(2) TRACK AND TIME lists Form B 24-118 MP 104.2-110.6 07:00-17:30 and T&T 24-207 15:15-18:00, both marked IN EFFECT  ||  Q(2) MAINTENANCE WINDOWS AND WAYSIDE lists gang, authority, limits and IN EFFECT spans 08:00-16:00, 13:00-until further notice, 15:30-16:15
    claude-opus c1: P(1) the crews table's last column is sliced mid-header (REL) with Var and Cal cut off, and the exceptions rail cuts an ADVISORY card in half at the bottom  ||  Q(1) the header's territory line is ellipsised mid-phrase (CTC Elk Yard-Sutton, TWC Sutton...)
    claude-opus c2: P(1) the in-chart stringline annotations (17:04 71.6, Form B 24-118, 16:49 108.8) are tiny and low-contrast against the plot  ||  Q(0) generous type throughout; even the chart annotations hold their weight on the light ground
    claude-opus c3: P(0) all panels carry real train, crew and authority data  ||  Q(0) no empty or template regions; the chart, tables and detail panel are all populated
    claude-opus c4: P(0) cards and the KPI strip keep an even rhythm and share gutters  ||  Q(0) exception rows, table columns and the right panel's label/value pairs align consistently
    claude-opus c5: P(0) the whole board fits 1440 x 900 with no horizontal overflow  ||  Q(0) the page is a single column inside the viewport width
    claude-opus d1: P(4) the roster must be re-formed so 11 trains fit the fixed board, and the crews table needs its truncated column back  ||  Q(6) only the truncated header string and small chart-label collisions stand between this and delivery
    claude-sonnet b1: P(1) Trains on the ground panel header reads '11 of 11' but only 4 rows (M31 06 - L505 06) render in the single, non-scrolling viewport.  ||  Q(1) TRAINS table with per-train speed, delay and status begins on tile-2; only the stringline chart is in the first viewport.
    claude-sonnet b2: P(2) Delay Exceptions column with CRITICAL/WARNING tags sits at top right, ahead of the train roster.  ||  Q(2) Three exception rows (M412 stop, M411/L071 approach) sit above the chart, each with a recommended action button.
    claude-sonnet b3: P(2) Crews on duty table shows ON DUTY clock time and REMAINING countdown for each crew.  ||  Q(2) TRAINS table has ON DUTY and ON THE LAW columns with clock times and countdowns for every train.
    claude-sonnet b4: P(2) Track and Time panel lists explicit windows, e.g. Form B 24-118 '07:00 - 17:30'.  ||  Q(2) MAINTENANCE WINDOWS AND WAYSIDE table lists IN EFFECT ranges such as 08:00-16:00 and 13:00-Until further notice.
    claude-sonnet c1: P(1) Rightmost 'REL' column values are cut off mid-word ('Var', 'Cal') at the panel edge.  ||  Q(0) No truncated labels or overflowing text found in the tables.
    claude-sonnet c2: P(0) Not seen; body text is a consistent, legible size.  ||  Q(0) Monospace text is small throughout but legible at capture resolution.
    claude-sonnet c3: P(0) No placeholder content seen.  ||  Q(0) No placeholder or broken regions seen.
    claude-sonnet c4: P(0) Stat tiles and table rows keep consistent alignment.  ||  Q(0) Table columns and exception rows keep consistent alignment.
    claude-sonnet c5: P(0) Content stays within the 1440px frame.  ||  Q(0) Content stays within the 1440px frame on both captures.
    claude-sonnet d1: P(3) The train roster and crew-relief column are both truncated with no scroll available on this single-viewport page; the panel needs resizing or scrolling added.  ||  Q(6) Well-organized and complete; would ship after cosmetic polish (accent color, spacing) rather than structural change.

## Cell rebate·A · item d1
- astra-medium: d1 P=6 Q=4
    P: Only minor copy and texture refinements are needed; the four requested tasks are clearly organized.
    Q: Place an eligibility summary near the opening estimate and reduce the distance to the application.
- astra-high: d1 P=6 Q=4
    P: Only minor copy and visual polish remain; the opening already answers who, how much and how long.
    Q: Bring eligibility ahead of the large estimator and rebalance the narrow application region.
- claude-opus: d1 P=6 Q=4
    P: states all four asks and reads cleanly; only its visual sameness from section to section would prompt any change
    Q: eligibility never reaches the first screen, so the qualification region would have to be raised or summarised before delivery
- claude-sonnet: d1 P=6 Q=7
    P: detailed, well-organized fund-tracker system; only cosmetic tightening needed before delivery
    Q: most complete site-chrome replica (breadcrumbs, secondary nav, proof columns, disclosures); deliverable as is
  Context for rebate·A: every other clause on both pages, per rater (rating in parentheses):
    astra-medium b1: P(2) The opening Who row explicitly names owners and renters on a residential utility account.  ||  Q(0) The first screen describes payment by capacity but gives no resident or property requirements.
    astra-medium b2: P(2) The rate schedule gives base, adders, maximums and percentage cost caps with worked examples.  ||  Q(2) The rebate schedule includes standard and income rates, adders, conditions and lifetime maximum.
    astra-medium b3: P(2) The installer table lists ten firms with license, area, systems and availability.  ||  Q(2) A detailed approved-installers register includes firms, licenses, areas and certified brands.
    astra-medium b4: P(2) Apply for the rebate is backed by the visible five-part application form.  ||  Q(2) Start the application corresponds to the visible application at the bottom of the page.
    astra-medium c1: P(0) No content visibly escapes or is cut off by its container.  ||  Q(0) No content visibly escapes or is cut off by its container.
    astra-medium c2: P(0) Native-resolution text remains readable, including supporting labels.  ||  Q(0) Native-resolution text remains readable, including supporting labels.
    astra-medium c3: P(0) No broken image, template copy or empty placeholder region is visible.  ||  Q(0) No broken image, template copy or empty placeholder region is visible.
    astra-medium c4: P(0) Repeated rows, fields and cards use consistent alignment and spacing.  ||  Q(0) Repeated rows, fields and cards use consistent alignment and spacing.
    astra-medium c5: P(0) The visible page stays within the capture width.  ||  Q(0) The visible page stays within the capture width.
    astra-medium d1: P(6) Only minor copy and texture refinements are needed; the four requested tasks are clearly organized.  ||  Q(4) Place an eligibility summary near the opening estimate and reduce the distance to the application.
    astra-high b1: P(2) The first-screen Who row explicitly names owners and renters on a Marston residential account.  ||  Q(0) The first screen is devoted to funding and a rebate estimate rather than who qualifies.
    astra-high b2: P(2) The rate schedule states $300 per kWh, conditional adders, individual limits and combined cost caps.  ||  Q(2) The opening states $385 per usable kWh, the 16-kWh limit and the Evening Reserve rate.
    astra-high b3: P(2) The approved-installer table lists ten firms with licences, coverage and availability.  ||  Q(2) The approved-installer register lists firms with licences, service areas and certified brands.
    astra-high b4: P(2) Apply for the rebate and Apply navigation accompany the embedded reservation form.  ||  Q(2) Start the application and Apply navigation accompany the embedded application.
    astra-high c1: P(0) No content is visibly cut off by a container in the supplied captures.  ||  Q(0) No content is visibly cut off by a container in the supplied captures.
    astra-high c2: P(0) Native-resolution body text and supporting labels remain readable.  ||  Q(0) Native-resolution body text and supporting labels remain readable.
    astra-high c3: P(0) No broken image slot or unfinished placeholder region is visible.  ||  Q(0) No broken image slot or unfinished placeholder region is visible.
    astra-high c4: P(0) Repeated rows, controls and columns use consistent spacing and alignment.  ||  Q(0) Repeated rows, controls and columns use consistent spacing and alignment.
    astra-high c5: P(0) No sideways overflow is visible in the supplied captures.  ||  Q(0) No sideways overflow is visible in the supplied captures.
    astra-high d1: P(6) Only minor copy and visual polish remain; the opening already answers who, how much and how long.  ||  Q(4) Bring eligibility ahead of the large estimator and rebalance the narrow application region.
    claude-opus b1: P(2) first screen carries a labelled 'Who:' line — 'owners and renters on a Marston Public Power residential account' — beside how much and how long  ||  Q(0) first screen carries only the rate headline, the fund panel and the estimate; eligibility appears solely as a 'Who qualifies' jump link
    claude-opus b2: P(2) rate schedule gives $300 per kWh base to a $4,500 cap, a $250 income adder, $1,000 evening-peak, up to $1,200 service upgrade and a $9,400 maximum, with two worked examples  ||  Q(2) 'The rebate schedule' table gives $385 and $610 per kWh, three adders, the 16.0 kWh cap and a $9,300 maximum with each line's condition and limit
    claude-opus b3: P(2) 'Approved installers' table of ten firms with city licence, service area, certified brands, availability and last-verified date  ||  Q(2) 'Approved installers' register, sixteen firms with licence, service area, certified brands, installs and approval date, plus area and availability filters
    claude-opus b4: P(2) one Apply form, service address through attestations, with a Submit application button and an estimate panel alongside  ||  Q(2) 'The application' section holds the whole form, service through payment, ending in a 'File the application' button
    claude-opus c1: P(0) seven-condition list, the conditional-review box and both worked examples end inside their rules  ||  Q(0) requirement rows, proof column and register rows all sit inside their rules
    claude-opus c2: P(0) leaders and mono figures are small but legible; body copy holds contrast on the textured ground  ||  Q(0) the mono proof column is small but crisp at native resolution in tile-2 and tile-3
    claude-opus c3: P(0) no empty slots; every panel including the estimate sidebar shows real values  ||  Q(0) no empty or template regions; the register and the returned-applications panel are fully populated
    claude-opus c4: P(0) the seven numbered conditions and both worked-example tables use one row rhythm and one leader style  ||  Q(0) requirement blocks, proof entries and schedule rows repeat on one consistent rhythm
    claude-opus c5: P(0) content stays within the frame; no sideways scroll in the full-page capture  ||  Q(0) no sideways scroll; the wide register table stays inside the content column
    claude-opus d1: P(6) states all four asks and reads cleanly; only its visual sameness from section to section would prompt any change  ||  Q(4) eligibility never reaches the first screen, so the qualification region would have to be raised or summarised before delivery
    claude-sonnet b1: P(2) the hero's 'Who:' row states 'owners and renters on a Marston Public Power residential account' within the first screen  ||  Q(0) first screen shows the rate calculator and funding bar, not an eligibility statement; 'Who qualifies' is a lower section
    claude-sonnet b2: P(2) hero states 'Up to $9,400' with 'How much: $300 per kWh, plus adders'; a full rate schedule and worked examples follow  ||  Q(2) hero states the rate ($385/kWh, cap 16.0 kWh) with a live $6,435 estimate for a 13.0 kWh battery
    claude-sonnet b3: P(2) 'Approved installers' table lists ten firms with licence, area and availability  ||  Q(2) 'Approved installers' table lists thirteen firms with licence, service area, certifications and install counts
    claude-sonnet b4: P(2) 'Apply for the rebate' button sits in the hero and a full 'Apply' form section follows  ||  Q(2) 'Start the application' button sits in the hero and a full 'The application' form follows
    claude-sonnet c1: P(0) no clipped content observed  ||  Q(0) no clipped content observed
    claude-sonnet c2: P(0) text legible throughout including small monospace labels  ||  Q(0) text legible throughout including the small 'proof' column entries
    claude-sonnet c3: P(0) no placeholder or broken regions observed  ||  Q(0) no placeholder or broken regions observed
    claude-sonnet c4: P(0) consistent alignment across the numbered list and rate tables  ||  Q(0) consistent alignment across breadcrumb, cards and tables
    claude-sonnet c5: P(0) no horizontal overflow observed  ||  Q(0) no horizontal overflow observed
    claude-sonnet d1: P(6) detailed, well-organized fund-tracker system; only cosmetic tightening needed before delivery  ||  Q(7) most complete site-chrome replica (breadcrumbs, secondary nav, proof columns, disclosures); deliverable as is

## Cell rebate·A · item b1
- astra-medium: b1 P=2 Q=0
    P: The opening Who row explicitly names owners and renters on a residential utility account.
    Q: The first screen describes payment by capacity but gives no resident or property requirements.
- astra-high: b1 P=2 Q=0
    P: The first-screen Who row explicitly names owners and renters on a Marston residential account.
    Q: The first screen is devoted to funding and a rebate estimate rather than who qualifies.
- claude-opus: b1 P=2 Q=0
    P: first screen carries a labelled 'Who:' line — 'owners and renters on a Marston Public Power residential account' — beside how much and how long
    Q: first screen carries only the rate headline, the fund panel and the estimate; eligibility appears solely as a 'Who qualifies' jump link
- claude-sonnet: b1 P=2 Q=0
    P: the hero's 'Who:' row states 'owners and renters on a Marston Public Power residential account' within the first screen
    Q: first screen shows the rate calculator and funding bar, not an eligibility statement; 'Who qualifies' is a lower section
