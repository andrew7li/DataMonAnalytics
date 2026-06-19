import os
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

ROOT_DIR = Path(__file__).resolve().parents[2]

DATASETS = {
    "sv": ROOT_DIR / "data" / "processed" / "sv_modeling_dataset.csv",
    "ex_era": ROOT_DIR / "data" / "processed" / "ex_era_dataset.csv",
    "sv_pricecharting": ROOT_DIR / "data" / "processed" / "sv_pricecharting_sales_graded_clean.csv",
}

OUTPUT_DIRS = {
    "sv": ROOT_DIR / "analysis" / "outputs" / "sv",
    "ex_era": ROOT_DIR / "analysis" / "outputs" / "ex_era",
    "sv_pricecharting": ROOT_DIR / "analysis" / "outputs" / "sv_pricecharting",
}

client_origin = os.environ.get("CLIENT_ORIGIN", "http://localhost:5173")

app = FastAPI(title="DataMonAnalysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[client_origin],
    allow_methods=["GET"],
    allow_headers=["content-type"],
)


@app.get("/", response_class=PlainTextResponse)
def health() -> str:
    return "BACKEND IS HEALTHY"


@app.get("/datasets")
def list_datasets() -> list[str]:
    return list(DATASETS.keys())


@app.get("/datasets/{name}")
def get_dataset(name: str, limit: int = 100, offset: int = 0):
    path = DATASETS.get(name)
    if path is None or not path.exists():
        raise HTTPException(status_code=404, detail=f"Unknown dataset: {name}")

    df = pd.read_csv(path)
    page = df.iloc[offset : offset + limit]
    return {
        "total": len(df),
        "limit": limit,
        "offset": offset,
        "rows": page.where(pd.notnull(page), None).to_dict(orient="records"),
    }


@app.get("/outputs/{dataset}/{kind}", response_class=PlainTextResponse)
def get_output(dataset: str, kind: str) -> str:
    out_dir = OUTPUT_DIRS.get(dataset)
    if out_dir is None:
        raise HTTPException(status_code=404, detail=f"Unknown dataset: {dataset}")

    path = out_dir / f"{kind}_output.txt"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No {kind} output for {dataset}")

    return path.read_text()


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
