# Paper2All installation

## Requirements

- Python 3.11
- Conda or venv
- LibreOffice (document conversion)
- Poppler (`pdftoppm`, `pdfinfo`)
- OpenAI API key (or compatible endpoint per Paper2All docs)
- Optional: NVIDIA GPU (48GB) for talking-head video only

## Install

```bash
git clone https://github.com/YuhangChen1/Paper2All.git
cd Paper2All
conda create -n paper2all python=3.11
conda activate paper2all
pip install -r requirements.txt
```

## Environment

Create `.env` in the Paper2All root:

```
OPENAI_API_KEY=your_key_here
```

Do not commit `.env`. Do not paste keys in chat logs.

## Verify

```bash
python -c "import openai; print('ok')"
which pdflatex   # if using LaTeX inputs
```

## macOS notes

```bash
brew install poppler
brew install --cask libreoffice
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| LaTeX parse fails | Compile `main.tex` locally first; fix missing figures |
| Low-res figures | Use PDF/SVG figures; 300 DPI for raster |
| API errors | Check key, balance, rate limits |
| Video fails | Ensure disk space; try `pipeline_light.py` without talking-head |
