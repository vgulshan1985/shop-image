# core/views.py
import os, csv, zipfile, openpyxl
from threading import Thread
from django.shortcuts import redirect, render
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .models import Manufacturer
from PIL import Image
import uuid
import threading
import traceback
import time
from django.http               import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.cache         import cache
from django.shortcuts          import redirect
import uuid
import threading
import traceback
from django.http      import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import time
from django.core.cache import cache
import uuid
from django.http import JsonResponse
import uuid
import threading
import time
from django.http import JsonResponse
from django.core.cache import cache
from django.http import JsonResponse
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pandas as pd
import os
import shutil
import zipfile
import zipfile
# ─── Standard library ──────────────────────────────────────────────────────────
# ─── Standard library ──────────────────────────────────────────────────────────
import os
import csv
import zipfile
import uuid
from datetime import datetime
from http.client import HTTPResponse
from concurrent.futures import ThreadPoolExecutor
from django.shortcuts import get_object_or_404, redirect
from .models import Manufacturer
import os
import time
import zipfile
import tempfile
import logging
from datetime import datetime
from pathlib import Path
from pdf2image import convert_from_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def manufacturer_delete(request, pk):
    if request.method == "POST" and request.user.is_staff:
        m = get_object_or_404(Manufacturer, pk=pk)
        m.delete()
    return redirect("logo_management")

