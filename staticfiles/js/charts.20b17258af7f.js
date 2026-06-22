// Chart default styling and shadow configurations for Chart.js
if (typeof Chart !== 'undefined') {
  Chart.defaults.font.family = "'Inter', system-ui, -apple-system, sans-serif";
  Chart.defaults.plugins.tooltip.padding = 12;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;
  Chart.defaults.plugins.tooltip.backgroundColor = '#0f172a';
  
  console.log("Chart.js SaaS styling defaults applied.");
}
