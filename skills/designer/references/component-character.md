# Component character

The same component — a primary/secondary/disabled button set, an interactive card, and a data table — implemented three times, once per worked derivation from `references/stances.md`, with identical content shape so the differences in typography, density, borders, radius, color, shadow, hover behavior, and focus treatment are easy to diff. Use this file at the build step, after the tokens exist: it shows how a derived system expresses itself in components, and it is the reference for interaction states. The token values are those three products' instantiations, not a menu — port the structure and the state model, and let your own derived tokens supply the values. Adapt class names to whatever styling approach the project actually uses.

---

### 1. Precision industrial

```tsx
// PrecisionIndustrialExamples.tsx
const rows = [
  { project: "North Terminal", owner: "M. Ibarra", status: "At risk", date: "18 Jul", budget: "$42,680" },
  { project: "Signal Relay", owner: "A. Chen", status: "On track", date: "22 Jul", budget: "$18,420" },
  { project: "Foundry Survey", owner: "R. Patel", status: "Review", date: "29 Jul", budget: "$31,050" },
];

const statusClass = {
  "At risk": "bg-[#B63B3B] text-white",
  "On track": "bg-[#2C725E] text-white",
  Review: "bg-[#B75D16] text-white",
};

export default function PrecisionIndustrialExamples() {
  return (
    <main className="min-h-screen bg-[#F4F6F7] px-6 py-10 font-['Manrope'] text-[#162024] sm:px-10">
      <div className="mx-auto max-w-5xl space-y-10">
        <header className="border-b border-[#C7D0D2] pb-6">
          <p className="text-[11px] font-bold uppercase tracking-[0.09em] text-[#607076]">
            Component specimen / 01
          </p>
          <h1 className="mt-2 font-['Archivo'] text-[32px] font-semibold leading-[1.12] tracking-[-0.022em]">
            Precision industrial
          </h1>
        </header>

        {/* Buttons */}
        <section aria-labelledby="industrial-buttons">
          <h2
            id="industrial-buttons"
            className="mb-4 text-[11px] font-bold uppercase tracking-[0.08em] text-[#607076]"
          >
            Buttons
          </h2>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              className="inline-flex h-10 items-center justify-center rounded-[4px] border border-[#123B45] bg-[#123B45] px-4 text-[13px] font-bold tracking-[-0.005em] text-[#F7FAFA] transition-[background-color,border-color,box-shadow,transform] duration-150 ease-out hover:bg-[#0C3038] hover:border-[#0C3038] active:translate-y-px active:bg-[#08252B] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F4F6F7] disabled:cursor-not-allowed disabled:border-[#AEBBBC] disabled:bg-[#AEBBBC] disabled:text-[#E9EEEE]"
            >
              Create work order
            </button>

            <button
              type="button"
              className="inline-flex h-10 items-center justify-center rounded-[4px] border border-[#8FA0A4] bg-transparent px-4 text-[13px] font-bold tracking-[-0.005em] text-[#243237] transition-[background-color,border-color,color,box-shadow,transform] duration-150 ease-out hover:border-[#123B45] hover:bg-[#E3E9EA] active:translate-y-px active:bg-[#D5DFE0] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F4F6F7] disabled:cursor-not-allowed disabled:border-[#C7D0D2] disabled:text-[#93A0A3]"
            >
              Export report
            </button>

            <button
              type="button"
              disabled
              className="inline-flex h-10 items-center justify-center rounded-[4px] border border-[#123B45] bg-[#123B45] px-4 text-[13px] font-bold tracking-[-0.005em] text-[#F7FAFA] transition-[background-color,border-color,box-shadow,transform] duration-150 ease-out hover:bg-[#0C3038] active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F4F6F7] disabled:cursor-not-allowed disabled:border-[#AEBBBC] disabled:bg-[#AEBBBC] disabled:text-[#E9EEEE]"
            >
              Awaiting approval
            </button>
          </div>
        </section>

        {/* Interactive card */}
        <section aria-labelledby="industrial-card">
          <h2
            id="industrial-card"
            className="mb-4 text-[11px] font-bold uppercase tracking-[0.08em] text-[#607076]"
          >
            Card
          </h2>

          <a
            href="#north-terminal"
            className="group block max-w-xl rounded-[6px] border border-[#C7D0D2] bg-white p-5 transition-[border-color,background-color,box-shadow,transform] duration-150 ease-out hover:border-[#7E9297] hover:bg-[#FCFDFD] hover:shadow-[0_1px_2px_rgb(22_32_36_/_8%),0_8px_20px_rgb(22_32_36_/_10%)] active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F4F6F7]"
          >
            <div className="flex items-start justify-between gap-6">
              <div>
                <p className="font-['Geist_Mono'] text-[11px] font-medium tracking-[-0.01em] text-[#607076]">
                  JOB-0418 · EAST SECTOR
                </p>
                <h3 className="mt-2 font-['Archivo'] text-[20px] font-semibold leading-[1.25] tracking-[-0.008em] text-[#162024]">
                  North Terminal inspection
                </h3>
                <p className="mt-2 max-w-md text-[14px] leading-[1.5] text-[#607076]">
                  Three unresolved equipment flags require assignment before the next field
                  window.
                </p>
              </div>

              <span className="shrink-0 border border-[#D7AA8B] bg-[#F9E6D9] px-2 py-1 font-['Geist_Mono'] text-[10px] font-semibold uppercase tracking-[0.04em] text-[#8C3C17]">
                3 flags
              </span>
            </div>

            <div className="mt-5 flex items-center justify-between border-t border-[#DCE3E4] pt-3">
              <span className="font-['Geist_Mono'] text-[12px] font-medium tracking-[-0.01em] text-[#607076]">
                Due 18 Jul · 14:00
              </span>
              <span className="text-[13px] font-bold text-[#123B45] transition-transform duration-150 group-hover:translate-x-0.5">
                View job →
              </span>
            </div>
          </a>
        </section>

        {/* Data table */}
        <section aria-labelledby="industrial-table">
          <div className="mb-4 flex items-end justify-between">
            <div>
              <h2
                id="industrial-table"
                className="text-[11px] font-bold uppercase tracking-[0.08em] text-[#607076]"
              >
                Data table
              </h2>
              <p className="mt-1 text-[13px] text-[#607076]">Active work orders</p>
            </div>
            <button
              type="button"
              className="text-[12px] font-bold text-[#123B45] underline decoration-[#8FA0A4] underline-offset-4 transition-colors hover:text-[#D46B2C] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 focus-visible:ring-offset-[#F4F6F7]"
            >
              View all
            </button>
          </div>

          <div className="overflow-x-auto rounded-[6px] border border-[#C7D0D2] bg-white">
            <table className="w-full min-w-[720px] border-collapse text-left">
              <thead className="bg-[#EDF1F1]">
                <tr className="border-b border-[#C7D0D2]">
                  {["Project", "Owner", "Status", "Due date", "Approved budget", ""].map((heading) => (
                    <th
                      key={heading || "action"}
                      scope="col"
                      className="px-4 py-3 text-[11px] font-bold uppercase tracking-[0.08em] text-[#607076]"
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.project}
                    className="group border-b border-[#DCE3E4] last:border-b-0 hover:bg-[#F6F8F8] focus-within:bg-[#F1F5F5]"
                  >
                    <td className="px-4 py-3.5 text-[13px] font-bold text-[#162024]">
                      {row.project}
                    </td>
                    <td className="px-4 py-3.5 text-[13px] text-[#607076]">{row.owner}</td>
                    <td className="px-4 py-3.5">
                      <span
                        className={`inline-flex rounded-[2px] px-2 py-1 font-['Geist_Mono'] text-[10px] font-semibold uppercase tracking-[0.035em] ${statusClass[row.status as keyof typeof statusClass]}`}
                      >
                        {row.status}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 font-['Geist_Mono'] text-[12px] font-medium tracking-[-0.01em] text-[#243237]">
                      {row.date}
                    </td>
                    <td className="px-4 py-3.5 font-['Geist_Mono'] text-[12px] font-medium tabular-nums tracking-[-0.01em] text-[#243237]">
                      {row.budget}
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      <button
                        type="button"
                        aria-label={`Open ${row.project}`}
                        className="text-[12px] font-bold text-[#123B45] opacity-0 transition-[color,opacity] duration-150 hover:text-[#D46B2C] focus-visible:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D46B2C] focus-visible:ring-offset-2 group-hover:opacity-100"
                      >
                        Open →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}
```

