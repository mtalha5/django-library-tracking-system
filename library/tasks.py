from celery import shared_task, group
from django.utils import timezone

from .models import Loan
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass

@shared_task
def check_over_due_loans():
    today_date = timezone.now().date
    due_loans = Loan.objects.select_related("member__user", "book").filter(is_returned=False, due_date__lt=today_date)
    tasks = group([send_overdue_email.si(loan.member.user.username,loan.book.title,loan.member.user.email)for
                   loan in due_loans])
    if tasks:
        tasks.apply_async()

@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,), retry_backoff=True)
def send_overdue_email(member_username,book_title,member_email):
    send_mail(
        subject='Book Loan Overdue',
        message=f'Hello {member_username},\n\nthe loaned book with title "{book_title}".\n is overdue.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[member_email],
        fail_silently=False,
    )
