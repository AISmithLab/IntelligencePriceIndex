
import pandas as pd

import numpy as np

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from pathlib import Path



np.random.seed(42)



OUT_TABLES = Path("outputs/tables")

OUT_FIGS = Path("outputs/figures")

OUT_TABLES.mkdir(parents=True, exist_ok=True)

OUT_FIGS.mkdir(parents=True, exist_ok=True)



categories = [

    "Content Writing",

    "Technical Writing",

    "Translation & Localization",

    "SEO",

    "Paid Advertising (PPC)",

    "Social Media Management",

    "Graphic Design",

    "Branding & Visual Identity",

    "UI/UX Design",

    "Video Editing",

    "Animation & Motion Graphics",

    "Audio Production & Voice Work",

    "Web Development",

    "Mobile App Development",

    "Software Engineering",

    "Cloud, DevOps & Cybersecurity",

    "Data Analytics & Business Intelligence",

    "AI Development & Automation",

    "Finance & Accounting",

    "Consulting & Legal Services",

]



months = pd.date_range("2025-06-01", "2026-06-01", freq="MS")



high_ai_exposure = {

    "Content Writing",

    "Technical Writing",

    "Translation & Localization",

    "SEO",

    "Graphic Design",

    "Data Analytics & Business Intelligence",

    "AI Development & Automation",

}



base_prices = {cat: np.random.uniform(50, 180) for cat in categories}



records = []



for month_i, month in enumerate(months):

    for cat in categories:

        for i in range(80):

            base = base_prices[cat]



            if cat in high_ai_exposure:

                trend = 1 - 0.012 * month_i

            else:

                trend = 1 + 0.004 * month_i



            noise = np.random.lognormal(mean=0, sigma=0.35)

            price = base * trend * noise



            records.append({

                "date": month,

                "month": month.strftime("%Y-%m"),

                "platform": np.random.choice(["Fiverr", "Upwork"]),

                "ipi_category": cat,

                "price": round(price, 2),

                "price_type": "mock_price"

            })



raw = pd.DataFrame(records)

raw.to_csv(OUT_TABLES / "mock_raw_records.csv", index=False)



monthly = (

    raw.groupby(["month", "ipi_category"])

    .agg(

        n_records=("price", "size"),

        median_price=("price", "median"),

        average_price=("price", "mean"),

        p25=("price", lambda x: x.quantile(0.25)),

        p75=("price", lambda x: x.quantile(0.75)),

    )

    .reset_index()

)



monthly.to_csv(OUT_TABLES / "monthly_category_prices.csv", index=False)



base_month = months[0].strftime("%Y-%m")

base = monthly[monthly["month"] == base_month][["ipi_category", "median_price"]]

base = base.rename(columns={"median_price": "base_price"})



ipi = monthly.merge(base, on="ipi_category", how="left")

ipi["price_index"] = ipi["median_price"] / ipi["base_price"] * 100



ipi = ipi.sort_values(["ipi_category", "month"])

ipi["1mo_pct_change"] = ipi.groupby("ipi_category")["price_index"].pct_change(1) * 100

ipi["12mo_pct_change"] = ipi.groupby("ipi_category")["price_index"].pct_change(12) * 100



ipi.to_csv(OUT_TABLES / "ipi_index_table.csv", index=False)



latest_month = months[-1].strftime("%Y-%m")

latest = ipi[ipi["month"] == latest_month].copy()

latest = latest[["ipi_category", "n_records", "median_price", "price_index", "12mo_pct_change"]]

latest = latest.sort_values("12mo_pct_change")

latest.to_csv(OUT_TABLES / "latest_12mo_pct_change.csv", index=False)



plt.figure(figsize=(14, 7))

plt.bar(latest["ipi_category"], latest["12mo_pct_change"])

plt.axhline(0, linewidth=1)

plt.title("12-month percentage change, Intelligence Price Index, selected categories")

plt.ylabel("12-month percentage change (%)")

plt.xlabel("IPI Category")

plt.xticks(rotation=75, ha="right")

plt.tight_layout()

plt.savefig(OUT_FIGS / "ipi_12mo_percentage_change_selected_categories.png", dpi=200)

plt.close()



selected = [

    "Content Writing",

    "Graphic Design",

    "Web Development",

    "AI Development & Automation",

    "Consulting & Legal Services",

]



plt.figure(figsize=(12, 6))

for cat in selected:

    temp = ipi[ipi["ipi_category"] == cat]

    plt.plot(temp["month"], temp["price_index"], marker="o", label=cat)



plt.axhline(100, linestyle="--", linewidth=1)

plt.title("Intelligence Price Index, selected categories")

plt.ylabel(f"Price Index, {base_month} = 100")

plt.xlabel("Month")

plt.xticks(rotation=45)

plt.legend()

plt.tight_layout()

plt.savefig(OUT_FIGS / "ipi_index_selected_categories.png", dpi=200)

plt.close()



print("Mockup created successfully.")

print("Tables saved to outputs/tables/")

print("Figures saved to outputs/figures/")

