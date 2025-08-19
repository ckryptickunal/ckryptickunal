- 👋 Hi, I’m @ckryptickunal
- 👀 I’m interested in content creation.
- 🌱 I’m currently learning Designing.  
- 💞️ I’m looking to collaborate on projects based on designing or marketing in general.
- 📫 to reach me mail @ ckryptickunal@gmail.com

<!---
ckryptickunal/ckryptickunal is a ✨ special ✨ repository because its `README.md` (this file) appears on your GitHub profile.
You can click the Preview link to take a look at your changes.
--->

## App Usage Monitor

A lightweight Linux/X11-focused monitor that logs the currently active application and generates a weekday/hour heatmap of your usage.

### Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the monitor

```bash
python cli.py monitor --db ./usage.db --poll 1.0
```
Keep it running in the background while you work. It records a new event whenever your active window changes.

### Generate a heatmap

```bash
python cli.py heatmap --db ./usage.db --out ./heatmap.png --since 7d
```
- `--since` accepts formats like `7d`, `24h`, or `YYYY-MM-DD`.
- `--until` can set an end date; defaults to now.

The output is a heatmap PNG showing minutes of focus per weekday/hour.
