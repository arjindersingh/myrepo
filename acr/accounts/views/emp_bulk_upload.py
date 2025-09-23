# views_employee_bulk.py
import csv
import io
from typing import Iterable, Tuple, List, Dict, Any, Optional
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.text import slugify

from accounts.forms.emp_bulk_upload import EmployeeBulkUploadForm
from accounts.models.employee import Employee, JobCategory, JobPost, EmploymentStatus
from accounts.models.institute import Institute, Department, Subject, Wing

# ---------- Utility helpers ----------

def _norm_header(h: str) -> str:
    return (h or "").strip().lower()

def _split_vals(s: Optional[str], sep: str) -> List[str]:
    if not s:
        return []
    return [v.strip() for v in str(s).split(sep) if str(v).strip()]

def _get_by_ids_or_names(
    Model, 
    ids: Iterable[str], 
    names: Iterable[str], 
    create_missing: bool
) -> Tuple[List[Any], List[str]]:
    """
    Resolve M2M values by IDs and/or names. Returns (objects, errors).
    """
    objs = []
    errors = []

    # IDs
    for raw_id in ids:
        try:
            obj = Model.objects.get(pk=int(raw_id))
            objs.append(obj)
        except (ValueError, Model.DoesNotExist):
            errors.append(f"{Model.__name__} id '{raw_id}' not found")

    # Names (case-insensitive exact match on 'name' or 'title' or 'display_name')
    # Adjust these fields based on your related models
    name_fields = ["name", "title", "display_name", "institute_name", "dept_name", "subject_name", "post_name", "wing_name"]
    for n in names:
        q = None
        for field in name_fields:
            if field in [f.name for f in Model._meta.fields]:
                q = {field + "__iexact": n}
                try:
                    obj = Model.objects.get(**q)
                    objs.append(obj)
                    break
                except Model.DoesNotExist:
                    continue
        else:
            if create_missing:
                # Pick first available name-like field to populate
                create_kwargs = {}
                for field in name_fields:
                    if field in [f.name for f in Model._meta.fields]:
                        create_kwargs[field] = n
                        break
                if not create_kwargs:
                    errors.append(f"Cannot create {Model.__name__} for '{n}' (no suitable name field).")
                else:
                    obj = Model.objects.create(**create_kwargs)
                    objs.append(obj)
            else:
                errors.append(f"{Model.__name__} name '{n}' not found")

    # dedupe
    seen = set()
    unique_objs = []
    for o in objs:
        if o.pk not in seen:
            unique_objs.append(o)
            seen.add(o.pk)
    return unique_objs, errors

def _resolve_fk(Model, id_val: Optional[str], name_val: Optional[str], create_missing: bool):
    """
    Resolve a FK either by id or name-like fields. Returns (object_or_none, error_or_none).
    """
    if id_val:
        try:
            return Model.objects.get(pk=int(id_val)), None
        except (ValueError, Model.DoesNotExist):
            return None, f"{Model.__name__} id '{id_val}' not found"

    if name_val:
        name_fields = ["name", "title", "display_name", "status_name"]
        for field in name_fields:
            if field in [f.name for f in Model._meta.fields]:
                try:
                    return Model.objects.get(**{field + "__iexact": name_val}), None
                except Model.DoesNotExist:
                    continue
        if create_missing:
            # create on first matching field
            for field in name_fields:
                if field in [f.name for f in Model._meta.fields]:
                    obj = Model.objects.create(**{field: name_val})
                    return obj, None
        return None, f"{Model.__name__} name '{name_val}' not found"

    return None, None  # optional FK

# ---------- The main upload view ----------

