# LNMD Macro Calculator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/lnmd-macro-calculator.svg?style=social&label=Star&maxAge=2592000)](https://github.com/yourusername/lnmd-macro-calculator/stargazers/)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/lnmd-macro-calculator.svg)](https://github.com/yourusername/lnmd-macro-calculator/issues)

A free, open-source macro calculator built as part of the LNMD Hub—an altruistic initiative to combat the global obesity crisis by providing accessible nutrition and training tools for everyone, from beginners to elite athletes like CrossFit Games competitors.

Powered by evidence-based science (e.g., Katch-McArdle BMR, MET values from Compendium of Physical Activities), this tool optimizes daily macros with personalized partitioning, supporting goals like weight loss, muscle gain, and athletic performance.

## Why This Tool?
In 2025, over 1 billion people face obesity (WHO data), yet premium apps lock features behind paywalls. This calculator is free, ad-free, privacy-focused (no data collection), and designed for real impact—e.g., nutrient timing for recovery in high-intensity training.

## Features
- **Personalized Macro Calculation**: Input weight, body fat %, steps, exercise hours (hybrid training support), wake/sleep times, and goals. Outputs calories, protein (total weight-based), fats (lean mass-based), carbs.
- **Goal-Specific Adjustments**: Maintain, Recomposition (5% deficit), Moderate Weight Loss (15% deficit), Aggressive Loss (30%), Aggressive Gain (20% surplus), Athletic Performance (10% surplus).
- **Hybrid Training**: Add multiple types (e.g., HIIT + Weightlifting) with MET-based energy estimates.
- **Daily Timeline Partitioning**: Custom wake/sleep and session times (dropdowns for 00:00-23:00) create a chronological macro breakdown (pre/intra/post-workout + other meals), optimized by goal (e.g., higher carbs for performance).
- **Beta Meal Planner**: Simple suggestions based on macros.
- **PWA-Ready**: Install as an app for offline/mobile use (add manifest.json/sw.js as guided).
- **Ethical Design**: Science-backed (citations in code comments), warnings for professional advice.

## Installation/Setup
No install needed—run in browser! For local/dev:
1. Clone repo: `git clone https://github.com/yourusername/lnmd-macro-calculator.git`
2. Open `index.html` in a browser (or use Live Server extension in VS Code).
3. For PWA: Add manifest.json and sw.js (code in docs), then host on GitHub Pages.

### Deployment (Live Site)
- Enable GitHub Pages in repo Settings > Pages > Branch: main, Folder: / (root).
- Access at: https://yourusername.github.io/lnmd-macro-calculator

## Usage
1. Fill inputs: Wake/sleep (dropdowns), weight, body fat, steps, training (add types), sessions/times, goal, protein/fat levels.
2. Click "Calculate" for macros, breakdown, timeline, and meal ideas.
3. Example: For a 90kg athlete (8% body fat, 10k steps, 20h/week HIIT/Weights, wake 6:00/sleep 22:00, performance goal, high protein/moderate fat):
   - Outputs ~3500kcal, 198g protein, 400g carbs, 100g fats, timed meals (e.g., 5am pre-workout: 30g protein/80g carbs).

**Tips**: Adjust for negative carbs by increasing activity/lowering macros. Consult a doctor for health advice.

## Contributing
Help build the hub! Fork, create branch (`git checkout -b feature/new`), commit (`git commit -m 'Add feature'`), push (`git push origin feature/new`), open PR. Issues/PRs welcome—e.g., add recipe API or multilingual support.

## License
MIT License—free to use/modify/share. See [LICENSE](LICENSE) for details.

## Acknowledgments
- Built with Tailwind CSS for UI.
- Inspired by Mifflin-St Jeor/Katch-McArdle equations and MET data from scientific sources.
- Part of the LNMD Hub: Join the mission against obesity—star/share to spread!

Questions? Open an issue or DM on X. Let's make health accessible! - DLL.
