from django.db.models import Max, Avg, Sum, Count, F, Value, Case, When, FloatField, OuterRef, Subquery

from django.shortcuts import render
from appraisal.forms.consolidated_report import AppraisalConsolidatedReportForm
from appraisal.models.appraisal_data import TotalAppraisalData
from accounts.models.employee import Employee
from appraisal.models.appraisal_type import AppraisalType
from accounts.context_processors import current_academic_year


# ---------- helpers (strategy functions) ----------
def _latest_qs(base_qs):
    latest_no_sq = (
        TotalAppraisalData.objects
        .filter(
            appraisal_year=OuterRef("appraisal_year"),
            employee=OuterRef("employee"),
            appraisal_type=OuterRef("appraisal_type"),
        )
        .values("employee_id", "appraisal_type_id", "appraisal_year_id")
        .annotate(m=Max("appraisal_no"))
        .values("m")[:1]
    )
    return (
        base_qs
        .annotate(lat_no=Subquery(latest_no_sq))
        .filter(appraisal_no=F("lat_no"))
        .select_related("employee", "appraisal_type", "emp_institute", "emp_job_category")
    )


def method_latest_obt_max(base_qs):
    qs = _latest_qs(base_qs)

    cell = {}
    sum_by_emp = {}
    for row in qs:
        key = (row.employee_id, row.appraisal_type_id)
        cell[key] = {"text": f"{row.obt_score} / {row.max_score}", "subtext": f"Appraisal #{row.appraisal_no}"}
        # totals as ΣObt / ΣMax across latest rows
        s = sum_by_emp.setdefault(row.employee_id, {"obt": 0.0, "max": 0.0})
        s["obt"] += float(row.obt_score or 0)
        s["max"] += float(row.max_score or 0)

    row_totals = {}
    for emp_id, s in sum_by_emp.items():
        row_totals[emp_id] = {"text": f"{s['obt']} / {s['max']}", "subtext": "Σ latest"}

    emp_ids = list(qs.values_list("employee_id", flat=True).distinct())
    type_ids = list(qs.values_list("appraisal_type_id", flat=True).distinct())
    return cell, emp_ids, type_ids, row_totals


def method_latest_pct(base_qs, places=2):
    qs = _latest_qs(base_qs)

    cell = {}
    sum_by_emp = {}
    for row in qs:
        pct = (row.obt_score / row.max_score * 100.0) if row.max_score else 0.0
        cell[(row.employee_id, row.appraisal_type_id)] = {
            "text": f"{pct:.{places}f}",
            "subtext": f"Appraisal #{row.appraisal_no}",
        }
        s = sum_by_emp.setdefault(row.employee_id, {"obt": 0.0, "max": 0.0})
        s["obt"] += float(row.obt_score or 0)
        s["max"] += float(row.max_score or 0)

    # Row total = overall % = ΣObt / ΣMax × 100 across latest rows
    row_totals = {}
    for emp_id, s in sum_by_emp.items():
        overall = (s["obt"] / s["max"] * 100.0) if s["max"] else 0.0
        row_totals[emp_id] = {"text": f"{overall:.{places}f}", "subtext": "Overall (latest)"}

    emp_ids = list(qs.values_list("employee_id", flat=True).distinct())
    type_ids = list(qs.values_list("appraisal_type_id", flat=True).distinct())
    return cell, emp_ids, type_ids, row_totals


def method_avg_pct_all(base_qs, places=2):
    # per-cell: Avg of per-appraisal percentages for that (emp, type, year)
    percent_expr = Case(
        When(max_score__gt=0, then=F("obt_score") * 100.0 / F("max_score")),
        default=Value(None),
        output_field=FloatField(),
    )
    agg = (
        base_qs
        .values("employee_id", "appraisal_type_id", "appraisal_year_id")
        .annotate(avg_pct=Avg(percent_expr), n=Count("id"))
    )

    cell = {}
    emp_ids_set, type_ids_set = set(), set()
    for row in agg:
        emp_id = row["employee_id"]; typ_id = row["appraisal_type_id"]
        emp_ids_set.add(emp_id); type_ids_set.add(typ_id)
        avg_pct = row["avg_pct"] if row["avg_pct"] is not None else 0.0
        n = row["n"]
        cell[(emp_id, typ_id)] = {"text": f"{avg_pct:.{places}f}", "subtext": f"Avg of {n}"}

    # Row total (weighted overall across ALL appraisals/types): ΣObt / ΣMax × 100
    overall = (
        base_qs.values("employee_id")
        .annotate(sum_obt=Sum("obt_score"), sum_max=Sum("max_score"))
    )
    row_totals = {}
    for r in overall:
        emp_id = r["employee_id"]
        smax = float(r["sum_max"] or 0.0)
        sobt = float(r["sum_obt"] or 0.0)
        pct = (sobt / smax * 100.0) if smax else 0.0
        row_totals[emp_id] = {"text": f"{pct:.{places}f}", "subtext": "Overall (all appraisals)"}

    return cell, list(emp_ids_set), list(type_ids_set), row_totals