def employee_bulk_upload(request):
    """
    Upload a CSV to create/update Employees, with M2M resolution via IDs or Names.
    Shows a preview in dry-run mode; commits if dry_run is False and no errors.
    """
    if request.method == "POST":
        form = EmployeeBulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data["csv_file"]
            dry_run = form.cleaned_data["dry_run"]
            update_existing = form.cleaned_data["update_existing"]
            create_missing_related = form.cleaned_data["create_missing_related"]
            list_sep = form.cleaned_data["delimiter"]

            try:
                data = csv_file.read().decode("utf-8-sig")
            except UnicodeDecodeError:
                data = csv_file.read().decode("latin-1")

            reader = csv.DictReader(io.StringIO(data))
            headers = [_norm_header(h) for h in reader.fieldnames or []]
            if "emp_code" not in headers:
                messages.error(request, "CSV must include 'emp_code' column.")
                return render(request, "employees/employee_bulk_upload.html", {"form": form})

            results: List[Dict[str, Any]] = []
            any_errors = False

            # transactional write only when not dry-run and no errors
            with transaction.atomic():
                savepoint = transaction.savepoint()

                for idx, row in enumerate(reader, start=2):  # header is line 1
                    row_norm = { _norm_header(k): (v or "").strip() for k, v in row.items() }
                    line_errors = []

                    # Required
                    emp_code = row_norm.get("emp_code")
                    emp_name = row_norm.get("emp_name") or ""
                    if not emp_code:
                        line_errors.append("emp_code is required")

                    # Parse ints
                    emp_code_int = None
                    if emp_code:
                        try:
                            emp_code_int = int(emp_code)
                            if emp_code_int < 0 or emp_code_int > 99999:
                                line_errors.append("emp_code must be 0..99999")
                        except ValueError:
                            line_errors.append("emp_code must be an integer")

                    # FK EmploymentStatus
                    es_id = row_norm.get("employment_status_id")
                    es_name = row_norm.get("employment_status_name")
                    employment_status, es_err = _resolve_fk(EmploymentStatus, es_id, es_name, create_missing_related)
                    if es_err:
                        line_errors.append(es_err)

                    # Resolve M2Ms
                    # job_categories
                    jc_ids = _split_vals(row_norm.get("job_categories_ids"), list_sep)
                    jc_names = _split_vals(row_norm.get("job_categories_names"), list_sep)
                    job_categories, errs = _get_by_ids_or_names(JobCategory, jc_ids, jc_names, create_missing_related)
                    line_errors.extend(errs)

                    # institutes
                    inst_ids = _split_vals(row_norm.get("institutes_ids"), list_sep)
                    inst_names = _split_vals(row_norm.get("institutes_names"), list_sep)
                    institutes, errs = _get_by_ids_or_names(Institute, inst_ids, inst_names, create_missing_related)
                    line_errors.extend(errs)

                    # departments
                    dept_ids = _split_vals(row_norm.get("departments_ids"), list_sep)
                    dept_names = _split_vals(row_norm.get("departments_names"), list_sep)
                    departments, errs = _get_by_ids_or_names(Department, dept_ids, dept_names, create_missing_related)
                    line_errors.extend(errs)

                    # teaching_posts
                    jp_ids = _split_vals(row_norm.get("teaching_posts_ids"), list_sep)
                    jp_names = _split_vals(row_norm.get("teaching_posts_names"), list_sep)
                    teaching_posts, errs = _get_by_ids_or_names(JobPost, jp_ids, jp_names, create_missing_related)
                    line_errors.extend(errs)

                    # subjects
                    sub_ids = _split_vals(row_norm.get("subjects_ids"), list_sep)
                    sub_names = _split_vals(row_norm.get("subjects_names"), list_sep)
                    subjects, errs = _get_by_ids_or_names(Subject, sub_ids, sub_names, create_missing_related)
                    line_errors.extend(errs)

                    # wings
                    wing_ids = _split_vals(row_norm.get("wings_ids"), list_sep)
                    wing_names = _split_vals(row_norm.get("wings_names"), list_sep)
                    wings, errs = _get_by_ids_or_names(Wing, wing_ids, wing_names, create_missing_related)
                    line_errors.extend(errs)

                    action = None
                    employee_obj = None

                    if not line_errors and emp_code_int is not None:
                        # create/update by emp_code
                        try:
                            employee_obj = Employee.objects.get(emp_code=emp_code_int)
                            if update_existing:
                                employee_obj.emp_name = emp_name or employee_obj.emp_name
                                employee_obj.employment_status = employment_status
                                employee_obj.save()
                                action = "updated"
                            else:
                                line_errors.append(f"emp_code {emp_code_int} already exists; updates disabled")
                        except Employee.DoesNotExist:
                            # Create new
                            employee_obj = Employee.objects.create(
                                emp_code=emp_code_int,
                                emp_name=emp_name or f"Emp-{emp_code_int}",
                                employment_status=employment_status
                            )
                            action = "created"

                        # set M2Ms only if we have an object and no errors
                        if employee_obj and not line_errors:
                            # Replace sets; if you prefer additive, change to add(...)
                            employee_obj.job_categories.set([o.pk for o in job_categories])
                            employee_obj.institutes.set([o.pk for o in institutes])
                            employee_obj.departments.set([o.pk for o in departments])
                            employee_obj.teaching_posts.set([o.pk for o in teaching_posts])
                            employee_obj.subjects.set([o.pk for o in subjects])
                            employee_obj.wings.set([o.pk for o in wings])

                    # Collect result
                    row_result = {
                        "line": idx,
                        "emp_code": emp_code,
                        "emp_name": emp_name,
                        "action": action if not line_errors else "error",
                        "errors": line_errors,
                    }
                    results.append(row_result)
                    if line_errors:
                        any_errors = True

                # Rollback if dry-run or errors
                if dry_run or any_errors:
                    transaction.savepoint_rollback(savepoint)
                else:
                    transaction.savepoint_commit(savepoint)

            context = {
                "form": form,
                "results": results,
                "dry_run": dry_run,
                "any_errors": any_errors,
            }
            if any_errors:
                messages.error(request, "Some rows have errors. Nothing was saved.")
            else:
                if dry_run:
                    messages.info(request, "Dry-run successful. No errors found. Re-upload with Dry-run off to commit.")
                else:
                    messages.success(request, "Employees imported successfully.")
            return render(request, "employee/bulk_upload_result.html", context)

    else:
        form = EmployeeBulkUploadForm()

    return render(request, "employee/bulk_upload.html", {"form": form})
