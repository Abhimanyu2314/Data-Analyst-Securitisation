
"""
Securitisation AI Risk Analyst Agent
Uses auto-loan securitisation datasets to generate ECL, DPD, vintage, collection,
loss, and early-warning analytics.

Run:
python src/securitisation_ai_agent.py --data-dir data --output-dir outputs
"""

import argparse
import json
from pathlib import Path
import pandas as pd
import numpy as np


def read_csv(path):
    p = Path(path)
    if not p.exists():
        print(f"WARNING: Missing file: {p}")
        return pd.DataFrame()
    return pd.read_csv(p)


def safe_sum(df, col):
    return float(df[col].sum()) if not df.empty and col in df.columns else 0.0


def safe_mean(df, col):
    return float(df[col].mean()) if not df.empty and col in df.columns else 0.0


def risk_band(score):
    if score < 40:
        return "LOW RISK"
    if score < 70:
        return "MEDIUM RISK"
    return "HIGH RISK"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    loans = read_csv(data_dir / "auto_loan_securitisation_data.csv")
    dpd = read_csv(data_dir / "dpd_snapshot_history.csv")
    monthly = read_csv(data_dir / "dynamic_loss_monthly.csv")
    vintage = read_csv(data_dir / "static_pool_vintage_data.csv")

    # Core portfolio metrics
    total_current_balance = safe_sum(loans, "CurrentBalance")
    total_ecl = safe_sum(loans, "ECL_Provision")
    total_ead = safe_sum(loans, "EAD")
    loan_count = int(len(loans))
    avg_pd = safe_mean(loans, "PD_Estimate")
    avg_lgd = safe_mean(loans, "LGD_Estimate")
    avg_cibil = safe_mean(loans, "CIBIL_Score_Current")
    avg_ltv = safe_mean(loans, "LTV_Current")
    default_count = int(loans["IsDefaulted"].sum()) if "IsDefaulted" in loans.columns else 0

    # DPD metrics from latest snapshot
    latest_dpd = pd.DataFrame()
    if not dpd.empty and "SnapshotDate" in dpd.columns:
        dpd["SnapshotDate"] = pd.to_datetime(dpd["SnapshotDate"], errors="coerce")
        latest_date = dpd["SnapshotDate"].max()
        latest_dpd = dpd[dpd["SnapshotDate"] == latest_date].copy()
    else:
        latest_date = None

    dpd30_balance = latest_dpd.loc[latest_dpd.get("DPD_Days", pd.Series(dtype=float)) >= 30, "CurrentBalance"].sum() if not latest_dpd.empty and "DPD_Days" in latest_dpd.columns else 0
    dpd60_balance = latest_dpd.loc[latest_dpd.get("DPD_Days", pd.Series(dtype=float)) >= 60, "CurrentBalance"].sum() if not latest_dpd.empty and "DPD_Days" in latest_dpd.columns else 0
    dpd90_balance = latest_dpd.loc[latest_dpd.get("DPD_Days", pd.Series(dtype=float)) >= 90, "CurrentBalance"].sum() if not latest_dpd.empty and "DPD_Days" in latest_dpd.columns else 0
    latest_balance = safe_sum(latest_dpd, "CurrentBalance")

    dpd30_rate = dpd30_balance / latest_balance if latest_balance else 0
    dpd60_rate = dpd60_balance / latest_balance if latest_balance else 0
    dpd90_rate = dpd90_balance / latest_balance if latest_balance else 0

    # Monthly performance
    avg_collection_eff = safe_mean(monthly, "CollectionEfficiency")
    avg_default_rate = safe_mean(monthly, "MonthlyDefaultRate")
    avg_net_loss_rate = safe_mean(monthly, "MonthlyNetLossRate")
    latest_eop_balance = float(monthly["EOP_Balance"].iloc[-1]) if not monthly.empty and "EOP_Balance" in monthly.columns else 0

    # Vintage metrics
    worst_vintage = "Not available"
    worst_vintage_loss_rate = 0.0
    if not vintage.empty and "VintageID" in vintage.columns and "CumulativeNetLossRate" in vintage.columns:
        vint_summary = vintage.groupby("VintageID", as_index=False)["CumulativeNetLossRate"].max()
        row = vint_summary.sort_values("CumulativeNetLossRate", ascending=False).iloc[0]
        worst_vintage = str(row["VintageID"])
        worst_vintage_loss_rate = float(row["CumulativeNetLossRate"])
        vint_summary.to_csv(output_dir / "vintage_loss_summary.csv", index=False)

    # IFRS9 stage summary
    if not loans.empty and "IFRS9_Stage" in loans.columns:
        stage_summary = loans.groupby("IFRS9_Stage", as_index=False).agg(
            Loan_Count=("LoanID", "count"),
            Current_Balance=("CurrentBalance", "sum"),
            ECL_Provision=("ECL_Provision", "sum"),
            Avg_PD=("PD_Estimate", "mean"),
            Avg_LGD=("LGD_Estimate", "mean")
        )
        stage_summary.to_csv(output_dir / "ifrs9_stage_summary.csv", index=False)
    else:
        stage_summary = pd.DataFrame()

    # Region/servicer summaries
    if not loans.empty and "Region" in loans.columns:
        loans.groupby("Region", as_index=False).agg(
            Current_Balance=("CurrentBalance", "sum"),
            ECL_Provision=("ECL_Provision", "sum"),
            Avg_PD=("PD_Estimate", "mean"),
            Avg_CIBIL=("CIBIL_Score_Current", "mean")
        ).to_csv(output_dir / "region_risk_summary.csv", index=False)

    if not loans.empty and "ServicerName" in loans.columns:
        loans.groupby("ServicerName", as_index=False).agg(
            Current_Balance=("CurrentBalance", "sum"),
            ECL_Provision=("ECL_Provision", "sum"),
            Avg_PD=("PD_Estimate", "mean"),
            Avg_CIBIL=("CIBIL_Score_Current", "mean")
        ).to_csv(output_dir / "servicer_risk_summary.csv", index=False)

    # Simple risk score: DPD + ECL + PD + loss + collection weakness
    ecl_rate = total_ecl / total_ead if total_ead else 0
    risk_score = round(
        min(dpd30_rate * 1000, 25)
        + min(ecl_rate * 500, 25)
        + min(avg_pd * 500, 20)
        + min(avg_net_loss_rate * 2500, 15)
        + min(max(0, 1 - avg_collection_eff) * 50, 15)
    )
    band = risk_band(risk_score)

    payload = {
        "Portfolio": {
            "Loan_Count": loan_count,
            "Current_Balance": total_current_balance,
            "EAD": total_ead,
            "ECL_Provision": total_ecl,
            "ECL_Rate": ecl_rate,
            "Default_Count": default_count,
            "Average_PD": avg_pd,
            "Average_LGD": avg_lgd,
            "Average_CIBIL": avg_cibil,
            "Average_LTV": avg_ltv,
        },
        "DPD": {
            "Latest_Snapshot_Date": str(latest_date.date()) if latest_date is not None else "Not available",
            "DPD30_Balance": float(dpd30_balance),
            "DPD60_Balance": float(dpd60_balance),
            "DPD90_Balance": float(dpd90_balance),
            "DPD30_Rate": float(dpd30_rate),
            "DPD60_Rate": float(dpd60_rate),
            "DPD90_Rate": float(dpd90_rate),
        },
        "Monthly_Performance": {
            "Average_Collection_Efficiency": avg_collection_eff,
            "Average_Monthly_Default_Rate": avg_default_rate,
            "Average_Monthly_Net_Loss_Rate": avg_net_loss_rate,
            "Latest_EOP_Balance": latest_eop_balance,
        },
        "Vintage": {
            "Worst_Vintage": worst_vintage,
            "Worst_Vintage_Cumulative_Net_Loss_Rate": worst_vintage_loss_rate,
        },
        "Risk_Score": risk_score,
        "Risk_Band": band,
    }

    interpretation = (
        f"The securitisation portfolio contains {loan_count:,} auto loans with current balance INR "
        f"{total_current_balance:,.0f}. Total ECL provision is INR {total_ecl:,.0f}, implying an ECL rate of "
        f"{ecl_rate:.2%}. Latest DPD30+ balance rate is {dpd30_rate:.2%}, DPD60+ is {dpd60_rate:.2%}, "
        f"and DPD90+ is {dpd90_rate:.2%}. Average collection efficiency is {avg_collection_eff:.2f}. "
        f"The worst vintage is {worst_vintage} with peak cumulative net loss rate of {worst_vintage_loss_rate:.2%}. "
        f"The AI risk score is {risk_score}/100, classified as {band}."
    )
    payload["AI_Interpretation"] = interpretation

    # Save outputs
    with open(output_dir / "securitisation_ai_summary.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    pd.DataFrame([{
        "Loan_Count": loan_count,
        "Current_Balance": total_current_balance,
        "ECL_Provision": total_ecl,
        "ECL_Rate": ecl_rate,
        "DPD30_Rate": dpd30_rate,
        "DPD60_Rate": dpd60_rate,
        "DPD90_Rate": dpd90_rate,
        "Average_Collection_Efficiency": avg_collection_eff,
        "Worst_Vintage": worst_vintage,
        "Risk_Score": risk_score,
        "Risk_Band": band,
    }]).to_csv(output_dir / "executive_risk_summary.csv", index=False)

    report = f"""# Securitisation AI Risk Analyst Report

## Executive AI Interpretation
{interpretation}

## Portfolio Metrics
- Loan Count: {loan_count:,}
- Current Balance: INR {total_current_balance:,.0f}
- EAD: INR {total_ead:,.0f}
- ECL Provision: INR {total_ecl:,.0f}
- ECL Rate: {ecl_rate:.2%}
- Average PD: {avg_pd:.2%}
- Average LGD: {avg_lgd:.2%}
- Average CIBIL: {avg_cibil:.0f}
- Average LTV: {avg_ltv:.2%}

## DPD Risk
- Latest Snapshot: {payload['DPD']['Latest_Snapshot_Date']}
- DPD30+ Rate: {dpd30_rate:.2%}
- DPD60+ Rate: {dpd60_rate:.2%}
- DPD90+ Rate: {dpd90_rate:.2%}

## Monthly Performance
- Average Collection Efficiency: {avg_collection_eff:.2f}
- Average Monthly Default Rate: {avg_default_rate:.2%}
- Average Monthly Net Loss Rate: {avg_net_loss_rate:.2%}

## Vintage Performance
- Worst Vintage: {worst_vintage}
- Worst Vintage Cumulative Net Loss Rate: {worst_vintage_loss_rate:.2%}

## Recommendation
Monitor DPD roll-rates, Stage 2 exposure, high-LTV borrowers, weak servicers, and deteriorating vintage cohorts. Use the Power BI dashboard for executive reporting and the Python agent for repeatable portfolio-risk assessment.
"""
    (output_dir / "Securitisation_AI_Risk_Report.md").write_text(report, encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print("\nGenerated:")
    print(output_dir / "securitisation_ai_summary.json")
    print(output_dir / "executive_risk_summary.csv")
    print(output_dir / "Securitisation_AI_Risk_Report.md")


if __name__ == "__main__":
    main()
