
import pandas as pd
from django.shortcuts import render
from django.core.mail import send_mail
from .models import UploadedData
from .forms import UploadFileForm
from io import StringIO

def handle_file_upload(file):
    file_name = file.name
    if file_name.endswith('.csv'):
        data = file.read().decode('utf-8')
        df = pd.read_csv(StringIO(data))
    elif file_name.endswith('.xls') or file_name.endswith('.xlsx'):
        df = pd.read_excel(file)
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or Excel file.")

    required_columns = ['Date', 'ACCNO', 'Cust State', 'Cust Pin', 'DPD']
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")

    try:
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)  
    except ValueError:
        raise ValueError("Invalid date format. Ensure dates are consistent and try again.")

    for _, row in df.iterrows():
        UploadedData.objects.create(
            date=row['Date'].date(), 
            acc_no=row['ACCNO'],
            cust_state=row['Cust State'],
            cust_pin=row['Cust Pin'],
            dpd=row['DPD'],
        )
    summary = df.groupby(['Cust State', 'DPD']).size().reset_index(name='Count')
    return summary

def file_upload(request):
    form = UploadFileForm()

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            summary = handle_file_upload(request.FILES['file'])
            send_summary_email(summary)
            return render(request, 'file_upload/success.html', {'summary': summary.to_html(index=False)})
        else:
            form = UploadFileForm()
    return render(request, 'file_upload/upload_form.html', {'form': form})

def send_summary_email(summary):
    body = summary.to_string(index=False)
    send_mail(
        'Summary Report',
        body,
        'file.uploadprojectz@gmail.com',
        ['tech@themedius.ai', 'hr@themedius.ai'],
        fail_silently=False,
    )