---

### 2. Quiet editorial

```tsx
// QuietEditorialExamples.tsx
const rows = [
  { project: "Autumn House", owner: "L. Okafor", status: "In edit", date: "18 Jul", budget: "$42,680" },
  { project: "The Estuary", owner: "N. Reyes", status: "On schedule", date: "22 Jul", budget: "$18,420" },
  { project: "After the Rain", owner: "S. Wilson", status: "Review", date: "29 Jul", budget: "$31,050" },
];

const statusClass = {
  "In edit": "border-[#B97965] bg-[#F8E4DD] text-[#7D3423]",
  "On schedule": "border-[#89A495] bg-[#E5EEE7] text-[#355C43]",
  Review: "border-[#C7A86A] bg-[#F7EFD9] text-[#73561B]",
};

export default function QuietEditorialExamples() {
  return (
    <main className="min-h-screen bg-[#F5F0E8] px-6 py-12 font-['Public_Sans'] text-[#24211E] sm:px-10 md:py-16">
      <div className="mx-auto max-w-5xl space-y-16">
        <header className="border-b border-[#D4CABE] pb-8">
          <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#756D64]">
            Studio ledger · July 2026
          </p>
          <h1 className="mt-3 font-['Newsreader'] text-[44px] font-medium leading-[1.04] tracking-[-0.024em] sm:text-[56px]">
            Quiet editorial
          </h1>
        </header>

        {/* Buttons */}
        <section aria-labelledby="editorial-buttons">
          <h2
            id="editorial-buttons"
            className="mb-5 text-[11px] font-bold uppercase tracking-[0.12em] text-[#756D64]"
          >
            Buttons
          </h2>

          <div className="flex flex-wrap items-center gap-x-6 gap-y-4">
            <button
              type="button"
              className="inline-flex min-h-11 items-center justify-center rounded-[4px] border border-[#2C302A] bg-[#2C302A] px-5 text-[13px] font-semibold text-[#FAF6EE] transition-[background-color,border-color,box-shadow,transform] duration-[160ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)] hover:bg-[#464B42] hover:border-[#464B42] active:translate-y-px active:bg-[#1E211D] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A9462D] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F5F0E8] disabled:cursor-not-allowed disabled:border-[#A9A39B] disabled:bg-[#A9A39B] disabled:text-[#EAE5DD]"
            >
              Prepare call sheet
            </button>

            <button
              type="button"
              className="inline-flex min-h-11 items-center justify-center border-b border-[#756D64] px-1 text-[13px] font-semibold text-[#24211E] transition-[border-color,color,transform] duration-[160ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)] hover:border-[#A9462D] hover:text-[#A9462D] active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A9462D] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F5F0E8] disabled:cursor-not-allowed disabled:border-[#C8C0B6] disabled:text-[#9A9187]"
            >
              Download treatment
            </button>

            <button
              type="button"
              disabled
              className="inline-flex min-h-11 items-center justify-center rounded-[4px] border border-[#2C302A] bg-[#2C302A] px-5 text-[13px] font-semibold text-[#FAF6EE] transition-[background-color,border-color,box-shadow,transform] duration-[160ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)] hover:bg-[#464B42] active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A9462D] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F5F0E8] disabled:cursor-not-allowed disabled:border-[#A9A39B] disabled:bg-[#A9A39B] disabled:text-[#EAE5DD]"
            >
              Awaiting cut
            </button>
          </div>
        </section>

        {/* Interactive card */}
        <section aria-labelledby="editorial-card">
          <h2
            id="editorial-card"
            className="mb-5 text-[11px] font-bold uppercase tracking-[0.12em] text-[#756D64]"
          >
            Card
          </h2>

          <a
            href="#autumn-house"
            className="group block max-w-2xl border-y border-[#D4CABE] py-7 transition-colors duration-[260ms] [transition-timing-function:cubic-bezier(0.22,1,0.36,1)] hover:border-[#9A8D80] hover:bg-[#F8F3EB] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A9462D] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F5F0E8]"
          >
            <div className="grid gap-6 sm:grid-cols-[minmax(0,1fr)_auto]">
              <div>
                <p className="font-['DM_Mono'] text-[11px] font-medium tracking-[0.01em] text-[#756D64]">
                  FEATURE · POST-PRODUCTION · 04
                </p>
                <h3 className="mt-3 font-['Newsreader'] text-[32px] font-medium leading-[1.12] tracking-[-0.018em] text-[#24211E]">
                  Autumn House
                </h3>
                <p className="mt-3 max-w-xl text-[16px] leading-[1.62] tracking-[-0.002em] text-[#5F5850]">
                  The editor’s assembly is ready for review, with one music cue and two
                  archival clearances still unresolved.
                </p>
              </div>

              <span className="h-fit border border-[#B97965] bg-[#F8E4DD] px-2.5 py-1.5 font-['DM_Mono'] text-[10px] font-semibold uppercase tracking-[0.05em] text-[#7D3423]">
                In edit
              </span>
            </div>

            <div className="mt-7 flex items-center justify-between">
              <span className="font-['DM_Mono'] text-[11px] tracking-[0.01em] text-[#756D64]">
                Delivery · 18 July
              </span>
              <span className="text-[13px] font-semibold text-[#24211E] transition-[color,transform] duration-[160ms] group-hover:translate-x-1 group-hover:text-[#A9462D]">
                Open project →
              </span>
            </div>
          </a>
        </section>

        {/* Data table */}
        <section aria-labelledby="editorial-table">
          <div className="mb-5">
            <p className="text-[11px] font-bold uppercase tracking-[0.12em] text-[#756D64]">
              Current slate
            </p>
            <h2
              id="editorial-table"
              className="mt-2 font-['Newsreader'] text-[32px] font-medium leading-[1.12] tracking-[-0.018em]"
            >
              Productions in motion
            </h2>
          </div>

          <div className="overflow-x-auto border-y border-[#D4CABE]">
            <table className="w-full min-w-[720px] border-collapse text-left">
              <thead>
                <tr className="border-b border-[#D4CABE]">
                  {["Project", "Producer", "Stage", "Delivery", "Budget", ""].map((heading) => (
                    <th
                      key={heading || "action"}
                      scope="col"
                      className="px-3 py-3 text-[11px] font-bold uppercase tracking-[0.1em] text-[#756D64] first:pl-0 last:pr-0"
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.project}
                    className="group border-b border-[#E0D8CE] last:border-b-0 transition-colors duration-[160ms] hover:bg-[#F8F3EB] focus-within:bg-[#F8F3EB]"
                  >
                    <td className="px-3 py-5 font-['Newsreader'] text-[21px] font-medium leading-[1.2] tracking-[-0.01em] first:pl-0">
                      {row.project}
                    </td>
                    <td className="px-3 py-5 text-[14px] text-[#5F5850]">{row.owner}</td>
                    <td className="px-3 py-5">
                      <span
                        className={`inline-flex border px-2 py-1 font-['DM_Mono'] text-[10px] font-medium uppercase tracking-[0.04em] ${statusClass[row.status as keyof typeof statusClass]}`}
                      >
                        {row.status}
                      </span>
                    </td>
                    <td className="px-3 py-5 font-['DM_Mono'] text-[11px] tracking-[0.01em] text-[#5F5850]">
                      {row.date}
                    </td>
                    <td className="px-3 py-5 font-['DM_Mono'] text-[11px] tabular-nums tracking-[0.01em] text-[#5F5850]">
                      {row.budget}
                    </td>
                    <td className="px-0 py-5 text-right">
                      <button
                        type="button"
                        aria-label={`Open ${row.project}`}
                        className="text-[13px] font-semibold text-[#24211E] underline decoration-transparent underline-offset-4 transition-[color,text-decoration-color] duration-[160ms] hover:text-[#A9462D] hover:decoration-[#A9462D] focus-visible:decoration-[#A9462D] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#A9462D] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F5F0E8]"
                      >
                        Open
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}
```

