"""
Simplified phased electrical grid optimizer.
Uses shapefiles only (no CSVs).
Automatically detects hospital buildings and generates a Gantt chart.
"""

import geopandas as gpd
import pandas as pd
import json
import matplotlib.pyplot as plt


class WorkerScheduler:
    HOURLY_RATE = 37.5
    MAX_WORKERS = 4

    def calc_labor_cost(self, hours):
        return hours * self.HOURLY_RATE


class PhasedGridOptimizer:
    INFRA_SPECS = {
        "aérien": {"cost_m": 500, "time_m": 2},
        "semi-aérien": {"cost_m": 750, "time_m": 4},
        "fourreau": {"cost_m": 900, "time_m": 5},
    }

    HOSPITAL_AUTONOMY = 20
    SAFETY_MARGIN = 0.2
    MAX_HOSPITAL_TIME = HOSPITAL_AUTONOMY / (1 + SAFETY_MARGIN)
    PHASES = {1: 0.4, 2: 0.2, 3: 0.2, 4: 0.2}

    def __init__(self):
        self.batiments = None
        self.infras = None
        self.results = []
        self.phase_stats = {}

    def load_data(self, batiments_path, infras_path):
        print("Loading shapefiles...")
        self.batiments = gpd.read_file(batiments_path)
        self.infras = gpd.read_file(infras_path)
        print(f"Loaded {len(self.batiments)} buildings, {len(self.infras)} infrastructures.\n")

    def get_specs(self, infra_type):
        return self.INFRA_SPECS.get(infra_type, self.INFRA_SPECS["aérien"])

    def calc_costs(self, avg_distance=50):
        print("Calculating connection costs...")
        data = []
        type_col = next((c for c in self.batiments.columns if "type" in c.lower()), None)
        house_col = next((c for c in self.batiments.columns if "maison" in c.lower() or "house" in c.lower()), None)

        for idx, b in self.batiments.iterrows():
            b_type = str(b.get(type_col) or "habitation").strip().lower()
            nb = int(b.get(house_col) or 1)
            best_cost, best_type = float("inf"), None

            for _, i in self.infras.iterrows():
                i_type = str(i.get("type_infra") or i.get("TYPE_INFRA") or "aérien").strip().lower()
                spec = self.get_specs(i_type)
                cost = avg_distance * spec["cost_m"] + avg_distance * spec["time_m"] * 37.5
                if cost < best_cost:
                    best_cost, best_type = cost, i_type

            data.append({
                "id": b.get("id_batiment") or idx,
                "type": b_type,
                "nb_maisons": nb,
                "infra_type": best_type,
                "total_cost": best_cost,
                "priority": self._priority(b_type, nb)
            })

        df = pd.DataFrame(data)
        df.sort_values("priority", ascending=False, inplace=True)
        self.results = df
        print("Costs calculated.\n")

    def _priority(self, b_type, nb):
        weights = {"hôpital": 100, "hopital": 100, "hospital": 100, "école": 50, "ecole": 50, "habitation": 10}
        return weights.get(b_type, 1) * nb

    def optimize_phases(self):
        print("Assigning buildings to phases...\n")
        hospital_mask = self.results["type"].apply(lambda t: any(k in t for k in ["hôpital", "hopital", "hospital"]))
        hospital = self.results[hospital_mask]
        others = self.results[~hospital_mask]
        total_cost = others["total_cost"].sum()

        if not hospital.empty:
            print(f"→ Phase 0: {len(hospital)} hospital(s) connected first.")
            self.results.loc[hospital.index, "phase"] = 0
        else:
            print("⚠️ No hospital found (check shapefile type labels).")

        others = others.copy()
        others["phase"] = None
        for phase, pct in self.PHASES.items():
            limit = total_cost * pct
            subset = others[others["phase"].isna()]
            chosen = subset[subset["total_cost"].cumsum() <= limit]
            self.results.loc[chosen.index, "phase"] = phase
            others = others.drop(chosen.index)
            print(f"→ Phase {phase}: {len(chosen)} buildings ({pct*100:.0f}% cost)")
        print("\nPhases assigned.\n")

    def summarize(self):
        print("Generating phase statistics...\n")
        stats = []
        for phase in sorted(self.results["phase"].dropna().unique()):
            subset = self.results[self.results["phase"] == phase]
            s = {
                "phase": int(phase),
                "nb_buildings": int(len(subset)),
                "nb_houses": int(subset["nb_maisons"].sum()),
                "total_cost": float(subset["total_cost"].sum()),
                "infra_types": dict(subset["infra_type"].value_counts()),
                "types": dict(subset["type"].value_counts())
            }
            stats.append(s)
            print(f"Phase {phase}: {s['nb_buildings']} buildings, {s['total_cost']:.2f} €")
        self.phase_stats = stats
        print("\nSummary complete.\n")

    def export(self):
        print("Exporting results...")
        self.results.to_csv("phased_connection_plan.csv", index=False)
        pd.DataFrame(self.phase_stats).to_csv("phase_statistics.csv", index=False)

        def to_serializable(obj):
            if isinstance(obj, (pd.Series, pd.DataFrame)):
                return obj.to_dict()
            if hasattr(obj, "item"):
                try:
                    return obj.item()
                except Exception:
                    return str(obj)
            if isinstance(obj, (dict, list)):
                if isinstance(obj, dict):
                    return {k: to_serializable(v) for k, v in obj.items()}
                else:
                    return [to_serializable(v) for v in obj]
            return obj

        clean_stats = to_serializable(self.phase_stats)
        with open("phased_optimization_summary.json", "w", encoding="utf-8") as f:
            json.dump(clean_stats, f, indent=2, ensure_ascii=False)
        print("✓ CSV + JSON exported.\n")

    # ------------- NEW -------------
    def plot_gantt(self):
        print("Generating Gantt chart...")
        df = pd.DataFrame(self.phase_stats)
        phases = df["phase"].tolist()
        counts = df["nb_buildings"].tolist()
        labels = [f"Phase {p}" for p in phases]
        durations = [c / max(counts) * 10 for c in counts]  # fake proportional durations

        fig, ax = plt.subplots(figsize=(8, 4))
        start = 0
        for label, dur in zip(labels, durations):
            ax.barh(0, dur, left=start, height=0.4, label=label)
            start += dur
        ax.set_yticks([])
        ax.set_xlabel("Temps (unités fictives)")
        ax.legend()
        plt.title("Phases de construction du raccordement électrique")
        plt.tight_layout()
        plt.savefig("phased_timeline.png", dpi=150)
        plt.close()
        print("✓ Gantt chart saved as 'phased_timeline.png'\n")


def main():
    print("=" * 60)
    print("PHASED ELECTRICAL GRID OPTIMIZER (SHAPEFILES)")
    print("=" * 60)
    optimizer = PhasedGridOptimizer()
    optimizer.load_data(
        "/Users/asmae/Downloads/projet/data/batiments.shp",
        "/Users/asmae/Downloads/projet/data/infrastructures.shp"
    )
    optimizer.calc_costs(avg_distance=50)
    optimizer.optimize_phases()
    optimizer.summarize()
    optimizer.export()
    optimizer.plot_gantt()
    print("=" * 60)
    print("✅ OPTIMIZATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
