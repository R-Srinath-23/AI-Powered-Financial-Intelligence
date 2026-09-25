import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Transaction

# Our FastAPI backend URL
API_URL = "http://127.0.0.1:8000"

def upload_view(request):
    if request.method == "POST":
        csv_file = request.FILES.get('csv_file')
        
        if not csv_file:
            messages.error(request, "Please select a file to upload.")
            return redirect('upload')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "File must be a CSV.")
            return redirect('upload')

        # Send the file to our FastAPI backend
        files = {'file': (csv_file.name, csv_file.read(), 'text/csv')}
        try:
            response = requests.post(f"{API_URL}/api/upload", files=files)
            if response.status_code == 200:
                messages.success(request, response.json().get('message', 'Success!'))
            else:
                messages.error(request, "Error processing file.")
        except Exception as e:
            messages.error(request, f"Backend error: {str(e)}")
            
        return redirect('upload')

    return render(request, 'dashboard/upload.html')

def transactions_view(request):
    if request.method == "POST":
        if "run_ai" in request.POST:
            try:
                response = requests.post(f"{API_URL}/api/categorize")
                if response.status_code == 200:
                    messages.success(request, response.json().get('message', 'AI Categorization complete!'))
                else:
                    messages.error(request, "Failed to run AI categorization.")
            except Exception as e:
                messages.error(request, f"Backend error: {str(e)}")
            return redirect('transactions')
            
        elif "update_category" in request.POST:
            txn_id = request.POST.get('txn_id')
            new_category = request.POST.get('new_category')
            try:
                txn = Transaction.objects.get(transaction_id=txn_id)
                txn.ai_category = new_category
                txn.needs_review = False  # cleared once user reviews
                txn.save()
                messages.success(request, f"Updated {txn_id} to '{new_category}' successfully!")
            except Transaction.DoesNotExist:
                messages.error(request, "Transaction not found.")
            return redirect('transactions')

    transactions_list = Transaction.objects.all().order_by('date')
    return render(request, 'dashboard/transactions.html', {'transactions': transactions_list})


def pl_view(request):
    try:
        response = requests.get(f"{API_URL}/api/pl")
        pl_data = response.json() if response.status_code == 200 else {}
    except Exception as e:
        messages.error(request, f"Failed to load P&L: {str(e)}")
        pl_data = {}
        
    return render(request, 'dashboard/pl.html', {'pl': pl_data})

def review_queue_view(request):
    if request.method == "POST":
        txn_id = request.POST.get('txn_id')
        action = request.POST.get('action') # 'approve' or 'update'
        
        try:
            txn = Transaction.objects.get(transaction_id=txn_id)
            if action == 'approve':
                txn.needs_review = False
                txn.save()
                messages.success(request, f"Approved {txn_id} as {txn.ai_category}!")
            elif action == 'update':
                new_cat = request.POST.get('new_category')
                txn.ai_category = new_cat
                txn.needs_review = False
                txn.save()
                messages.success(request, f"Updated {txn_id} to {new_cat} and marked as reviewed!")
        except Transaction.DoesNotExist:
            messages.error(request, "Transaction not found.")
            
        return redirect('review_queue')

    # Only fetch transactions that need review
    flagged_txns = Transaction.objects.filter(needs_review=True).order_by('date')
    return render(request, 'dashboard/review_queue.html', {'transactions': flagged_txns})

def variance_view(request):
    try:
        response = requests.get(f"{API_URL}/api/variance")
        variance_data = response.json() if response.status_code == 200 else []
    except Exception as e:
        messages.error(request, f"Failed to load variance report: {str(e)}")
        variance_data = []

    return render(request, 'dashboard/variance.html', {'comparisons': variance_data})

def chat_view(request):
    chat_history = request.session.get('chat_history', [])

    if request.method == "POST" and "clear_chat" in request.POST:
        request.session['chat_history'] = []
        return redirect('chat')

    return render(request, 'dashboard/chat.html', {'chat_history': chat_history})

@require_POST
def chat_message_view(request):
    """AJAX endpoint — returns JSON, no page reload."""
    import json
    body = json.loads(request.body)
    user_message = body.get('message', '').strip()
    if not user_message:
        return JsonResponse({'reply': ''}, status=400)

    chat_history = request.session.get('chat_history', [])
    chat_history.append({'sender': 'user', 'text': user_message})

    try:
        res = requests.post(f"{API_URL}/api/chat", json={'message': user_message}, timeout=90)
        ai_reply = res.json().get('reply', 'No response received.') if res.status_code == 200 else "Error communicating with AI Analyst."
    except Exception as e:
        ai_reply = f"Sorry, I encountered an error: {str(e)}"

    chat_history.append({'sender': 'ai', 'text': ai_reply})
    request.session['chat_history'] = chat_history
    return JsonResponse({'reply': ai_reply})