---

### 3. Playful consumer

```tsx
// PlayfulConsumerExamples.tsx
const rows = [
  { habit: "Morning stretch", streak: "12 days", status: "On fire", next: "Today", score: "+36" },
  { habit: "Sketch for fun", streak: "6 days", status: "Growing", next: "Today", score: "+18" },
  { habit: "Read 15 minutes", streak: "3 days", status: "New", next: "Tomorrow", score: "+9" },
];

const statusClass = {
  "On fire": "border-[#D17A15] bg-[#FFF0C8] text-[#703B00]",
  Growing: "border-[#4CB184] bg-[#DCF7E9] text-[#124C35]",
  New: "border-[#7768E4] bg-[#E9E4FF] text-[#3D317E]",
};

export default function PlayfulConsumerExamples() {
  return (
    <main className="min-h-screen bg-[#F7F5FF] px-5 py-8 font-['DM_Sans'] text-[#24203D] sm:px-8 sm:py-12">
      <div className="mx-auto max-w-5xl space-y-10">
        <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-[12px] font-bold tracking-[0.02em] text-[#716B88]">Your component kit</p>
            <h1 className="mt-1 font-['Bricolage_Grotesque'] text-[36px] font-bold leading-[1.08] tracking-[-0.025em] sm:text-[52px]">
              Playful consumer
            </h1>
          </div>
          <span className="w-fit rounded-full bg-[#E9E4FF] px-3 py-1.5 text-[12px] font-bold text-[#4A3AB2]">
            Small wins, daily
          </span>
        </header>

        {/* Buttons */}
        <section aria-labelledby="playful-buttons">
          <h2
            id="playful-buttons"
            className="mb-4 font-['Bricolage_Grotesque'] text-[20px] font-bold tracking-[-0.008em]"
          >
            Buttons
          </h2>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              className="inline-flex min-h-11 items-center justify-center rounded-[14px] border border-[#5A47D5] bg-[#5A47D5] px-5 text-[14px] font-bold text-white shadow-[0_2px_4px_rgb(36_32_61_/_7%),0_10px_24px_rgb(90_71_213_/_16%)] transition-[background-color,border-color,box-shadow,transform] duration-[140ms] [transition-timing-function:cubic-bezier(0.2,0.8,0.2,1)] hover:-translate-y-0.5 hover:bg-[#4938C5] hover:shadow-[0_4px_10px_rgb(36_32_61_/_9%),0_14px_28px_rgb(90_71_213_/_22%)] active:translate-y-px active:scale-[0.98] active:bg-[#3E2FA8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5A47D5] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F7F5FF] disabled:cursor-not-allowed disabled:border-[#B6AEE2] disabled:bg-[#B6AEE2] disabled:text-[#F5F2FF] disabled:shadow-none"
            >
              Log today’s win
            </button>

            <button
              type="button"
              className="inline-flex min-h-11 items-center justify-center rounded-[14px] border border-[#DCD7EF] bg-white px-5 text-[14px] font-bold text-[#342B76] shadow-[0_1px_2px_rgb(36_32_61_/_5%),0_7px_16px_rgb(90_71_213_/_8%)] transition-[background-color,border-color,box-shadow,transform] duration-[140ms] [transition-timing-function:cubic-bezier(0.2,0.8,0.2,1)] hover:-translate-y-0.5 hover:border-[#AFA5EC] hover:bg-[#F5F2FF] hover:shadow-[0_2px_5px_rgb(36_32_61_/_7%),0_10px_20px_rgb(90_71_213_/_12%)] active:translate-y-px active:scale-[0.98] active:bg-[#E9E4FF] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5A47D5] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F7F5FF] disabled:cursor-not-allowed disabled:border-[#E6E1F4] disabled:bg-[#F4F2F9] disabled:text-[#AAA3BD] disabled:shadow-none"
            >
              Edit habits
            </button>

            <button
              type="button"
              disabled
              className="inline-flex min-h-11 items-center justify-center rounded-[14px] border border-[#5A47D5] bg-[#5A47D5] px-5 text-[14px] font-bold text-white shadow-[0_2px_4px_rgb(36_32_61_/_7%),0_10px_24px_rgb(90_71_213_/_16%)] transition-[background-color,border-color,box-shadow,transform] duration-[140ms] [transition-timing-function:cubic-bezier(0.2,0.8,0.2,1)] hover:-translate-y-0.5 hover:bg-[#4938C5] active:translate-y-px active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5A47D5] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F7F5FF] disabled:cursor-not-allowed disabled:border-[#B6AEE2] disabled:bg-[#B6AEE2] disabled:text-[#F5F2FF] disabled:shadow-none"
            >
              Come back tomorrow
            </button>
          </div>
        </section>

        {/* Interactive card */}
        <section aria-labelledby="playful-card">
          <h2
            id="playful-card"
            className="mb-4 font-['Bricolage_Grotesque'] text-[20px] font-bold tracking-[-0.008em]"
          >
            Card
          </h2>

          <a
            href="#morning-stretch"
            className="group relative block max-w-xl overflow-hidden rounded-[20px] border border-[#DCD7EF] bg-white p-6 shadow-[0_1px_2px_rgb(36_32_61_/_5%),0_7px_16px_rgb(90_71_213_/_8%)] transition-[border-color,box-shadow,transform] duration-[220ms] [transition-timing-function:cubic-bezier(0.16,1,0.3,1)] hover:-translate-y-1 hover:border-[#B2A8EF] hover:shadow-[0_5px_12px_rgb(36_32_61_/_10%),0_22px_42px_rgb(90_71_213_/_17%)] active:translate-y-0 active:scale-[0.99] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5A47D5] focus-visible:ring-offset-4 focus-visible:ring-offset-[#F7F5FF]"
          >
            <div className="absolute -right-10 -top-12 h-40 w-40 rounded-[58%_42%_51%_49%_/_42%_55%_45%_58%] bg-[#E9E4FF] transition-transform duration-[320ms] [transition-timing-function:cubic-bezier(0.34,1.56,0.64,1)] group-hover:rotate-12 group-hover:scale-110" />
            <div className="absolute right-10 top-8 h-8 w-8 rounded-full bg-[#FFB94D] transition-transform duration-[320ms] [transition-timing-function:cubic-bezier(0.34,1.56,0.64,1)] group-hover:-translate-y-1 group-hover:translate-x-1" />

            <div className="relative">
              <div className="flex items-start justify-between gap-5">
                <div>
                  <p className="text-[12px] font-bold tracking-[0.02em] text-[#716B88]">
                    Your next tiny win
                  </p>
                  <h3 className="mt-2 font-['Bricolage_Grotesque'] text-[28px] font-bold leading-[1.14] tracking-[-0.018em] text-[#24203D]">
                    Morning stretch
                  </h3>
                </div>

                <span className="rounded-full border border-[#D17A15] bg-[#FFF0C8] px-3 py-1.5 text-[12px] font-bold text-[#703B00]">
                  12-day streak
                </span>
              </div>

              <p className="mt-3 max-w-sm text-[16px] font-medium leading-[1.5] text-[#5E5874]">
                Two minutes counts. Give your shoulders a little “thank you.”
              </p>

              <div className="mt-6 flex items-center justify-between">
                <span className="rounded-full bg-[#DCF7E9] px-3 py-1.5 text-[12px] font-bold text-[#124C35]">
                  +3 energy points
                </span>
                <span className="text-[14px] font-bold text-[#5A47D5] transition-transform duration-[140ms] group-hover:translate-x-1">
                  Check in →
                </span>
              </div>
            </div>
          </a>
        </section>

        {/* Data table */}
        <section aria-labelledby="playful-table">
          <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="text-[12px] font-bold tracking-[0.02em] text-[#716B88]">This week</p>
              <h2
                id="playful-table"
                className="mt-1 font-['Bricolage_Grotesque'] text-[28px] font-bold leading-[1.14] tracking-[-0.018em]"
              >
                Habit scoreboard
              </h2>
            </div>
            <button
              type="button"
              className="rounded-full border border-[#DCD7EF] bg-white px-3 py-2 text-[12px] font-bold text-[#4A3AB2] transition-[background-color,border-color,transform] duration-[140ms] hover:-translate-y-0.5 hover:border-[#AFA5EC] hover:bg-[#F5F2FF] active:translate-y-px focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5A47D5] focus-visible:ring-offset-3 focus-visible:ring-offset-[#F7F5FF]"
            >
              See all habits
            </button>
          </div>

          <div className="overflow-x-auto rounded-[20px] border border-[#DCD7EF] bg-white shadow-[0_1px_2px_rgb(36_32_61_/_5%),0_7px_16px_rgb(90_71_213_/_8%)]">
            <table className="w-full min-w-[700px] border-collapse text-left">
              <thead className="bg-[#F0EDF8]">
                <tr className="border-b border-[#DCD7EF]">
                  {["Habit", "Streak", "Mood", "Next up", "Points", ""].map((heading) => (
                    <th
                      key={heading || "action"}
                      scope="col"
                      className="px-5 py-3 text-[12px] font-bold tracking-[0.02em] text-[#716B88]"
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.habit}
                    className="group border-b border-[#E9E5F4] last:border-b-0 transition-colors duration-[140ms] hover:bg-[#FAF9FF] focus-within:bg-[#F5F2FF]"
                  >
                    <td className="px-5 py-4 text-[14px] font-bold text-[#24203D]">{row.habit}</td>
                    <td className="px-5 py-4">
                      <span className="rounded-full bg-[#E9E4FF] px-2.5 py-1 text-[12px] font-bold text-[#4A3AB2]">
                        {row.streak}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <span
                        className={`inline-flex rounded-full border px-2.5 py-1 text-[12px] font-bold ${statusClass[row.status as keyof typeof statusClass]}`}
                      >
                        {row.status}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-[14px] font-medium text-[#5E5874]">{row.next}</td>
                    <td className="px-5 py-4 font-['Bricolage_Grotesque'] text-[20px] font-bold leading-none tracking-[-0.02em] text-[#5A47D5]">
                      {row.score}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <button
                        type="button"
                        aria-label={`Check in to ${row.habit}`}
                        className="rounded-full bg-[#5A47D5] px-3 py-1.5 text-[12px] font-bold text-white opacity-0 shadow-[0_2px_4px_rgb(36_32_61_/_7%),0_10px_20px_rgb(90_71_213_/_16%)] transition-[background-color,box-shadow,opacity,transform] duration-[140ms] hover:-translate-y-0.5 hover:bg-[#4938C5] active:translate-y-px active:scale-[0.97] focus-visible:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5A47D5] focus-visible:ring-offset-3 group-hover:opacity-100"
                      >
                        Done!
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}
```

The character differences above are concentrated in:

- **Precision industrial:** tight radius, rule-based surfaces, minimal shadow, compact mono metadata, restrained transitions.
- **Quiet editorial:** mostly flat surfaces, generous vertical rhythm, serif hierarchy, underline-led secondary actions, low-noise states.
- **Playful consumer:** larger radius, brighter controlled color, soft elevated shadows, expressive display type, springier movement, rounded status/pill treatment.

