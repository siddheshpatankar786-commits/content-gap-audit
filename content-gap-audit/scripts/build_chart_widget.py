#!/usr/bin/env python3
"""
Step 3: Given pillar_counts.json for two or more companies, generate the
Chart.js widget code (small multiples, one panel per company, data labels
on every bar) matching the format used in the original audit.

This script does NOT call the Visualizer tool itself — it just assembles
the HTML/JS string. Claude should read the output and pass it directly
to visualize:show_widget's widget_code parameter, after first calling
visualize:read_me with modules=["chart","interactive"].

Usage:
    python build_chart_widget.py <company1_pillars.json> <company2_pillars.json> ...

The first company passed is treated as the "highlighted" one (accent
border) if you want to distinguish a client from competitors — pass
your own company's file first.
"""
import json
import sys

PILLAR_ORDER = [
    'Capability / showcase (remainder)',
    'AI literacy (what/why explainers)',
    'Tool/vendor comparisons (X vs Y)',
    'AI readiness',
    'Data readiness',
    'AI adoption / maturity',
    'Implementation / how-to',
    'Execution / ROI / outcomes',
]
SHORT_LABELS = ['Capability', 'Literacy', 'Compare', 'AI ready',
                'Data ready', 'Adoption', 'Implement', 'Execution']
COLORS = ['#73726c', '#2a78d6', '#4a3aa7', '#eda100',
          '#c98500', '#e87ba4', '#008300', '#e34948']


def main():
    if len(sys.argv) < 2:
        print("Usage: python build_chart_widget.py <pillars.json> [pillars2.json ...]")
        sys.exit(1)

    companies = []
    for path in sys.argv[1:]:
        with open(path) as f:
            d = json.load(f)
        companies.append(d)

    panels_html = []
    scripts_js = []
    for idx, c in enumerate(companies):
        name = c['company']
        total = c['total_ai_relevant']
        counts = c['pillar_counts']
        values = [counts.get(p, 0) for p in PILLAR_ORDER]
        canvas_id = f"c{idx}"
        border = 'border: 2px solid var(--border-accent);' if idx == 0 else ''

        panels_html.append(f'''
  <div style="background: var(--surface-1); border-radius: 12px; padding: 1rem; {border}">
    <p style="font-size: 14px; font-weight: 500; margin: 0 0 4px;">{name}</p>
    <p style="font-size: 12px; color: var(--text-secondary); margin: 0 0 12px;">{total} AI-relevant pieces total</p>
    <div style="position: relative; width: 100%; height: 220px;">
      <canvas id="{canvas_id}" role="img" aria-label="{name}: {', '.join(f'{l} {v}' for l, v in zip(SHORT_LABELS, values))}"></canvas>
    </div>
  </div>''')

        scripts_js.append(f"  {canvas_id}: {values},")

    html = f'''<h2 class="sr-only">Small multiple bar charts comparing content pillar distribution across companies, with exact counts labeled on every bar.</h2>

<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
{''.join(panels_html)}
</div>

<div style="margin-top: 1rem; font-size: 12px; color: var(--text-muted); line-height: 1.6;">
  Pillars, left to right: {' · '.join(SHORT_LABELS)}.<br/>
  Slug-level classification of sitemap URLs, restricted to AI-relevant content. See methodology notes for exclusions applied.
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-datalabels/2.2.0/chartjs-plugin-datalabels.min.js"></script>
<script>
const pillarLabels = {json.dumps(SHORT_LABELS)};
const colors = {json.dumps(COLORS)};

const datasets = {{
{chr(10).join(scripts_js)}
}};

Chart.register(ChartDataLabels);

Object.keys(datasets).forEach(id => {{
  new Chart(document.getElementById(id), {{
    type: 'bar',
    data: {{
      labels: pillarLabels,
      datasets: [{{ data: datasets[id], backgroundColor: colors, borderRadius: 3, maxBarThickness: 20 }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      layout: {{ padding: {{ top: 20 }} }},
      scales: {{
        y: {{ beginAtZero: true, ticks: {{ color: '#898781', font: {{ size: 10 }} }}, grid: {{ color: '#e1e0d9' }} }},
        x: {{ grid: {{ display: false }}, ticks: {{ color: '#52514e', font: {{ size: 9 }}, maxRotation: 45, minRotation: 45 }} }}
      }},
      plugins: {{
        legend: {{ display: false }},
        datalabels: {{
          anchor: 'end', align: 'top', color: '#52514e',
          font: {{ size: 10, weight: 500 }}, formatter: (v) => v
        }},
        tooltip: {{ callbacks: {{ label: function(ctx) {{ return ctx.parsed.y + ' pieces'; }} }} }}
      }}
    }}
  }});
}});
</script>'''

    print(html)


if __name__ == '__main__':
    main()