def zip_directory(folder_path, output_zip_path):
    """
    Recursively zips the contents of `folder_path` into `output_zip_path`.
    """
    # Make sure the output directory exists
    os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)

    with zipfile.ZipFile(output_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                # Compute the path inside the ZIP (so that subfolders are preserved)
                rel_path = os.path.relpath(full_path, start=folder_path)
                zipf.write(full_path, arcname=rel_path)
# ─── Third‑party ────────────────────────────────────────────────────────────────
import openpyxl
from PIL import Image

# ─── Django ────────────────────────────────────────────────────────────────────
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

# ─── Local app ─────────────────────────────────────────────────────────────────
from .models import Manufacturer

from django.http import FileResponse, Http404
from django.conf import settings
import os
from django.http import FileResponse, Http404
from django.conf import settings
import os

# Create your views here.

def pdf_to_jpg(request):
    context = {}

    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Check if we need to delete a previously processed file
    if request.GET.get('delete_file'):
        file_to_delete = request.GET.get('delete_file')
        # Validate the filename to prevent directory traversal attacks
        if os.path.basename(file_to_delete) == file_to_delete and not file_to_delete.startswith('.'):
            try:
                # Delete the ZIP file
                zip_path = os.path.join(settings.MEDIA_ROOT, 'pdf_conversions', file_to_delete)
                if os.path.exists(zip_path) and os.path.isfile(zip_path):
                    os.remove(zip_path)

                # Also delete the corresponding log file
                log_name = file_to_delete.replace('converted_jpgs_', 'pdf_conversion_')
                log_name = log_name.replace('.zip', '.log')
                log_path = os.path.join(settings.MEDIA_ROOT, 'pdf_conversion_logs', log_name)
                if os.path.exists(log_path) and os.path.isfile(log_path):
                    os.remove(log_path)

                context['deleted'] = True
            except Exception as e:
                logger.error(f"Error deleting file {file_to_delete}: {str(e)}")

    if request.method == 'POST':
        start_time = time.time()

        # Get the uploaded ZIP file
        pdf_zip = request.FILES.get('pdf_zip')
        dpi = int(request.POST.get('dpi', 300))

        # Validate DPI
        if dpi < 72:
            dpi = 72
        elif dpi > 600:
            dpi = 600

        if not pdf_zip:
            context['error'] = "No ZIP file uploaded"
            return render(request, 'admin/pdf_to_jpg.html', context)

        # Create temp directories
        temp_dir = tempfile.mkdtemp()
        extract_dir = os.path.join(temp_dir, 'pdfs')
        output_dir = os.path.join(temp_dir, 'jpgs')
        os.makedirs(extract_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # Create log file
        log_path = os.path.join(settings.MEDIA_ROOT, 'pdf_conversion_logs')
        os.makedirs(log_path, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_path, f'pdf_conversion_{timestamp}.log')

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        try:
            # Extract ZIP
            with zipfile.ZipFile(pdf_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # Process PDFs
            pdf_files = [f for f in os.listdir(extract_dir) if f.lower().endswith('.pdf')]

            if not pdf_files:
                logger.error("No PDF files found in the ZIP")
                context['error'] = "No PDF files found in the ZIP"
                return render(request, 'admin/pdf_to_jpg.html', context)

            logger.info(f"Found {len(pdf_files)} PDF files to process")

            # Convert each PDF to JPG
            for pdf_file in pdf_files:
                pdf_path = os.path.join(extract_dir, pdf_file)
                output_folder = os.path.join(output_dir, os.path.splitext(pdf_file)[0])
                os.makedirs(output_folder, exist_ok=True)

                logger.info(f"Converting {pdf_file} to JPG")

                try:
                    # Convert PDF to images
                    images = convert_from_path(
                        pdf_path,
                        dpi=dpi,
                        thread_count=4  # Use multiple threads for better performance
                    )

                    # Save each page as JPG
                    for i, image in enumerate(images):
                        image_path = os.path.join(output_folder, f'page_{i+1}.jpg')
                        image.save(image_path, 'JPEG', quality=95)
                        logger.info(f"Saved {image_path}")

                except Exception as e:
                    logger.error(f"Error converting {pdf_file}: {str(e)}")

            # Create output ZIP
            output_zip_name = f'converted_jpgs_{timestamp}.zip'
            output_zip_path = os.path.join(settings.MEDIA_ROOT, 'pdf_conversions', output_zip_name)
            os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)

            with zipfile.ZipFile(output_zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, output_dir)
                        zipf.write(file_path, arcname)

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            elapsed_time_str = f"{elapsed_time:.2f} seconds"

            # Set context for template
            context['processed'] = True
            context['elapsed_time'] = elapsed_time_str
            context['zip_path'] = f'/media/pdf_conversions/{output_zip_name}'
            context['log_path'] = f'/media/pdf_conversion_logs/pdf_conversion_{timestamp}.log'
            context['file_name'] = output_zip_name  # Store filename for deletion
            context['pdf_count'] = len(pdf_files)

            logger.info(f"Processing complete. Time taken: {elapsed_time_str}")

        except Exception as e:
            logger.error(f"Error processing ZIP: {str(e)}")
            context['error'] = f"Error processing ZIP: {str(e)}"

        finally:
            # Clean up temp files
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.error(f"Error cleaning up temp files: {str(e)}")

            # Remove file handler
            logger.removeHandler(file_handler)

    # Clean up old files (older than 1 hour)
    try:
        cleanup_pdf_conversion_files()
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

    return render(request, 'admin/pdf_to_jpg.html', context)

def cleanup_pdf_conversion_files():
    """Clean up PDF conversion files older than 1 hour"""
    now = time.time()
    one_hour_ago = now - 3600  # 1 hour in seconds

    # Clean up PDF conversions
    conversions_dir = os.path.join(settings.MEDIA_ROOT, 'pdf_conversions')
    if os.path.exists(conversions_dir):
        for filename in os.listdir(conversions_dir):
            file_path = os.path.join(conversions_dir, filename)
            if os.path.isfile(file_path):
                # Check if file is older than 1 hour
                if os.path.getmtime(file_path) < one_hour_ago:
                    try:
                        os.remove(file_path)
                        logger.info(f"Deleted old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting {file_path}: {str(e)}")

    # Clean up logs
    logs_dir = os.path.join(settings.MEDIA_ROOT, 'pdf_conversion_logs')
    if os.path.exists(logs_dir):
        for filename in os.listdir(logs_dir):
            file_path = os.path.join(logs_dir, filename)
            if os.path.isfile(file_path):
                # Check if file is older than 1 hour
                if os.path.getmtime(file_path) < one_hour_ago:
                    try:
                        os.remove(file_path)
                        logger.info(f"Deleted old log: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting {file_path}: {str(e)}")

def combine_pdfs(request):
    context = {}

    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Check if we need to delete a previously processed file
    if request.GET.get('delete_file'):
        file_to_delete = request.GET.get('delete_file')
        # Validate the filename to prevent directory traversal attacks
        if os.path.basename(file_to_delete) == file_to_delete and not file_to_delete.startswith('.'):
            try:
                # Delete the ZIP file
                zip_path = os.path.join(settings.MEDIA_ROOT, 'pdf_combinations', file_to_delete)
                if os.path.exists(zip_path) and os.path.isfile(zip_path):
                    os.remove(zip_path)

                # Also delete the corresponding log file
                log_name = file_to_delete.replace('combined_pdfs_', 'pdf_combination_')
                log_name = log_name.replace('.zip', '.log')
                log_path = os.path.join(settings.MEDIA_ROOT, 'pdf_combination_logs', log_name)
                if os.path.exists(log_path) and os.path.isfile(log_path):
                    os.remove(log_path)

                context['deleted'] = True
            except Exception as e:
                logger.error(f"Error deleting file {file_to_delete}: {str(e)}")

    if request.method == 'POST':
        start_time = time.time()

        # Get the uploaded files
        cover_pdf = request.FILES.get('cover_pdf')
        pdfs_zip = request.FILES.get('pdfs_zip')

        if not cover_pdf:
            context['error'] = "No cover PDF uploaded"
            return render(request, 'admin/combine_pdfs.html', context)

        if not pdfs_zip:
            context['error'] = "No ZIP file uploaded"
            return render(request, 'admin/combine_pdfs.html', context)

        # Create temp directories
        temp_dir = tempfile.mkdtemp()
        cover_path = os.path.join(temp_dir, 'cover.pdf')
        extract_dir = os.path.join(temp_dir, 'pdfs')
        output_dir = os.path.join(temp_dir, 'combined')
        os.makedirs(extract_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)

        # Create log file
        log_path = os.path.join(settings.MEDIA_ROOT, 'pdf_combination_logs')
        os.makedirs(log_path, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(log_path, f'pdf_combination_{timestamp}.log')

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        try:
            # Save cover PDF
            with open(cover_path, 'wb') as f:
                for chunk in cover_pdf.chunks():
                    f.write(chunk)

            logger.info(f"Saved cover PDF: {cover_path}")

            # Extract ZIP
            with zipfile.ZipFile(pdfs_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # Process PDFs
            pdf_files = [f for f in os.listdir(extract_dir) if f.lower().endswith('.pdf')]

            if not pdf_files:
                logger.error("No PDF files found in the ZIP")
                context['error'] = "No PDF files found in the ZIP"
                return render(request, 'admin/combine_pdfs.html', context)

            logger.info(f"Found {len(pdf_files)} PDF files to process")

            # Import PyPDF2 for PDF manipulation
            try:
                from PyPDF2 import PdfMerger
            except ImportError:
                logger.error("PyPDF2 library not installed. Please install it with: pip install PyPDF2")
                context['error'] = "PyPDF2 library not installed. Please contact the administrator."
                return render(request, 'admin/combine_pdfs.html', context)

            # Combine each PDF with the cover
            for pdf_file in pdf_files:
                pdf_path = os.path.join(extract_dir, pdf_file)
                output_path = os.path.join(output_dir, pdf_file)

                logger.info(f"Combining cover with {pdf_file}")

                try:
                    merger = PdfMerger()

                    # Add cover PDF
                    merger.append(cover_path)

                    # Add content PDF
                    merger.append(pdf_path)

                    # Write to output file
                    with open(output_path, 'wb') as f:
                        merger.write(f)

                    merger.close()
                    logger.info(f"Created combined PDF: {output_path}")

                except Exception as e:
                    logger.error(f"Error combining {pdf_file}: {str(e)}")

            # Create output ZIP
            output_zip_name = f'combined_pdfs_{timestamp}.zip'
            output_zip_path = os.path.join(settings.MEDIA_ROOT, 'pdf_combinations', output_zip_name)
            os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)

            with zipfile.ZipFile(output_zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, output_dir)
                        zipf.write(file_path, arcname)

            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            elapsed_time_str = f"{elapsed_time:.2f} seconds"

            # Set context for template
            context['processed'] = True
            context['elapsed_time'] = elapsed_time_str
            context['zip_path'] = f'/media/pdf_combinations/{output_zip_name}'
            context['log_path'] = f'/media/pdf_combination_logs/pdf_combination_{timestamp}.log'
            context['file_name'] = output_zip_name  # Store filename for deletion
            context['pdf_count'] = len(pdf_files)

            logger.info(f"Processing complete. Time taken: {elapsed_time_str}")

        except Exception as e:
            logger.error(f"Error processing files: {str(e)}")
            context['error'] = f"Error processing files: {str(e)}"

        finally:
            # Clean up temp files
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.error(f"Error cleaning up temp files: {str(e)}")

            # Remove file handler
            logger.removeHandler(file_handler)

    # Clean up old files (older than 1 hour)
    try:
        cleanup_pdf_combination_files()
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")

    return render(request, 'admin/combine_pdfs.html', context)

def cleanup_pdf_combination_files():
    """Clean up PDF combination files older than 1 hour"""
    now = time.time()
    one_hour_ago = now - 3600  # 1 hour in seconds

    # Clean up PDF combinations
    combinations_dir = os.path.join(settings.MEDIA_ROOT, 'pdf_combinations')
    if os.path.exists(combinations_dir):
        for filename in os.listdir(combinations_dir):
            file_path = os.path.join(combinations_dir, filename)
            if os.path.isfile(file_path):
                # Check if file is older than 1 hour
                if os.path.getmtime(file_path) < one_hour_ago:
                    try:
                        os.remove(file_path)
                        logger.info(f"Deleted old file: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting {file_path}: {str(e)}")

    # Clean up logs
    logs_dir = os.path.join(settings.MEDIA_ROOT, 'pdf_combination_logs')
    if os.path.exists(logs_dir):
        for filename in os.listdir(logs_dir):
            file_path = os.path.join(logs_dir, filename)
            if os.path.isfile(file_path):
                # Check if file is older than 1 hour
                if os.path.getmtime(file_path) < one_hour_ago:
                    try:
                        os.remove(file_path)
                        logger.info(f"Deleted old log: {file_path}")
                    except Exception as e:
                        logger.error(f"Error deleting {file_path}: {str(e)}")

def manufacturer_edit(request, pk):
    m = get_object_or_404(Manufacturer, pk=pk)

    if request.method == "POST":
        # 1) name
        m.name = request.POST.get("name", m.name)

        # 2) status checkbox (will only appear in POST if checked)
        m.status = "status" in request.POST

        # 3) optional new logo upload?
        upload = request.FILES.get("logo")
        if upload:
            # rename original_filename_timestamp.ext
            base, ext = os.path.splitext(upload.name)
            ts = timezone.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{base}_{ts}{ext.lower()}"

            # write into MEDIA_ROOT/logos/
            logos_dir = os.path.join(settings.MEDIA_ROOT, "logos")
            os.makedirs(logos_dir, exist_ok=True)
            full_path = os.path.join(logos_dir, new_filename)
            with open(full_path, "wb+") as out:
                for chunk in upload.chunks():
                    out.write(chunk)

            # point the ImageField at the new file
            m.logo = f"logos/{new_filename}"

        # 4) save it all
        m.save()
        return redirect("logo_management")   # or wherever your listing lives

    # GET: show the form
    return render(request, "core/manufacturer_edit.html", {
        "manufacturer": m,
    })


def logo_uploaded(request):
    if request.method == 'POST':
        name = request.POST.get('manufacturer_name')
        upload = request.FILES.get('manufacturer_logo')
        if name and upload:
            # split original filename and extension
            base, ext = os.path.splitext(upload.name)
            # make a timestamp string, e.g. "20250505_131523"
            ts = timezone.now().strftime("%Y%m%d_%H%M%S")
            # build new filename: originalname_timestamp.ext
            new_filename = f"{base}_{ts}{ext.lower()}"

            # ensure the target folder exists under MEDIA_ROOT
            logos_dir = os.path.join(settings.MEDIA_ROOT, 'logo')
            os.makedirs(logos_dir, exist_ok=True)

            # write the file to disk
            dest_path = os.path.join(logos_dir, new_filename)
            with open(dest_path, 'wb+') as out:
                for chunk in upload.chunks():
                    out.write(chunk)

            # save to your model; path is relative to MEDIA_ROOT
            m = Manufacturer(name=name)
            m.logo = f"logo/{new_filename}"
            m.save()

            return redirect('admin:index')

    # on GET or invalid POST, re-render
    logos = Manufacturer.objects.all()
    return render(request, 'core/logo_management.html', {
        'logos': logos
    })


def logo_management(request):
    manufacturers = Manufacturer.objects.all()

    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")
    return render(request, "admin/logo_management.html", {
        "manufacturers": manufacturers
    })


def shop_image_generation(request):
    manufacturers = Manufacturer.objects.all()
    if not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to access this page.")
    return render(request, 'admin/shop_image_generation.html', {
        "manufacturers": manufacturers,
        # …any other context…
    })


def sample_processing(request):
    # fetch and validate the uploaded sample
    sample = request.FILES.get("sample_prod_img")
    if not sample:
        # no file → back to form
        return redirect("shop_image_generation")

    # safe int parser for your config
    def gi(name, default):
        try:
            return int(request.POST.get(name, default))
        except (TypeError, ValueError):
            return default

    cfg = {
        "canvas_width":       max(1, gi("canvas_width", 1000)),
        "canvas_height":      max(1, gi("canvas_height", 1000)),
        "logo_top_margin":    max(1, gi("logo_top_margin", 50)),
        "logo_right_margin":  max(1, gi("logo_right_margin", 50)),
        "logo_max_width":     max(1, gi("logo_max_width", 200)),
        "product_left_margin":max(1, gi("product_left_margin", 50)),
        "product_bottom_margin":max(1, gi("product_bottom_margin", 50)),
        "product_max_height": max(1, gi("product_max_height", 500)),
    }

    # timestamp & build a safe filename
    orig_name, ext = os.path.splitext(sample.name)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{orig_name}-{ts}{ext}"
    samples_dir = os.path.join(settings.MEDIA_ROOT, "samples")
    os.makedirs(samples_dir, exist_ok=True)

    # save original sample
    sample_path_rel = f"samples/{filename}"
    sample_path_abs = default_storage.save(sample_path_rel, sample)

    # figure out logo path (fallback to 1x1.png if missing)
    manu = request.POST.get("manufacturer_dropdown")
    if not manu:
        return HttpResponseForbidden("Manufacturer must be selected.")
    try:
        m = Manufacturer.objects.get(name=manu)
        logo_rel = str(m.logo)
    except Manufacturer.DoesNotExist:
        logo_rel = "1x1.png"
    logo_abs = os.path.join(settings.MEDIA_ROOT, logo_rel)
    if not os.path.isfile(logo_abs):
        logo_abs = os.path.join(settings.MEDIA_ROOT, "1x1.png")

    # merge them
    # load images
    prod = Image.open(os.path.join(settings.MEDIA_ROOT, sample_path_abs)).convert("RGBA")
    logo = Image.open(logo_abs).convert("RGBA")
    canvas = Image.new("RGBA",
                       (cfg["canvas_width"], cfg["canvas_height"]),
                       (255, 255, 255, 0))

    # resize product
    pr = prod.width / prod.height
    ph = min(cfg["product_max_height"],
             cfg["canvas_height"] - cfg["product_bottom_margin"])
    pw = int(ph * pr)
    prod_rs = prod.resize((pw, ph), Image.LANCZOS)

    # resize logo
    lr = logo.height / logo.width
    lw = min(cfg["logo_max_width"],
             cfg["canvas_width"] - cfg["logo_right_margin"])
    lh = int(lw * lr)
    logo_rs = logo.resize((lw, lh), Image.LANCZOS)

    # compute positions
    px = cfg["product_left_margin"]
    py = cfg["canvas_height"] - cfg["product_bottom_margin"] - ph
    lx = cfg["canvas_width"] - cfg["logo_right_margin"] - lw
    ly = cfg["logo_top_margin"]

    # paste and save final
    canvas.paste(prod_rs, (px, py), prod_rs)
    canvas.paste(logo_rs, (lx, ly), logo_rs)
    final_name = f"{orig_name}-{ts}-final.jpg"
    final_rel  = f"samples/{final_name}"
    final_abs  = os.path.join(settings.MEDIA_ROOT, final_rel)
    canvas.convert("RGB").save(final_abs, "JPEG", quality=95)
    manufacturers = Manufacturer.objects.all()
    # return the URL (you could JSON-ify this if you prefer)
    url = settings.MEDIA_URL + final_rel
    return render(
        request,
        'admin/shop_image_generation.html',  # or whatever your original page template is
        {
            'img': url,
            'processed1': True,
            "manufacturers": manufacturers,
        }
    )

def main_processing(request):
    start = time.perf_counter()
    if request.method != 'POST':
        return redirect('shop_image_generation')

    ts = timezone.now().strftime("%Y%m%d_%H%M%S")
    import os
    from django.conf import settings  # make sure Django is configured before running

    # list of sub-folders under MEDIA_ROOT to clean
    folders = [
        'error_logs',
        'processed_imgs',
        'raw_images',
        'samples',
        'spreadsheets',
        'unprocessed_renamed_imgs',
        'zips',
    ]

    for sub in folders:
        dir_path = os.path.join(settings.MEDIA_ROOT, sub)
        if not os.path.isdir(dir_path):
            continue

        # walk the directory tree and delete all files
        for root, dirs, files in os.walk(dir_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    # optional: log errors instead of crashing
                    pass

        # —if you also want to remove any empty sub-directories afterwards:
        for root, dirs, _ in os.walk(dir_path, topdown=False):
            for d in dirs:
                dir_to_remove = os.path.join(root, d)
                try:
                    os.rmdir(dir_to_remove)
                except OSError:
                    # still not empty or permission issue
                    pass

    # helper for safe int parsing:
    def get_int(field, default):
        try:
            return int(request.POST.get(field, default))
        except (TypeError, ValueError):
            return default

    # 1) Build config with defaults instead of zeros:
    cfg = {
        "canvas_width":         get_int("canvas_width", 1000),
        "canvas_height":        get_int("canvas_height", 1000),
        "logo_top_margin":      get_int("logo_top_margin", 50),
        "logo_right_margin":    get_int("logo_right_margin", 50),
        "logo_max_width":       get_int("logo_max_width", 200),
        "product_left_margin":  get_int("product_left_margin", 50),
        "product_bottom_margin":get_int("product_bottom_margin", 50),
        "product_max_height":   get_int("product_max_height", 500),
    }

    # 2) Early‐exit if our canvas is still invalid:
    if cfg["canvas_width"] <= 0 or cfg["canvas_height"] <= 0:
        log_dir = os.path.join(settings.MEDIA_ROOT, "error_logs")
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, f"errors_{ts}.log"), "a") as lf:
            lf.write("ERROR: canvas_width and canvas_height must be > 0\n")
        return redirect('shop_image_generation')
    # 2) Save & convert CSV/XLSX
    csv_file       = request.FILES['mapping_csv']
    csv_dir        = os.path.join(settings.MEDIA_ROOT, "spreadsheets")
    os.makedirs(csv_dir, exist_ok=True)
    fs_csv         = FileSystemStorage(location=csv_dir)
    saved_csv_name = fs_csv.save(csv_file.name, csv_file)
    csv_path       = fs_csv.path(saved_csv_name)

    root, ext      = os.path.splitext(saved_csv_name)
    ext            = ext.lstrip('.').lower()
    if ext != "csv":
        wb = openpyxl.load_workbook(csv_path, data_only=True)
        ws = wb.active
        converted_name = f"{root}_{ts}.csv"
        converted_path = os.path.join(csv_dir, converted_name)
        with open(converted_path, "w", newline="", encoding="utf-8") as out_f:
            writer = csv.writer(out_f)
            for row in ws.iter_rows(values_only=True):
                writer.writerow(row)
        os.remove(csv_path)
    else:
        converted_name = saved_csv_name
        converted_path = csv_path

    # 3) Save & unzip ZIP of product images
    zip_file       = request.FILES['images_zip']
    zip_dir        = os.path.join(settings.MEDIA_ROOT, "raw_images")
    os.makedirs(zip_dir, exist_ok=True)
    fs_zip         = FileSystemStorage(location=zip_dir)

    base, ext2     = os.path.splitext(zip_file.name)
    saved_zip_name = f"{base}_{ts}{ext2}"
    saved_zip_name_withoutzip = f"{base}_{ts}"
    fs_zip.save(saved_zip_name, zip_file)
    abs_zip_path   = fs_zip.path(saved_zip_name)

    extract_dir    = os.path.join(zip_dir, os.path.splitext(saved_zip_name)[0])
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(abs_zip_path, 'r') as zf:
        zf.extractall(extract_dir)

    # 4) Determine raw_base (descend into single folder if present)
    entries = [e for e in os.listdir(extract_dir) if not e.startswith('.')]
    if len(entries) == 1 and os.path.isdir(os.path.join(extract_dir, entries[0])):
        raw_base = os.path.join(extract_dir, entries[0])
    else:
        raw_base = extract_dir
    default_logo_path = os.path.join(settings.MEDIA_ROOT, "1x1.png")  # make sure this file exists
    manu_name = request.POST.get('manufacturer_dropdown', 'no image')

    if manu_name == 'no image':
        logo_path = default_logo_path
    else:
        try:
            m1 = Manufacturer.objects.get(name=manu_name)
            rel = str(m1.logo).lstrip('/')
            logo_path = os.path.join(settings.MEDIA_ROOT, rel)
        except Manufacturer.DoesNotExist:
            logo_path = default_logo_path

    if not os.path.isfile(logo_path):
        # immediate bail with log
        log_dir = os.path.join(settings.MEDIA_ROOT, "error_logs")
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, f"errors_{ts}.log"), "w") as lf:
            lf.write(f"LOGO MISSING: {logo_path}\n")
        return redirect('shop_image_generation')

    # 6) Prepare output dir
    zip_folder = os.path.splitext(saved_zip_name)[0]
    proc_dir   = os.path.join(settings.MEDIA_ROOT, "processed_imgs", zip_folder)
    os.makedirs(proc_dir, exist_ok=True)

    # 7) Read CSV & build tasks
    merge_errors = []
    tasks        = []
    missing      = []
    with open(converted_path, newline="", encoding="utf-8") as fmap:
        reader = csv.DictReader(fmap)
        for row in reader:
            target = row["Target Image Name"].strip()
            source = row["Document Name"].strip()
            if not source:
                continue
            prod_path = os.path.join(raw_base, source)
            if not os.path.isfile(prod_path):
                missing.append(prod_path)
                continue
            name, extn = os.path.splitext(target)
            if not extn:
                extn = os.path.splitext(source)[1] or ".jpg"
            out_filename = f"{name}{extn}"
            out_path     = os.path.join(proc_dir, out_filename)
            tasks.append((prod_path, logo_path, out_path))

    # 8) Write missing‐product log
    log_dir = os.path.join(settings.MEDIA_ROOT, "error_logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file= os.path.join(log_dir, f"errors_{ts}.log")
    with open(log_file, "w", encoding="utf-8") as lf:
        if not missing and not merge_errors:
            lf.write("no error\n")
        else:
            for p in missing:
                lf.write(f"Missing product file: {p}\n")
    # 9) Merge helper collects its own errors
    def merge_images(prod_p, logo_p, out_p, cfg):
        try:
            prod   = Image.open(prod_p).convert("RGBA")
            logo   = Image.open(logo_p).convert("RGBA")
            canvas = Image.new("RGBA", (cfg["canvas_width"], cfg["canvas_height"]), (255,255,255,0))
            # resize product
            pr     = prod.width / prod.height
            ph     = min(cfg["product_max_height"], cfg["canvas_height"] - cfg["product_bottom_margin"])
            pw     = int(ph * pr)
            prod_rs= prod.resize((pw, ph), Image.LANCZOS)
            # resize logo
            lr     = logo.height / logo.width
            lw     = min(cfg["logo_max_width"], cfg["canvas_width"] - cfg["logo_right_margin"])
            lh     = int(lw * lr)
            logo_rs= logo.resize((lw, lh), Image.LANCZOS)
            # positions
            px = cfg["product_left_margin"]
            py = cfg["canvas_height"] - cfg["product_bottom_margin"] - ph
            lx = cfg["canvas_width"] - cfg["logo_right_margin"] - lw
            ly = cfg["logo_top_margin"]
            # paste & save
            canvas.paste(prod_rs, (px, py), prod_rs)
            canvas.paste(logo_rs, (lx, ly), logo_rs)
            canvas.convert("RGB").save(out_p, "JPEG", quality=95)
        except Exception as e:
            msg = f"ERROR merging {prod_p} + {logo_p}: {e}"
            print(msg)
            merge_errors.append(msg)

    # 10) Execute merges
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for prod_p, logo_p, out_p in tasks:
            executor.submit(merge_images, prod_p, logo_p, out_p, cfg)

    # 11) Append merge_errors to the same log
    if merge_errors:
        with open(log_file, "a", encoding="utf-8") as lf:
            lf.write("\n# Merge errors:\n")
            for err in merge_errors:
                lf.write(err + "\n")
    saved_zip_name_to = f"{base}_{ts}"
    zip_to = os.path.join(settings.MEDIA_ROOT, "processed_imgs")
    zip_to1 = os.path.join(settings.MEDIA_ROOT, "zips")
    # base1, ext12 = os.path.splitext(zip_file.name)

    source_folder = f"{zip_to}/{saved_zip_name_to}"
    target_zip = f"{zip_to1}/{saved_zip_name_to}.zip"
    zip_directory(source_folder, target_zip)
    pc=f"/media/zips/{saved_zip_name_to}.zip"

    # print(f"Zipped folder `{source_folder}` → `{target_zip}`")
    logpath = os.path.join(log_dir, f"errors_{ts}.log")
    dictdat={
        'zip': target_zip,
        'log': str(logpath),
    }
    lp=f"/media/error_logs/errors_{ts}.log"
    lzp=f"/media/unprocessed_renamed_imgs/{saved_zip_name_to}.zip"
    # 1. Load your CSV mapping file
    csv_path = os.path.join(settings.MEDIA_ROOT, f"spreadsheets/{converted_name}")
    df = pd.read_csv(csv_path)
    # 2. Parameters
    saved_zip_name = saved_zip_name_withoutzip
    input_dir = os.path.join(settings.MEDIA_ROOT, f"raw_images/{saved_zip_name}/RAW IMAGES")
    output_dir = os.path.join(settings.MEDIA_ROOT, f"unprocessed_renamed_imgs/{saved_zip_name}")

    # 3. Create destination (you'll need write perms here)
    os.makedirs(output_dir, exist_ok=True)



    # … after reading df = pd.read_csv(csv_path) …

    # import os, shutil, pandas as pd

    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        src_raw = row.get('Document Name')
        tgt_raw = row.get('Target Image Name')

        # skip blank or NaN rows
        if pd.isna(src_raw) or pd.isna(tgt_raw):
            continue

        src_name = str(src_raw).strip()
        tgt_base = str(tgt_raw).strip()

        # get ext from source filename (e.g. ".png", ".jpg")
        src_ext = os.path.splitext(src_name)[1] or '.jpg'

        # if target has no extension, append the source ext
        if not os.path.splitext(tgt_base)[1]:
            tgt_name = tgt_base + src_ext
        else:
            tgt_name = tgt_base

        src = os.path.join(input_dir, src_name)
        dst = os.path.join(output_dir, tgt_name)

        if os.path.isfile(src):
            shutil.copy2(src, dst)
        else:
            missing.append(src)

    # 5. Zip the renamed folder
    zip_output = os.path.join(settings.MEDIA_ROOT, f"unprocessed_renamed_imgs/{saved_zip_name}.zip")
    with zipfile.ZipFile(zip_output, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(output_dir):
            for fn in files:
                fp = os.path.join(root, fn)
                # make paths inside zip relative
                arc = os.path.relpath(fp, os.path.dirname(output_dir))
                zf.write(fp, arc)
    elapsed = time.perf_counter() - start
    return render(
        request,
        'admin/shop_image_generation.html',  # or whatever your original page template is
        {
            'zip_path': pc,
            'log_path': lp,
            'normal_path': lzp,
            'elapsed_time': f"{elapsed:.2f}s",
            'processed': True,
        }
    )
    #target_zip
    #logpath