def method_best_pct_all(base_qs, places=2):
    """Best % per (emp,type) across all appraisals; row total = average of best % across types."""
    percent_expr = Case(
        When(max_score__gt=0, then=F("obt_score") * 100.0 / F("max_score")),
        default=Value(None),
        output_field=FloatField(),
    )
    best = (
        base_qs
        .values("employee_id", "appraisal_type_id", "appraisal_year_id")
        .annotate(best_pct=Max(percent_expr))
    )

    cell = {}
    by_emp = {}
    emp_ids_set, type_ids_set = set(), set()
    for r in best:
        emp_id = r["employee_id"]; typ_id = r["appraisal_type_id"]
        emp_ids_set.add(emp_id); type_ids_set.add(typ_id)
        b = r["best_pct"]
        val = 0.0 if b is None else float(b)
        cell[(emp_id, typ_id)] = {"text": f"{val:.{places}f}", "subtext": "Best"}
        by_emp.setdefault(emp_id, []).append(val)

    # Row total = average of best % across types (ignoring missing)
    row_totals = {}
    for emp_id, vals in by_emp.items():
        if vals:
            row_totals[emp_id] = {"text": f"{(sum(vals)/len(vals)):.{places}f}", "subtext": "Avg of best"}
        else:
            row_totals[emp_id] = {"text": "0.00", "subtext": "Avg of best"}

    return cell, list(emp_ids_set), list(type_ids_set), row_totals



# Registry of methods (easy to extend)
METHODS = {
    "latest_obt_max": {"label": "Obt/Max (Latest)", "fn": method_latest_obt_max},
    "latest_pct":     {"label": "Percentage (Latest)", "fn": method_latest_pct},
    "avg_pct_all":    {"label": "Average % (All Appraisals)", "fn": method_avg_pct_all},
    "best_pct_all":   {"label": "Best % (All Appraisals)", "fn": method_best_pct_all},
}



def show_appraisal_consolidated_Report(request):
    CAY = current_academic_year()  # current academic year
    form = AppraisalConsolidatedReportForm(request.GET or None)

    # Base queryset: only current academic year
    base_qs = (
        TotalAppraisalData.objects.select_related(
            "employee", "appraisal_type", "emp_institute", "emp_job_category"
        )
        .filter(appraisal_year=CAY)
    )

    # Apply filters
    if form.is_valid():
        inst_qs = form.cleaned_data.get("emp_institutes")
        jc_qs = form.cleaned_data.get("emp_job_categories")
        if inst_qs and inst_qs.exists():
            base_qs = base_qs.filter(emp_institute__in=inst_qs)
        if jc_qs and jc_qs.exists():
            base_qs = base_qs.filter(emp_job_category__in=jc_qs)

    # Read method (default)
    method_key = request.GET.get("method", "latest_obt_max")
    if method_key not in METHODS:
        method_key = "latest_obt_max"
    method_label = METHODS[method_key]["label"]

    # Compute cells via strategy
    cell_display, emp_ids, type_ids, row_totals = METHODS[method_key]["fn"](base_qs)
    # Build employees/types in user-friendly order
   
    employees = list(Employee.objects.filter(id__in=emp_ids).order_by("emp_name"))
    appraisal_types = list(AppraisalType.objects.filter(id__in=type_ids).order_by("display_name", "name"))

    context = {
        "CAY": CAY,
        "form": form,
        "employees": employees,
        "appraisal_types": appraisal_types,
        "cell": cell_display,
        "row_totals": row_totals,          # NEW
        "method": method_key,
        "method_choices": [(k, v["label"]) for k, v in METHODS.items()],
        "method_label": METHODS[method_key]["label"],
    }

    return render(request, "reports/consolidated.html", context)
