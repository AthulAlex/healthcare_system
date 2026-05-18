import requests
from .ai_helper import generate_health_report
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import ResidentProfile, VitalSign, LabReport
from stockkeeper.models import Prescription
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import io

def resident_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'resident':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@resident_required
def resident_dashboard(request):
    try:
        profile = ResidentProfile.objects.get(user=request.user)
    except ResidentProfile.DoesNotExist:
        return render(request, 'residents/no_profile.html')

    latest_vital = profile.vitals.order_by('-recorded_at').first()
    recent_labs  = profile.lab_reports.order_by('-uploaded_at')[:5]
    prescriptions = profile.prescriptions.filter(is_active=True)

    # Risk analysis
    risk_level = 'Low'
    risk_reasons = []
    if profile.vitals.filter(is_abnormal=True).exists():
        risk_level = 'High'
        risk_reasons.append('Abnormal vital signs detected')
    if profile.lab_reports.filter(is_critical=True).exists():
        risk_level = 'High'
        risk_reasons.append('Critical lab results found')
    if not risk_reasons:
        risk_reasons.append('All readings are within normal range')

    context = {
        'profile': profile,
        'latest_vital': latest_vital,
        'recent_labs': recent_labs,
        'prescriptions': prescriptions,
        'risk_level': risk_level,
        'risk_reasons': risk_reasons,
    }
    return render(request, 'residents/dashboard.html', context)


@resident_required
def vital_history(request):
    profile = get_object_or_404(ResidentProfile, user=request.user)
    vitals  = profile.vitals.order_by('-recorded_at')
    return render(request, 'residents/vitals.html', {
        'profile': profile,
        'vitals': vitals
    })


@resident_required
def lab_reports(request):
    profile = get_object_or_404(ResidentProfile, user=request.user)
    reports = profile.lab_reports.order_by('-uploaded_at')
    return render(request, 'residents/lab_reports.html', {
        'profile': profile,
        'reports': reports
    })


@resident_required
def export_pdf(request):
    profile       = get_object_or_404(ResidentProfile, user=request.user)
    vitals        = profile.vitals.order_by('-recorded_at')[:10]
    labs          = profile.lab_reports.order_by('-uploaded_at')[:10]
    prescriptions = profile.prescriptions.filter(is_active=True)

    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story  = []

    # Title
    story.append(Paragraph("Medical Report", styles['Title']))
    story.append(Paragraph(f"Old Age Home Healthcare System", styles['Normal']))
    story.append(Spacer(1, 20))

    # Personal Info
    story.append(Paragraph("Personal Details", styles['Heading2']))
    personal_data = [
        ['Full Name', profile.full_name],
        ['Date of Birth', str(profile.date_of_birth)],
        ['Gender', profile.gender],
        ['Blood Group', profile.blood_group],
        ['Admission Date', str(profile.admission_date)],
        ['Emergency Contact', profile.emergency_contact],
    ]
    t = Table(personal_data, colWidths=[150, 350])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.lightblue),
        ('FONTNAME',   (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',   (0,0), (-1,-1), 10),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING',    (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    # Risk Summary
    risk_level = 'Low'
    if profile.vitals.filter(is_abnormal=True).exists():
        risk_level = 'High'
    if profile.lab_reports.filter(is_critical=True).exists():
        risk_level = 'High'
    story.append(Paragraph("AI Risk Summary", styles['Heading2']))
    story.append(Paragraph(f"Overall Risk Level: {risk_level}", styles['Normal']))
    story.append(Spacer(1, 16))

    # Vitals
    story.append(Paragraph("Recent Vital Signs", styles['Heading2']))
    if vitals:
        vital_data = [['Date', 'BP', 'Pulse', 'Oxygen', 'Temp', 'Blood Sugar', 'Status']]
        for v in vitals:
            vital_data.append([
                v.recorded_at.strftime('%d %b %Y'),
                v.blood_pressure,
                f"{v.pulse_rate} bpm",
                f"{v.oxygen_level}%",
                f"{v.temperature}°C",
                f"{v.blood_sugar} mg/dL",
                'Abnormal' if v.is_abnormal else 'Normal'
            ])
        t2 = Table(vital_data, colWidths=[80, 60, 55, 55, 50, 75, 65])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
            ('FONTNAME',   (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE',   (0,0), (-1,-1), 8),
            ('GRID',       (0,0), (-1,-1), 0.5, colors.grey),
            ('PADDING',    (0,0), (-1,-1), 5),
        ]))
        story.append(t2)
    else:
        story.append(Paragraph("No vitals recorded.", styles['Normal']))
    story.append(Spacer(1, 16))

    # Lab Reports
    story.append(Paragraph("Lab Reports", styles['Heading2']))
    if labs:
        lab_data = [['Test Name', 'Result', 'Unit', 'Normal Range', 'Status']]
        for lab in labs:
            lab_data.append([
                lab.test_name,
                str(lab.result_value),
                lab.unit,
                lab.normal_range,
                'Critical' if lab.is_critical else 'Normal'
            ])
        t3 = Table(lab_data, colWidths=[130, 70, 60, 100, 80])
        t3.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
            ('FONTNAME',   (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE',   (0,0), (-1,-1), 8),
            ('GRID',       (0,0), (-1,-1), 0.5, colors.grey),
            ('PADDING',    (0,0), (-1,-1), 5),
        ]))
        story.append(t3)
    else:
        story.append(Paragraph("No lab reports.", styles['Normal']))
    story.append(Spacer(1, 16))

    # Prescriptions
    story.append(Paragraph("Active Prescriptions", styles['Heading2']))
    if prescriptions:
        presc_data = [['Medicine', 'Dosage', 'Frequency', 'Prescribed By']]
        for p in prescriptions:
            presc_data.append([
                p.medicine.name,
                p.dosage,
                p.frequency,
                p.prescribed_by
            ])
        t4 = Table(presc_data, colWidths=[130, 100, 120, 130])
        t4.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a73e8')),
            ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
            ('FONTNAME',   (0,0), (-1,-1), 'Helvetica'),
            ('FONTSIZE',   (0,0), (-1,-1), 8),
            ('GRID',       (0,0), (-1,-1), 0.5, colors.grey),
            ('PADDING',    (0,0), (-1,-1), 5),
        ]))
        story.append(t4)
    else:
        story.append(Paragraph("No active prescriptions.", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{profile.full_name}_report.pdf"'
    return response


@resident_required
def ai_health_report(request):
    from residents.ai_helper import generate_health_report
    from .models import AIHealthReport

    profile     = get_object_or_404(ResidentProfile, user=request.user)
    vitals      = list(profile.vitals.order_by('-recorded_at')[:5])
    lab_reports = list(profile.lab_reports.order_by('-uploaded_at')[:5])

    report = None
    error  = None

    if request.method == 'POST':
        try:
            result = generate_health_report(profile, vitals, lab_reports)

            # Save to database
            report = AIHealthReport.objects.create(
                resident   = profile,
                risk_score = result.get('risk_score', 0),
                risk_level = result.get('risk_level', 'Low'),
                summary    = result.get('summary', ''),
                factors    = result.get('factors', ''),
            )
            messages.success(request, 'AI Health Report generated successfully!')

        except requests.exceptions.Timeout:
            error = "Request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            error = "Could not connect to AI service."
        except Exception as e:
            error = f"Something went wrong: {str(e)}"

    # Always get latest report
    latest_report = profile.ai_reports.order_by('-generated_at').first()

    return render(request, 'residents/ai_report.html', {
        'profile':       profile,
        'latest_report': latest_report,
        'error':         error,
    })